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

    
class EmailQuery(BaseModel):
    inbox: str = "INBOX"  # Default to INBOX
    filtr: str="ALL"  # Default filter to fetch all emails
    keyword: str = None  # Keyword to filter emails by subject or body
    from_email: str = None  # Email address to filter emails from
    to_email: str = None  # Email address to filter emails to
    since: str = None  # Date in YYYY-MM-DD format to filter emails since this date, ex. "2023-01-01"
    before: str = None  # Date in YYYY-MM-DD format to filter emails before this, ex. "2023-01-31"
