from pydantic import BaseModel # BaseModel to klasa bazowa dla modeli Pydantic, która zapewnia walidację danych i serializację do JSON podczas komunikacji z API
from datetime import datetime

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
    date: datetime = None
    content: str
    body_type: str = "html"
    attachments: list[Attachment] = []
    mailbox: str
    flags: list[str] = [] 

class GetEmails(BaseModel):
    uid_list: list[int]
    mailbox: str

class DeleteEmails(BaseModel):
    uid: list[int]
    mailbox: str

class SendEmail(BaseModel):
    subject: str
    mail_to: str
    content: str
    body_type: str = 'html'
    attachments: list[Attachment] = []
        
class EmailQuery(BaseModel):
    mailbox_name: str = "INBOX"  # Skrzynka pocztowa do wyszukiwania wiadomości, domyślnie "INBOX"
    sender: str = None # Adres e-mail nadawcy do wyszukiwania
    sender_name: str = None  # Nazwa nadawcy do wyszukiwania
    subject: str = None  # Temat wiadomości do wyszukiwania
    keyword: str = None # Słowo kluczowe do wyszukiwania w temacie lub treści wiadomości
    date: str = None # Data w formacie YYYY-MM-DD, do filtrowania wiadomości po dacie, ex. "2023-01-01"
    since: str = None # Data w formacie YYYY-MM-DD, do filtrowania wiadomości od tej daty, ex. "2023-01-31"
    before: str = None  # Data w formacie YYYY-MM-DD, do filtrowania wiadomości przed tą datą, ex. "2023-01-31"

