import imapclient
import imapclient.exceptions
import pyzmail
import json
import smtplib
import sys
import base64
from fastapi import HTTPException

from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pydantic import BaseModel
from mailbox_models import Inbox, Email, EmailQuery, Attachment
from db_models import DBMailbox, DBEmail, DBAttachment

# ----------------------------------------
# Funkcje pomocnicze do logowania i wczytywania konfiguracji
# ----------------------------------------

def _load_config() -> dict:
    """
    Wczytuje plik konfiguracyjny z danymi logowania.
    """

    if getattr(sys, "frozen", False):
        # Jeśli aplikacja jest uruchomiona jako skompilowany plik .exe
        config_path = Path(sys.executable).resolve().parent / "config.json"
        # - sys.executable wskazuje na ścieżkę do pliku wykonywalnego (.exe) po kompilacji,
        # - .resolve().parent pobiera folder, w którym ten plik .exe się znajduje,
        # - / "config.json" dodaje nazwę pliku konfiguracyjnego do tej ścieżki.
    else:
        # Jeśli aplikacja jest uruchomiona jako skrypt Pythona
        config_path = Path(__file__).resolve().parent / "dist/config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Brak pliku konfiguracyjnego: {config_path}")

    with config_path.open() as f:
        return json.load(f)

def login_to_imap(config):
    """
    Funkcja do logowania się do serwera IMAP.
    Zwraca obiekt IMAPClient po zalogowaniu.
    """

    host = config.get("host_imap")
    email = config.get("email")
    password = config.get("password")

    # Połączenie i logowanie
    mail = imapclient.IMAPClient(host, ssl=True)
    mail.login(email, password)

    return mail

def login_to_smtp(config):
    """
    Funkcja do logowania się do serwera SMTP.
    Zwraca obiekt SMTP po zalogowaniu.
    """

    host = config.get("host_smtp")
    email = config.get("email")
    password = config.get("password")

    # Połączenie i logowanie
    smtp = smtplib.SMTP_SSL(host, config.get("smtp_port", 465))
    smtp.login(email, password)

    return smtp

def fetch_email(mail, inbox, uid):
    mail.select_folder(inbox, readonly=True)
    raw_message = mail.fetch(
        [uid], ["BODY[]", "FLAGS"]
    )  # fetch zwraca słownik, gdzie kluczem jest UID wiadomości, a wartością jest słownik z danymi wiadomości
    message = pyzmail.PyzMessage.factory(
        raw_message[uid][b"BODY[]"]
    )  # extractujemy z tego słownika treść wiadomości w formacie MIME.
    flags = raw_message[uid][
        b"FLAGS"
    ]  # Pobieramy flagi wiadomości (np. czy jest przeczytana, oznaczona jako spam itp.) // DO OPROGRAMOWANIA!!!!

    subject = message.get_subject()  # Pobieramy temat wiadomości
    from_ = message.get_addresses(
        "from"
    )  # Pobieramy dane nadawcy w postaci krotki (nazwa, adres e-mail)
    date = message.get_decoded_header("date")  # Pobieramy datę wiadomości

    if message.html_part:
        body = message.html_part.get_payload().decode(
            message.html_part.charset
        )  # Dekodujemy treść HTML wiadomości
        body_type = "html"  # Ustawiamy typ treści na HTML
    elif message.text_part:
        body = message.text_part.get_payload().decode(
            message.text_part.charset
        )  # Dekodujemy treść tekstową wiadomości
        body_type = "text"  # Ustawiamy typ treści na tekst
    else:
        body = ""  # Jeśli nie ma części HTML ani tekstowej, ustawiamy pusty ciąg
        body_type = "text"  # Domyślny typ treści to tekst

    attachments = []  # Lista do przechowywania załączników

    for part in message.mailparts:
        if (
            part.filename
        ):  # Sprawdzamy, czy część wiadomości ma nazwę pliku (czyli jest załącznikiem)
            attachment = part.get_payload()  # Pobieramy zawartość załącznika
            filename = (
                part.filename or "unknown"
            )  # Ustawiamy nazwę pliku załącznika, jeśli nie jest podana, to "unknown"
            content = base64.b64encode(attachment).decode(
                "utf-8"
            )  # Kodujemy zawartość załącznika w base64 i dekodujemy na UTF-8
            file_type = (
                part.content_type or "application/octet-stream"
            )  # Pobieramy typ zawartości załącznika, jeśli nie jest podany, to ustawiamy na "application/octet-stream"
            size = len(attachment)  # Pobieramy rozmiar załącznika w bajtach
            attachments.append(
                {
                    "filename": filename,
                    "file_type": file_type,
                    "size": size,
                    "content": content,
                }
            )  # Tworzymy obiekt załacznika i dodajemy go do listy

        email = {
            "uid": uid,  # Unikalny identyfikator wiadomości
            "subject": subject,  # Temat wiadomości
            "sender": (
                from_[0][1] if from_ else "Nieznany nadawca"
            ),  # Adres e-mail nadawcy
            "sender_name": from_[0][0] if from_ else "Nieznany",
            "date": date,  # Data wiadomości
            "flags": flags,  # Flagi wiadomości (np. czy jest przeczytana, oznaczona jako spam itp.)
            "body": body,  # Treść wiadomości
            "body_type": body_type,  # Typ treści wiadomości (HTML lub tekst)
            "attachments": attachments,  # Lista załączników
            "inbox": inbox,  # Nazwa skrzynki odbiorczej, z której pochodzi wiadomość
        }

    return email

