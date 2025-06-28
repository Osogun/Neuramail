import imapclient # IMAPClient to biblioteka do obsługi protokołu IMAP, która umożliwia łatwe połączenie i interakcję z serwerami pocztowymi
import imapclient.exceptions # Wyjątki specyficzne dla IMAPClient, które mogą wystąpić podczas logowania lub interakcji z serwerem IMAP
import pyzmail # Pyzmail to biblioteka do parsowania wiadomości e-mail w formacie MIME, która umożliwia łatwe odczytywanie treści wiadomości, nagłówków i załączników
import smtplib # SMTP to biblioteka do obsługi protokołu SMTP, która umożliwia wysyłanie wiadomości e-mail przez serwer SMTP
import base64 # Pakiet do kodowania i dekodowania base64, który jest używany do przesyłania załączników w wiadomościach e-mail
from fastapi import HTTPException # HTTPException to wyjątek FastAPI, który jest używany do zwracania błędów HTTP z odpowiednim kodem statusu i komunikatem
from email.mime.multipart import MIMEMultipart # MIMEMultipart to klasa z biblioteki email, która umożliwia tworzenie wiadomości e-mail w formacie MIME, która może zawierać wiele części (np. tekst, HTML, załączniki)
from email.mime.text import MIMEText # MIMEText to klasa z biblioteki email, która umożliwia tworzenie części wiadomości e-mail w formacie tekstowym (np. HTML lub zwykły tekst)
from email.mime.application import MIMEApplication # MIMEApplication to klasa z biblioteki email, która umożliwia tworzenie części wiadomości e-mail dla załączników, które nie są tekstem (np. pliki PDF, obrazy itp.)

from base_models import *
from loadconfig import _load_config

# ----------------------------------------
# Funkcje pomocnicze
# ----------------------------------------

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

def get_uids(mail, mailbox, filtr=["ALL"]):
    mail.select_folder(mailbox, readonly=True)
    return mail.search(filtr) # ["ALL'] lub ['UNSEEN'], ['FROM', 'adres@kogoś.pl'], itd.

def fetch_email(mail, mailbox, uid):
    '''
    Funkcja do pobierania pojedynczje wiadomości e-mail z serwera IMAP.
    '''
    
    # Wybieramy skrzynkę poztową
    mail.select_folder(mailbox, readonly=True)
    # Pobieramy wiadomość o podanym UID
    raw_message = mail.fetch([uid], ["BODY[]", "FLAGS"])  # fetch zwraca słownik, gdzie kluczem jest UID wiadomości, a wartością jest słownik z danymi wiadomości
    # Przetwarzamy pobraną wiadomość do formatu MIME
    message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"]) 
    # Pobieramy flagi wiadomości (np. czy jest przeczytana, oznaczona jako spam itp.)
    flags = raw_message[uid][b"FLAGS"]
    # Pobieramy temat wiadomości, nadawcę i datę
    subject = message.get_subject()
    from_ = message.get_addresses("from") # Krotka (nazwa nadawcy, adres e-mail)
    date = message.get_decoded_header("date")
    # Parser wiadomości MIME zawiera różne części wiadomości, takie jak tekst, HTML i załączniki
    # W pierwszej kolejności sprawdzamy, czy wiadomość ma część HTML lub tekstową i pobieramy jej treść
    if message.html_part:
        body = message.html_part.get_payload().decode(message.html_part.charset)
        body_type = "html" 
    elif message.text_part:
        body = message.text_part.get_payload().decode(message.text_part.charset)
        body_type = "text" 
    else:
        body = ""
        body_type = "text"
    # Następnie przetwarzamy załączniki wiadomości
    attachments = [] 
    for part in message.mailparts:
        if (part.filename): # Sprawdzamy, czy część wiadomości jest załącznikiem (tak jeżeli ma nazwę pliku)
            '''
            Istnieje też nagłówek part.disposition, który może mieć wartość 'attachment' lub 'inline', ale nie jest to zawsze obecne.
            Dlatego sprawdzamy tylko, czy jest nazwa pliku (part.filename), co jest wystarczające do identyfikacji załącznika.
            '''
            attachment = part.get_payload()  # Pobieramy zawartość załącznika
            filename = part.filename
            content = base64.b64encode(attachment).decode("utf-8") #Przetwarzamy plik binarny do postaci tekstu zakodowanego w base64, aby można było go przesłać w formacie JSON
            size = len(attachment)  #Pobieramy rozmiar załącznika w bajtach
            attachments.append(Attachment(
                filename=filename,
                content=content,
                size=size,
            ))  # Tworzymy obiekt załacznika i dodajemy go do listy
    
    # Zwracamy obiekt Email z pobranymi danymi            
    return Email(
        uid=uid,
        subject=subject,
        sender=(from_[0][1] if from_ else "Nieznany nadawca"),
        sender_name=from_[0][0] if from_ else "Nieznany",
        date=date,
        content=body,
        body_type=body_type,
        attachments=attachments,
        mailbox=mailbox,
        flags=flags)
     
# ----------------------------------------
# Funkcje do ekspotu z modułu
# ----------------------------------------
  
