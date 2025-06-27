from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import DBEmail, DBMailbox
from backend.mailbox_fun import fetch_emails_metadata, get_inboxes, get_uids
from bs4 import BeautifulSoup
import pyzmail

from db_models import DBEmail, DBMailbox
from sqlalchemy.orm import Session

def sync_mailbox_metadata():
    db: Session = SessionLocal()

    # 🔁 Pobranie listy wszystkich folderów (np. INBOX, Sent, Trash)
    folders = get_inboxes()

    for folder in folders:

        # --- 1. UIDVALIDITY
        mailbox = db.query(DBMailbox).filter_by(name=folder.name).first()

        if not mailbox:
            mailbox = DBMailbox(name=folder.name, uidvalidity=folder.uidvalidity)
            db.add(mailbox)
            db.commit()
        elif mailbox.uidvalidity != folder.uidvalidity:
            db.query(DBEmail).filter(DBEmail.mailbox_name == folder).delete(synchronize_session=False)
            mailbox.uidvalidity = folder.uidvalidity
            db.commit()

        # --- 2. Porównanie UID-ów
        remote_uids = set(get_uids())
        local_uids = set(
            uid for (uid,) in db.query(DBEmail.uid).filter(DBEmail.mailbox_name == folder).all()
        )

        to_fetch = list(remote_uids - local_uids)
        to_delete = list(local_uids - remote_uids)

        # --- 3. Pobieranie nowych maili
        for uid in to_fetch:
            email, attachments = fetch_emails_metadata(folder, to_fetch)
            db.add(email)
            for attachment in attachments:
                db.add(attachment)

        # --- 4. Usuwanie z bazy
        if to_delete:
            db.query(DBEmail).filter(
                DBEmail.mailbox_name == folder,
                DBEmail.uid.in_(to_delete)
            ).delete(synchronize_session=False)

        db.commit()

    db.close()

