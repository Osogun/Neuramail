from pydantic import BaseModel # BaseModel to klasa bazowa dla modeli Pydantic, która zapewnia walidację danych i serializację do JSON podczas komunikacji z API

class Mailbox(BaseModel):
    name: str
    uidvalidity: int = None  # Unikalny identyfikator skrzynki pocztowej, który jest używany do sprawdzania, czy skrzynka została zmodyfikowana
    unread_count: int = 0
    total_count: int = 0
    uids_list: list[int] = []  # Lista unikalnych identyfikatorów wiadomości w obrębie skrzynki pocztowej, razem z uidvalidity uid tworzy unikalny identyfikator wiadomości
    
class Attachment(BaseModel):
    filename: str
    content: str  # base64 string
    size: int

class Email(BaseModel):
    uid: int = None  # Unikalny identyfikator wiadomości w obrębie skrzynki pocztowej, razem z uidvalidity tworzy unikalny identyfikator wiadomości
    subject: str
    sender: str
    sender_name: str = None
    date: str = None
    content: str
    body_type: str = "html"
    attachments: list[Attachment] = []
    mailbox: str
    flags: list[str] = [] 

class GetEmails(BaseModel):
    uid_list: list[int]
    mailbox: str

class SendEmail(BaseModel):
    subject: str
    mail_to: str
    content: str
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

