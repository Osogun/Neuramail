from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint, UniqueConstraint, ForeignKey, Index
from database import Base

class DBMailbox(Base):
    __tablename__ = "mailboxes"
    uidvalidity = Column(Integer, primary_key=True)  # Unikalny identyfikator skrzynki IMAP
    name = Column(String)
    unread_count = Column(Integer)
    total_count = Column(Integer)

class DBEmail(Base):
    __tablename__ = "emails"
    uid = Column(Integer) # Unikalny identyfikator wiadomości w obrębie skrzynki pocztowej, razem z uidvalidity tworzy unikalny identyfikator wiadomości
    subject = Column(String)
    sender = Column(String)
    sender_name = Column(String)
    date = Column(String)
    content_preview = Column(String)
    mailbox_name = Column(String)
    mailbox_uidvalidity = Column(Integer, ForeignKey("mailboxes.uidvalidity"))
    body_type = Column(String)
    flags = Column(String)

    __table_args__ = (
        # Unikalny klucz główny składający się z uid i mailbox_uidvalidity
        PrimaryKeyConstraint('uid', 'mailbox_uidvalidity'),
        # Indeks przyspieszający wyszukiwanie wiadomości po uid i mailbox_uidvalidity
        Index("ix_mailbox_mail_uid", "mailbox_uidvalidity", "uid"),
        # Przyspieszona filtracja po nadawcy w ramach skrzynki
        Index("ix_mailbox_sender", "mailbox_name", "sender"),
        # Przyspieszona filtracja po nazwie nadawcy
        Index("ix_mailbox_sender_name", "mailbox_name", "sender_name"),
        
        #Indexy tworzą specjalne struktury danych, które przyspieszają wyszukiwanie wiadomości, 
        #przypisując odpowiednim "kluczon" lub kombinacją "kluczy" indeksy wierszy, które je zawierają.
        #Dzięki temu przeszukiwanie jest szybsza ale kosztem większego zużycia pamięci i czasu przy dodawaniu nowych wiadomości.
        
    )

class DBAttachment(Base):
    __tablename__ = "attachments"
    email_uid = Column(Integer, ForeignKey("emails.uid")) 
    mailbox_uidvalidity =Column(Integer, ForeignKey("mailboxes.uidvalidity"))
    filename = Column(String)
    size = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('email_uid', 'mailbox_uidvalidity', 'filename', name='unique_attachment_per_email'), # Unikalny klucz dla załącznika w obrębie wiadomości i skrzynki
        Index("ix_email_uid", "email_uid", "mailbox_uidvalidity")  # Indeks przyspieszający wyszukiwanie załączników po email_uid i mailbox_uidvalidity
    )

