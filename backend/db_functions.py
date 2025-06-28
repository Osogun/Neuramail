from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import *
from mailbox_functions import fetch_mailboxes, fetch_emails, handle_opeation_on_imap
from bs4 import BeautifulSoup
import pyzmail

from sqlalchemy.orm import Session
from base_models import *

class DBModelParser:
    
    @staticmethod
    def parse_mailbox(mailbox: Mailbox):
        """
        Parse mailbox to DBMailbox.
        """
        return DBMailbox(
            name=mailbox.name,
            uidvalidity=mailbox.uidvalidity,
            unread_count=mailbox.unread_count,
            total_count=mailbox.total_count,
        )
            
    @staticmethod
    def parse_email(mailbox: Mailbox, email: Email):
        """
        Parse email to DBEmail.
        """
        return DBEmail(
            uid=email.uid,
            subject=email.subject,
            sender=email.sender,
            sender_name=email.sender_name,
            date=email.date,
            content_preview=email.content[:25],
            mailbox_name=mailbox.name,
            mailbox_uidvalidity=mailbox.uidvalidity,
            body_type=email.body_type)
           
    @staticmethod
    def parse_attachment(mailbox: Mailbox, email: Email, attachment: DBAttachment):
        """
        Parse attachment content and return a structured dictionary.
        """
        return DBAttachment(
            email_uid=email.uid,
            mailbox_uidvalidity=mailbox.uidvalidity,
            filename=attachment.filename,
            size=attachment.size
        )
        
    @staticmethod
    def get_uids_list(mailbox: Mailbox):
        """ 
        Get list of UIDs from mailbox.
        """
        return mailbox.uids_list if mailbox.uids_list else []   

def sync_mailbox_metadata():
    db: Session = SessionLocal()

    # Pobranie listy wszystkich folderów (np. INBOX, Sent, Trash)
    mailboxes_list = handle_opeation_on_imap(lambda mail: fetch_mailboxes(mail))

    for mailbox_data in mailboxes_list:
        
        ### 1. Walidacja spójności danych o skrzynkach pocztowych    
        # Sprawdzenie, czy skrzynka o danej nazwie już istnieje w bazie danych, poprzez pobranie jej reprezentacji z bazy
        mailbox = db.query(DBMailbox).filter_by(name=mailbox_data.name).first()
        # Jeżeli skrzynka nie istnieje, tworzymy nowy obiekt DBMailbox i dodajemy go do bazy
        if not mailbox:
            mailbox = DBModelParser.parse_mailbox(mailbox_data)
            db.add(mailbox)
            db.commit()
        # Jeżeli skrzynka istnieje, walidujemy zgodność identyfiaktorów UIDVALITY
        elif mailbox.uidvalidity != mailbox_data.uidvalidity:
            # Jeżeli identyfikator UIDVALIDITY się zmienił, usuwamy z bazy danych wszystkie maile i załaczniki przypisane do tej skrzynki (zostaną pobrane ponownie)
            db.query(DBEmail).filter(DBEmail.mailbox_name == mailbox.name).delete(synchronize_session=False)
            db.query(DBAttachment).filter(DBAttachment.mailbox_uidvalidity == mailbox.uidvalidity).delete(synchronize_session=False)
            # Aktualizujemy UIDVALIDITY skrzynki w bazie danych
            mailbox.uidvalidity = mailbox_data.uidvalidity
            db.commit()
        
        ### 2. Walidacja spójności danych o wiadomościach i załącznikach    
        # Porównujemy listę UID wiadomości w skrzynce z tymi, które są już w bazie danych
        remote_uids = set(DBModelParser.get_uids_list(mailbox_data))
        local_uids = set(uid for (uid,) in db.query(DBEmail.uid).filter(DBEmail.mailbox_name == mailbox.name).all())
        to_fetch = list(remote_uids - local_uids)
        to_delete = list(local_uids - remote_uids)

        ### 3. Pobieranie nowych wiadomości i załączników
        imap_query = GetEmails(uid_list=to_fetch, mailbox=mailbox.name)
        emails = handle_opeation_on_imap(lambda mail: fetch_emails(imap_query, mail))

        # Dodaj nowe e-maile
        for email_data in emails:
            existing = db.query(DBEmail).filter_by(uid=email_data.uid, mailbox_uidvalidity=mailbox.uidvalidity).first()
            if not existing:
                db.add(DBModelParser.parse_email(mailbox, email_data))

            # Dodaj nowe załączniki
            attachments = email_data.attachments if email_data.attachments else []
            for attachment_data in attachments:
                existing = db.query(DBAttachment).filter_by(mailbox_uidvalidity=mailbox.uidvalidity, email_uid=email_data.uid, filename=attachment_data.filename).first()
                if not existing:
                    db.add(DBModelParser.parse_attachment(mailbox, email_data, attachment_data))


        # --- 4. Usuwanie z bazy
        if to_delete:
            db.query(DBEmail).filter(
                DBEmail.mailbox_name == mailbox_data.name,
                DBEmail.uid.in_(to_delete)
            ).delete(synchronize_session=False)

        db.commit()

    db.close()

# Uruchamiamy sync jako jednorazowy task w tle
def background_sync():
    try:
        sync_mailbox_metadata()
        print("[SYNC] Synchronizacja zakończona")
    except Exception as e:
        print(f"[SYNC] Błąd podczas synchronizacji: {e}")