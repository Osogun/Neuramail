import imapclient
import pyzmail
import json
import smtplib
import sys

from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel
from base_models import Email, EmailQuery

def _load_config() -> dict:
    """Wczytuje plik konfiguracyjny z danymi logowania."""
    if getattr(sys, 'frozen', False):
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

def login_to_email():
    """
    Funkcja do logowania się do serwera IMAP.
    Zwraca obiekt IMAPClient po zalogowaniu.
    """
    
    config = _load_config()

    host = config.get("host_imap")
    email = config.get("email")
    password = config.get("password")

    # Połączenie i logowanie
    mail = imapclient.IMAPClient(host, ssl=True)
    mail.login(email, password)
    
    return mail


# Funkcje do ekspotu
def get_inbox_list():
    
    mail = login_to_email()
    inboxes = [name for _, _, name in mail.list_folders()]
    return inboxes

def fetch_emails(inbox="INBOX", filtr=["ALL"]):
    """
    Funkcja do pobierania e-maili z serwera IMAP.
    """
    
    mail = login_to_email()
    # Wybieramy skrzynkę odbiorczą
    mail.select_folder(inbox, readonly=True) #readonly=True oznacza, że nie będziemy modyfikować skrzynki odbiorczej (np. oznaczać wiadomości jako przeczytane przy pobieraniu).

    # Szukamy maili
    uids = mail.search(filtr)  # ["ALL'] lub ['UNSEEN'], ['FROM', 'adres@kogoś.pl'], itd.
    
    mails = []

    for uid in uids:
        raw_message = mail.fetch([uid], ["BODY[]", "FLAGS"])
        message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"])

        subject = message.get_subject()
        from_ = message.get_addresses("from")
        to_ = message.get_addresses("to")
        date = message.get_decoded_header("date")

        if message.html_part:
            body = message.html_part.get_payload().decode(message.html_part.charset)
            body_type = "html"
        elif message.text_part:
            body = message.text_part.get_payload().decode(message.text_part.charset)
            body_type = "text"
        else:
            body = "Brak treści"
            body_type = "text"       
          
        mails.append(Email(
            subject=subject,
            from_name=from_[0][0] if from_ else "Nieznany nadawca",
            from_mail=from_[0][1] if from_ else "Nieznany nadawca",
            to_name=to_[0][0] if to_ else "Nieznany odbiorca",
            to_mail=to_[0][1] if to_ else "Nieznany odbiorca",
            date=date,
            body=body,
            body_type=body_type
        ))
        
    return mails


def send_mail(email: Email):
    """Send an email using SMTP based on the configuration."""

    config = _load_config()
    host = config.get("host_smtp")
    port = config.get("smtp_port", 465)

    msg = MIMEMultipart()
    msg["Subject"] = email.subject
    msg["From"] = (
        f"{email.from_name} <{email.from_mail}>" if email.from_name else email.from_mail # Do weryfikacji
    )
    msg["To"] = f"{email.to_name} <{email.to_mail}>" if email.to_name else email.to_mail #Tez
    msg.attach(MIMEText(email.body, email.body_type))
    
    # Oprogramowac dodawanie załączników !!

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(config.get("email"), config.get("password"))
        smtp.sendmail(email.from_mail, [email.to_mail], msg.as_string())

    return True