# ----------------------------------------
# Funkcje do ekspotu z modułu
# ----------------------------------------

def get_uids(inbox):
    config = _load_config()
    mail = login_to_imap(config)
    mail.select_folder(inbox, readonly=True)
    return mail.search(['ALL'])

def get_inboxes():
    """
    Funkcja do pobierania listy skrzynek odbiorczych z serwera IMAP.
    """
    config = _load_config()  # Wczytanie konfiguracji z pliku config.json
    mail = login_to_imap(config)  # Logowanie do serwera IMAP
    inboxes_list = [
        name for _, _, name in mail.list_folders()
    ]  # Pobieranie listy skrzynek odbiorczych
    inboxes = []
    for inbox in inboxes_list:
        mail.select_folder(inbox, readonly=True)
        status = mail.folder_status(
            inbox, ["UNSEEN", "MESSAGES", "UIDVALIDITY"]
        )  # Pobieranie statusu skrzynki odbiorczej
        unread_count = status[b"UNSEEN"]  # Liczba nieprzeczytanych wiadomości
        total_count = status[b"MESSAGES"]  # Łączna liczba wiadomości
        uidvalidity = status[b"UIDVALIDITY"]  # UIDVALIDITY skrzynki odbiorczej
        # Dodajemy skrzynkę odbiorczą do listy z informacjami o liczbie wiadomości
        inboxes.append(
            {
                "name": inbox,
                "unread_count": unread_count,
                "total_count": total_count,
                "uidvalidity": uidvalidity,
            }
        )

    mail.logout()  # Zamykanie połączenia z serwerem IMAP
    return inboxes

def fetch_email_data(inbox, uid):
    try:
        config = _load_config()
        mail = login_to_imap(config)
        mail.select_folder(inbox, readonly=True)
        # Pobieramy wiadomość o podanym UID
        email_data = fetch_email(mail, inbox, uid)
        email = Email(
            uid=email_data["uid"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            sender_name=email_data["sender_name"],
            date=email_data["date"],
            body=email_data["body"],
            body_type=email_data["body_type"],
            attachments=[
                Attachment(**att) for att in email_data["attachments"]
            ],  # Konwersja załączników do obiektów Attachment
        )  # Tworzymy obiekt Email z pobranej wiadomości
        
        mail.logout()
        return email
    
    # Obsługa wyjątków
    except imapclient.exceptions.LoginError as e:
        raise HTTPException(
            status_code=401, detail=f"Błąd logowania do serwera IMAP: {str(e)}"
        )  # Błąd logowania do serwera IMAP
    except imapclient.exceptions.IMAPClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Błąd połączenia z serwerem IMAP: {str(e)}"
        )  # Błąd połączenia z serwerem IMAP
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Nieznany błąd: {str(e)}"
        )  # Inne nieoczekiwane błędy
    finally:
        mail.logout()  # Zamykanie połączenia z serwerem IMAP, nawet jeśli wystąpił błąd

def send_email(email: Email):
    """
    Funkcja do wysyłania e-maili przez serwer SMTP.
    """
    try:
        config = _load_config()  # Wczytanie konfiguracji z pliku config.json
        smtp = login_to_smtp(config)  # Logowanie do serwera SMTP

        msg = MIMEMultipart()  # Tworzenie wiadomości MIME
        msg["Subject"] = email.subject
        msg["To"] = (
            f"{email.to_name} <{email.to_mail}>" if email.to_name else email.to_mail
        )  # Ustawianie odbiorcy wiadomości
        msg.attach(
            MIMEText(email.body, email.body_type)
        )  # Dodawanie treści wiadomości (HTML lub tekst) do obiektu MIME

        if email.attachments:
            for attachment in email.attachments:
                decoded_content = base64.b64decode(
                    attachment.content
                )  # Dekodowanie zawartości załącznika z base64 do postaci binarnej
                part = MIMEApplication(
                    decoded_content, Name=attachment.filename
                )  # Tworzenie części MIME dla załącznika
                part["Content-Disposition"] = (
                    f'attachment; filename="{attachment.filename}"'  # Ustawianie nagłówka Content-Disposition, aby wskazać, że jest to załącznik
                )
                msg.attach(part)  # Dodawanie załącznika do obiektu drzewa MIME

        smtp.sendmail(
            email.from_mail, [email.to_mail], msg.as_string()
        )  # Wysyłka wiadomości
        smtp.quit()  # Zamykanie połączenia z serwerem SMTP
        return {"status": "ok"}  # Zwracamy status powodzenia

    except smtplib.SMTPAuthenticationError as e:
        raise HTTPException(
            status_code=401, detail=f"Błąd uwierzytelniania SMTP: {str(e)}"
        )  # Błąd uwierzytelniania SMTP
    except smtplib.SMTPRecipientsRefused as e:
        raise HTTPException(
            status_code=422, detail=f"Odrzucono adres odbiorcy: {str(e)}"
        )  # Odrzucono adres odbiorcy
    except smtplib.SMTPSenderRefused as e:
        raise HTTPException(
            status_code=400, detail=f"Odrzucono adres nadawcy: {str(e)}"
        )  # Odrzucono adres nadawcy
    except smtplib.SMTPConnectError as e:
        raise HTTPException(
            status_code=503, detail=f"Nie można połączyć się z serwerem SMTP: {str(e)}"
        )  # Błąd połączenia z serwerem SMTP
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Nieznany błąd: {str(e)}"
        )  # Inne nieoczekiwane błędy
    finally:
        smtp.quit()  # Zamykanie połączenia z serwerem SMTP, nawet jeśli wystąpił błąd

