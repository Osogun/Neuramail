from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import DBEmail, DBInbox, DBAttachment
from mailbox_fun import fetch_emails_metadata, get_inboxes, get_uids
from bs4 import BeautifulSoup
import pyzmail

from db_models import DBEmail, DBInbox
from sqlalchemy.orm import Session

def sync_mailbox_metadata():
    db: Session = SessionLocal()

    # Pobranie listy wszystkich folderów (np. INBOX, Sent, Trash)
    folders = get_inboxes()

    for folder in folders:

        # --- 1. UIDVALIDITY
        mailbox = db.query(DBInbox).filter_by(name=folder.name).first()

        if not mailbox:
            mailbox = DBInbox(name=folder.name, unread_count=folder.unread_count, total_count=folder.total_count, uidvalidity=folder.uidvalidity)
            db.add(mailbox)
            db.commit()
        elif mailbox.uidvalidity != folder.uidvalidity:
            db.query(DBEmail).filter(DBEmail.mailbox_name == folder.name).delete(synchronize_session=False)
            mailbox.uidvalidity = folder.uidvalidity
            db.commit()

        # --- 2. Porównanie UID-ów
        remote_uids = set(get_uids(folder.name))
        local_uids = set(
            uid for (uid,) in db.query(DBEmail.uid).filter(DBEmail.mailbox_name == folder.name).all()
        )

        to_fetch = list(remote_uids - local_uids)
        to_delete = list(local_uids - remote_uids)

        # --- 3. Pobieranie nowych maili
        emails, attachments = fetch_emails_metadata(folder.name, to_fetch)

        # Dodaj nowe e-maile
        for email in emails:
            existing = db.query(DBEmail).filter_by(uid=email.uid, mailbox_name=email.mailbox_name).first()
            if not existing:
                db.add(email)

        # Dodaj nowe załączniki
        for attachment in attachments:
            existing = db.query(DBAttachment).filter_by(email_uid=attachment.email_uid, filename=attachment.filename).first()
            if not existing:
                db.add(attachment)


        # --- 4. Usuwanie z bazy
        if to_delete:
            db.query(DBEmail).filter(
                DBEmail.mailbox_name == folder.name,
                DBEmail.uid.in_(to_delete)
            ).delete(synchronize_session=False)

        db.commit()

    db.close()

