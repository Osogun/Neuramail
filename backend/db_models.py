from sqlalchemy import Column, Integer, String
from .database import Base

class DBMailbox(Base):
    __tablename__ = "mailboxes"
    name = Column(String, primary_key=True)  # np. "INBOX"
    uidvalidity = Column(Integer)

class DBAttachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    email_uid = Column(Integer)  # Foreign key to DBEmail.uid
    filename = Column(String)
    content_type = Column(String)  # e.g. "application/pdf"
    size = Column(Integer)  # Size in bytes

class DBEmail(Base):
    __tablename__ = "emails"
    uid = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    sender_name = Column(String)    
    date = Column(String)
    subject = Column(String)
    content_preview = Column(String)
    mailbox_name = Column(String)
