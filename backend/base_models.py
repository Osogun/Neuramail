from pydantic import BaseModel

class Inbox(BaseModel):
    name: str
    unread_count: int = 0
    total_count: int = 0
    uidvalidity: int = None  # UIDVALIDITY for the mailbox, used to check if the mailbox has changed

class Attachment(BaseModel):
    filename: str
    content: str  # base64 string

class Email(BaseModel):
    uid: int = None  # Unique identifier for the email
    subject: str
    sender: str
    sender_name: str = None
    date: str = None
    body: str
    body_type: str = "html"
    attachments: list[Attachment] = []

class GetEmail(BaseModel):
    uid: int
    mailbox: str

class SendEmail(BaseModel):
    subject: str
    mail_to: str
    from_mail: str
    from_mail_name: str = None
    body: str
    body_type: str = 'html'
    attachments: list[Attachment] = []
        
class EmailQuery(BaseModel):
    mailbox: str = "INBOX"  # Default to INBOX
    sender: str = None #sender email
    sender_name: str = None  # Sender name
    date: str = None  # Date of email
    subject: str = None  #Subject of email
    keyword: str = None #Keyword in subject or in body of email
    since: str = None # Date in YYYY-MM-DD format to filter emails since this date, ex. "2023-01-01"
    before: str = None  # Date in YYYY-MM-DD format to filter emails before this, ex. "2023-01-31"