def fetch_mailboxes(mail=None):
    """
    Funkcja do pobierania listy skrzynek odbiorczych z serwera IMAP.
    Musi zostać wywowłana w kontekści handle_operation_on_imap jako callback - lambda: fetch_mailboxes()
    ponieważ wymaga przkazywanego parametru mail z aktywnympołączenia IMAP.
    Zwraca listę obiektów Mailbox, które zawierają informacje o skrzynkach pocztowych:
    liczbę nieprzeczytanych wiadomości, liczbę wszystkich wiadomości, 
    unikalny identyfikator skrzynki pocztowej (uidvalidity) oraz listę unikalnych identyfikatorów wiadomości (uids_list).
    """
    # Pobieramy listę folderów (skrzynek pocztowych) z serwera IMAP
    mailboxes_list = [name for _, _, name in mail.list_folders()]
    # Inicjalizujemy pustą listę do przechowywania obiektów Mailbox
    mailboxes = []
    # Iterujemy przez listę folderów i tworzymy obiekty Mailbox
    for mailbox in mailboxes_list:
        try:
            # Wybieramy folder (skrzynkę pocztową) i pobieramy jej status
            mail.select_folder(mailbox, readonly=True)
            status = mail.folder_status(mailbox, ["UNSEEN", "MESSAGES", "UIDVALIDITY"])
            uids_list = mail.search(['ALL'])  # Pobieramy listę UID-ów wiadomości w folderze
            # Tworzymy obiekt Mailbox z pobranych danych
            mailboxes.append(Mailbox(name=mailbox, unread_count=status[b"UNSEEN"], total_count=status[b"MESSAGES"], uidvalidity=status[b"UIDVALIDITY"], uids_list=uids_list))
        except Exception as e:
            # Obsługa błędów, jeśli wystąpią podczas pobierania statusu folderu
            print(f"Błąd przy przetwarzaniu folderu: {mailbox}, pomijam. Błąd: {e}")

    return mailboxes

def fetch_emails(query: GetEmails, mail=None):
    """
    Funkcja do pobierania e-maili z serwera IMAP.
    Musi zostać wywowłana w kontekści handle_operation_on_imap jako callback - lambda: fetch_emails(query)
    ponieważ wymaga przkazywanego parametru mail z aktywnym połączeniem IMAP.
    Przyjmuje obiekt GetEmails, który zawiera listę UID-ów wiadomości do pobrania oraz nazwę skrzynki pocztowej.
    Zwraca listę obiektów Email, które zawierają szczegóły pobranych wiadomości e-mail.
    """
    emails = []
    for uid in query.uid_list:
        email = fetch_email(mail, query.mailbox, uid)
        emails.append(email) 
        
    return emails
    
def handle_opeation_on_imap(callback):
    """
    Funkcja pomocnicza do obsługi operacji na serwerze IMAP. Obługuje logowanie oraz wyjątki związane z logowaniem i połączeniem z serwerem IMAP.
    Przyjmuje funkcję callback, która zostanie wywołana wewnątrz kontekstu połączenia IMAP.
    Przykład użycia:
    handle_operation_on_imap(lambda mail: fetch_mailboxes())
    handle_operation_on_imap(lambda mail: fetch_emails(query))
    Zwraca wynik działania funkcji callback.
    """
    try:
        # Wczytanie konfiguracji z pliku config.json
        config = _load_config() 
        # Logowanie do serwera IMAP
        mail = login_to_imap(config)
        # Wywołanie funkcji callback z połączeniem IMAP
        result = callback(mail)
        # Zamykanie połączenia z serwerem IMAP
        mail.logout()
        # Zwracamy wynik działania funkcji callback
        return result
    
    # Obsługa wyjątków
    except imapclient.exceptions.LoginError as e:
        raise HTTPException(status_code=401, detail=f"Błąd logowania do serwera IMAP: {str(e)}")  # Błąd logowania do serwera IMAP
    
    except imapclient.exceptions.IMAPClientError as e:
        raise HTTPException(status_code=500, detail=f"Błąd połączenia z serwerem IMAP: {str(e)}")  # Błąd połączenia z serwerem IMAP
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nieznany błąd: {str(e)}")  # Inne nieoczekiwane błędy   

def send_email(email: SendEmail):
    """
    Funkcja do wysyłania e-maili przez serwer SMTP.
    Przyjmuje obiekt SendEmail, który zawiera szczegóły wiadomości e-mail, takie jak temat, adres odbiorcy, 
    treść, typ treści (HTML lub tekst) oraz opcjonalne załączniki.
    """
    try:
        # Wczytanie konfiguracji z pliku config.json i zalogowanie do serwera SMTP
        config = _load_config()
        smtp = login_to_smtp(config) 
        # Tworzenie obiektu MIME dla wiadomości e-mail
        msg = MIMEMultipart() 
        msg["Subject"] = email.subject
        msg["To"] = email.mail_to
        msg.attach(MIMEText(email.content, email.body_type))
        # Obsługa załączników do wiadomości e-mail
        if email.attachments:
            for attachment in email.attachments:
                # Dekodowanie zawartości załącznika z base64 do postaci binarnej
                decoded_content = base64.b64decode(attachment.content)
                # Tworzenie części MIME dla załącznika
                part = MIMEApplication(decoded_content, Name=attachment.filename) 
                # Ustawienie nagłówka Content-Disposition dla załącznika, żeby przeglądarki i klienty pocztowe wiedziały, że to jest załącznik
                part["Content-Disposition"] = (f'attachment; filename="{attachment.filename}"')
                # Dodawanie załącznika do obiektu drzewa MIME
                msg.attach(part)

        # Wysyłanie wiadomości e-mail przez serwer SMTP
        smtp.sendmail(config.get("email"), [email.mail_to], msg.as_string())
        # Zamykanie połączenia z serwerem SMTP
        smtp.quit() 
        # Zwracanie statusu operacji
        return {"status": "ok"}

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
