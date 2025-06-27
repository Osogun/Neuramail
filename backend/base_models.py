from pydantic import BaseModel

class Email(BaseModel):
    subject: str
    from_name: str | None = None
    from_mail: str
    to_name: str | None = None
    to_mail: str
    date: str | None = None
    body: str
    body_type: str
    
class EmailQuery(BaseModel):
    inbox: str = "INBOX"  # Default to INBOX
    filtr: str="ALL"  # Default filter to fetch all emails
    keyword: str = None  # Keyword to filter emails by subject or body
    from_email: str = None  # Email address to filter emails from
    to_email: str = None  # Email address to filter emails to
    since: str = None  # Date in YYYY-MM-DD format to filter emails since this date, ex. "2023-01-01"
    before: str = None  # Date in YYYY-MM-DD format to filter emails before this, ex. "2023-01-31"
