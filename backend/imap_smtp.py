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
from base_models import Email, EmailQuery

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


# ----------------------------------------
# Funkcje do ekspotu z modułu
# ----------------------------------------

def get_inbox_list():
    """ 
    Funkcja do pobierania listy skrzynek odbiorczych z serwera IMAP.
    """
    
    config = _load_config()  # Wczytanie konfiguracji z pliku config.json
    mail = login_to_imap(config) # Logowanie do serwera IMAP
    inboxes = [name for _, _, name in mail.list_folders()] # Pobieranie listy skrzynek odbiorczych
    mail.logout()  # Zamykanie połączenia z serwerem IMAP
    return inboxes

def fetch_emails(inbox="INBOX", filtr=["ALL"]):
    """
    Funkcja do pobierania e-maili z serwera IMAP.
    """

    try:
        
        config = _load_config() # Wczytujemy konfigurację z pliku config.json
        mail = login_to_imap(config) # Logujemy się do serwera IMAP
        mail.select_folder(inbox, readonly=True)  # Wybieramy skrzynkę odbiorczą
        # readonly=True oznacza, że nie będziemy modyfikować skrzynki odbiorczej (np. oznaczać wiadomości jako przeczytane przy pobieraniu).
        uids = mail.search(filtr)  # Szukamy maili z użyciem określonego filtra
        # ["ALL'] lub ['UNSEEN'], ['FROM', 'adres@kogoś.pl'], itd.
        mails = [] # Przygotowanie listy do przechowywania e-maili

        # Konwertujemy pobrane przez IMAP obiekty MIME na Email zdefiniowane w base_models.py
        for uid in uids:
            raw_message = mail.fetch([uid], ["BODY[]", "FLAGS"]) #fetch zwraca słownik, gdzie kluczem jest UID wiadomości, a wartością jest słownik z danymi wiadomości.
            message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"]) #extractujemy z tego słownika treść wiadomości w formacie MIME.

            subject = message.get_subject() # Pobieramy temat wiadomości
            from_ = message.get_addresses("from") # Pobieramy dane nadawcy w postaci krotki (nazwa, adres e-mail)
            to_ = message.get_addresses("to") # Pobieramy dane odbiorcy w postaci krotki (nazwa, adres e-mail)
            date = message.get_decoded_header("date") # Pobieramy datę wiadomości

            if message.html_part:
                body = message.html_part.get_payload().decode(message.html_part.charset) # Dekodujemy treść HTML wiadomości
                body_type = "html" #Ustawiamy typ treści na HTML
            elif message.text_part:
                body = message.text_part.get_payload().decode(message.text_part.charset) # Dekodujemy treść tekstową wiadomości
                body_type = "text" # Ustawiamy typ treści na tekst
            else:
                body = "" # Jeśli nie ma części HTML ani tekstowej, ustawiamy pusty ciąg
                body_type = "text" # Domyślny typ treści to tekst
        
            attachments = [] # Lista do przechowywania załączników
        
            for part in message.mailparts:
                if part.filename: # Sprawdzamy, czy część wiadomości ma nazwę pliku (czyli jest załącznikiem)
                    attachment = part.get_payload() # Pobieramy zawartość załącznika
                    filename = part.filename or "unknown" #Ustawiamy nazwę pliku załącznika, jeśli nie jest podana, to "unknown"
                    content = base64.b64encode(attachment).decode('utf-8') # Kodujemy zawartość załącznika w base64 i dekodujemy na UTF-8
                    attachments.append({"filename": filename, "content": content}) # Tworzymy słownik z nazwą pliku i zawartością w base64, dodajemy go do listy załączników
    
            mails.append(
                Email(
                    subject=subject,
                    from_name=from_[0][0] if from_ else "Nieznany nadawca",
                    from_mail=from_[0][1] if from_ else "Nieznany nadawca",
                    to_name=to_[0][0] if to_ else "Nieznany odbiorca",
                    to_mail=to_[0][1] if to_ else "Nieznany odbiorca",
                    date=date,
                    body=body,
                    body_type=body_type,
                    attachments=attachments
                ) # Tworzymy obiekt Email z pobranymi danymi
            )
        mail.logout()  # Zamykanie połączenia z serwerem IMAP
        return mails  # Zwracamy listę e-maili jako odpowiedź
    except imapclient.exceptions.LoginError as e:
        raise HTTPException(status_code=401, detail=f"Błąd logowania do serwera IMAP: {str(e)}") # Błąd logowania do serwera IMAP
    except imapclient.exceptions.IMAPClientError as e:
        raise HTTPException (status_code=500, detail=f"Błąd połączenia z serwerem IMAP: {str(e)}") # Błąd połączenia z serwerem IMAP
    except Exception as e: 
        raise HTTPException (status_code=500, detail=f"Nieznany błąd: {str(e)}") # Inne nieoczekiwane błędy

def send_email(email: Email):
    """
    Funkcja do wysyłania e-maili przez serwer SMTP.
    """
    try:
        config = _load_config()  # Wczytanie konfiguracji z pliku config.json
        smtp = login_to_smtp(config)  # Logowanie do serwera SMTP

        msg = MIMEMultipart() # Tworzenie wiadomości MIME
        msg["Subject"] = email.subject
        msg["From"] = (f"{email.from_name} <{email.from_mail}>" if email.from_name else email.from_mail) # Ustawianie nadawcy wiadomości
        msg["To"] = (f"{email.to_name} <{email.to_mail}>" if email.to_name else email.to_mail) # Ustawianie odbiorcy wiadomości
        msg.attach(MIMEText(email.body, email.body_type)) # Dodawanie treści wiadomości (HTML lub tekst) do obiektu MIME

        if (email.attachments):
            for attachment in email.attachments:
                decoded_content = base64.b64decode(attachment.content)  # Dekodowanie zawartości załącznika z base64 do postaci binarnej
                part = MIMEApplication(decoded_content, Name=attachment.filename) # Tworzenie części MIME dla załącznika
                part["Content-Disposition"] = f'attachment; filename="{attachment.filename}"' # Ustawianie nagłówka Content-Disposition, aby wskazać, że jest to załącznik
                msg.attach(part) # Dodawanie załącznika do obiektu drzewa MIME

        smtp.sendmail(email.from_mail, [email.to_mail], msg.as_string())  # Wysyłka wiadomości
        smtp.quit()  # Zamknięcie połączenia
        return {"status": "ok"}  # Zwracamy status powodzenia
            
    except smtplib.SMTPAuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"Błąd uwierzytelniania SMTP: {str(e)}") #Błąd uwierzytelniania SMTP
    except smtplib.SMTPRecipientsRefused as e:
        raise HTTPException(status_code=422, detail=f"Odrzucono adres odbiorcy: {str(e)}") # Odrzucono adres odbiorcy
    except smtplib.SMTPSenderRefused as e:
        raise HTTPException(status_code=400, detail=f"Odrzucono adres nadawcy: {str(e)}") # Odrzucono adres nadawcy
    except smtplib.SMTPConnectError as e:
        raise HTTPException(status_code=503, detail=f"Nie można połączyć się z serwerem SMTP: {str(e)}") # Błąd połączenia z serwerem SMTP
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nieznany błąd: {str(e)}") # Inne nieoczekiwane błędy
