import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.imap_smtp_fun import get_inbox_list, fetch_emails, send_email, fetch_emails_metadata
from base_models import Email, EmailQuery
from datetime import datetime
from pathlib import Path
import base64
from . import db_models
from .database import engine
from db_fun import sync_mailbox_metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("BACKEND: Server wystartował")
    db_models.Base.metadata.create_all(bind=engine)
    sync_mailbox_metadata()

    yield
    # cleanup np. zamknięcie połączeń, zapis logów itp.
    print("BACKEDN: Shutdown aplikacji")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.post("/api/test")
async def send_pdf():
    try:
        # Wczytaj plik PDF z dysku
        file_path = Path("test.pdf")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Plik test.pdf nie istnieje.")

        with open(file_path, "rb") as f:
            content = f.read()

        # Zakoduj do base64
        encoded = base64.b64encode(content).decode("utf-8")

        # Stwórz obiekt Email (dostosuj do swojego modelu)
        email = Email(
            subject="Test Email",
            from_name="Test",
            from_mail="oskargum@gmail.com",
            to_name="Test",
            to_mail="oskargum@gmail.com",
            date="",
            body="This is a test email with a PDF attachment.",
            body_type="text",
            attachments=[{"filename": "test.pdf", "content": encoded}]
        )

        send_email(email)  # zakładam że ta funkcja rzuca wyjątki HTTPException jeśli coś pójdzie nie tak
        return {"status": "ok"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
        
@app.get("/api/inboxes")
def get_inboxes():
    """
    Endpoint to fetch the list of inboxes.
    """
    inboxes = get_inbox_list()
    return {"inboxes": inboxes}

@app.post("/api/metadata")
def get_email_by_imap(query: EmailQuery):
    filtr = [query.filtr]

    if query.keyword:
        filtr += ["TEXT", query.keyword]
    if query.from_email:
        filtr += ["FROM", query.from_email]
    if query.to_email:
        filtr += ["TO", query.to_email]
    if query.since:
        filtr += ["SINCE", format_imap_date(query.since)]
    if query.before:
        filtr += ["BEFORE", format_imap_date(query.before)]

    try:
        mails = fetch_emails_metadata(query.inbox, filtr)
        return mails  # Obiekty BaseModel są automatycznie serializowane do JSON, więc nie trzeba ich konwertować na słownik
    except HTTPException as e:
        raise e

@app.post("/api/emails")
def get_email_by_imap(query: EmailQuery):
    filtr = [query.filtr]

    if query.keyword:
        filtr += ["TEXT", query.keyword]
    if query.from_email:
        filtr += ["FROM", query.from_email]
    if query.to_email:
        filtr += ["TO", query.to_email]
    if query.since:
        filtr += ["SINCE", format_imap_date(query.since)]
    if query.before:
        filtr += ["BEFORE", format_imap_date(query.before)]

    try:
        mails = fetch_emails(query.inbox, filtr)
        return mails  # Obiekty BaseModel są automatycznie serializowane do JSON, więc nie trzeba ich konwertować na słownik
    except HTTPException as e:
        raise e


@app.post("/api/send")
def send_email_by_stmp(email: Email):
    try:
        status = send_email(email)
        return(status)
    except HTTPException as e:
        raise e


def format_imap_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%d-%m-%Y") # zamiana formatu DD-MM-YYYY na datetime
    return dt.strftime("%d-%b-%Y")  # zamiana datetime na format IMAP 'DD-Mon-YYYY'



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# build: pyinstaller --onefile --name main main.py
# CMD znajdz proces: netstat -ano | findstr :8000
# CMD zabij proces: taskkill /PID {tuWstawPID} /F /T
# reczne odpalanie backendu: uvicorn main:app --reload --port 8000

