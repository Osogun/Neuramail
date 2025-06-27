from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint, UniqueConstraint, ForeignKey
from database import Base

class DBInbox(Base):
    __tablename__ = "mailboxes"
    name = Column(String, primary_key=True)  # np. "INBOX"
    unread_count = Column(Integer)
    total_count = Column(Integer)
    uidvalidity = Column(Integer)

class DBAttachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    email_uid = Column(Integer, ForeignKey("emails.uid"))  # UWAGA: to za mało przy kluczu złożonym!
    filename = Column(String)
    size = Column(Integer)

    __table_args__ = (
        UniqueConstraint('email_uid', 'filename', name='unique_attachment_per_email'),
    )
    
class DBEmail(Base):
    __tablename__ = "emails"
    uid = Column(Integer)
    mailbox_name = Column(String)
    sender = Column(String)
    sender_name = Column(String)
    date = Column(String)
    subject = Column(String)
    content_preview = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('uid', 'mailbox_name'),
    )