def fetch_emails_metadata(inbox, uids_list):
    try:
        config = _load_config()  # Wczytanie konfiguracji z pliku config.json
        mail = login_to_imap(config)  # Logowanie do serwera IMAP
        mail.select_folder(inbox, readonly=True)
        
        emails = []
        attachements = []
        
        for uid in uids_list:     
            email_data = fetch_email(mail, inbox, uid)
            emails.append(DBEmail(
                uid=email_data["uid"],
                sender=email_data["sender"],
                sender_name=email_data["sender_name"],
                date=email_data["date"],
                subject=email_data["subject"],            
                content_preview=email_data["body"][:20],  # Pobieramy pierwsze 20 znaków jako podgląd treści
                mailbox_name=email_data['inbox']
            ))
            
            attachements.append(DBAttachment(
                email_uid=email_data["uid"],  # Ustawiamy UID wiadomości jako klucz obcy
                filename=email_data["attachments"][0]["filename"] if email_data["attachments"] else None,
                content_type=email_data["attachments"][0]["file_type"] if email_data["attachments"] else None,
                size=email_data["attachments"][0]["size"] if email_data["attachments"] else 0,
            ))
        
        mail.logout()  # Zamykanie połączenia z serwerem IMAP
        return emails, attachements  # Zwracamy obiekt DBEmail i DBAttachment
        
    # Obsługa wyjątków
    except imapclient.exceptions.LoginError as e:
        raise HTTPException(
            status_code=401, detail=f"Błąd logowania do serwera IMAP: {str(e)}"
        )  # Błąd logowania do serwera IMAP
    except imapclient.exceptions.IMAPClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Błąd połączenia z serwerem IMAP: {str(e)}"
        )  # Błąd połączenia z serwerem IMAP
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Nieznany błąd: {str(e)}"
        )  # Inne nieoczekiwane błędy
    finally:
        mail.logout()  # Zamykanie połączenia z serwerem IMAP, nawet jeśli wystąpił błąd

##########################################################

def fetch_filtred_emails(inbox="INBOX", filtr=["ALL"]):
    """
    Funkcja do pobierania filtrowanych e-maili z serwera IMAP.
    """

    try:
        # Wczytujemy konfigurację z pliku config.json
        config = _load_config()
        # Logujemy się do serwera IMAP
        mail = login_to_imap(config)
        # Wybieramy skrzynkę odbiorczą
        mail.select_folder(
            inbox, readonly=True
        )  # readonly=True oznacza, że nie będziemy modyfikować skrzynki odbiorczej (np. oznaczać wiadomości jako przeczytane przy pobieraniu).
        # Szukamy maili z użyciem określonego filtra
        uids = mail.search(['ALL'])[]  # ["ALL'] lub ['UNSEEN'], ['FROM', 'adres@kogoś.pl'], itd.
        # Przygotowanie listy do przechowywania e-maili
        mails = []
        # Konwertujemy pobrane przez IMAP obiekty MIME na Email zdefiniowane w base_models.py
        for uid in uids:
            email = fetch_email_data(mail, uid)
            mails.append(email)
        # Zamykanie połączenia z serwerem IMAP
        mail.logout()  # Zamykanie połączenia z serwerem IMAP, nawet jeśli wystąpił błąd
        # Zwracamy listę e-maili
        return mails

    # Obsługa wyjątków
    except imapclient.exceptions.LoginError as e:
        raise HTTPException(
            status_code=401, detail=f"Błąd logowania do serwera IMAP: {str(e)}"
        )  # Błąd logowania do serwera IMAP
    except imapclient.exceptions.IMAPClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Błąd połączenia z serwerem IMAP: {str(e)}"
        )  # Błąd połączenia z serwerem IMAP
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Nieznany błąd: {str(e)}"
        )  # Inne nieoczekiwane błędy
    finally:
        mail.logout()  # Zamykanie połączenia z serwerem IMAP, nawet jeśli wystąpił błąd
