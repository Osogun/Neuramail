import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mailbox_fun import send_email, fetch_emails_metadata, get_inboxes, fetch_email_data
from base_models import Email, EmailQuery, SendEmail, GetEmail
from datetime import datetime
from pathlib import Path
import base64
from database import Base, engine
from db_fun import sync_mailbox_metadata
from contextlib import asynccontextmanager
import threading
from loadconfig import _load_config
from database import SessionLocal
from db_models import DBEmail
from sqlalchemy import or_
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("BACKEND: Start backendu")

    Base.metadata.create_all(bind=engine)
    config = _load_config()

    # Uruchamiamy sync jako jednorazowy task w tle
    def background_sync():
        try:
            sync_mailbox_metadata()
            print("[SYNC] Synchronizacja zakończona")
        except Exception as e:
            print(f"[SYNC] Błąd podczas synchronizacji: {e}")

    if config.get("sync_on_startup"):
        threading.Thread(target=background_sync, daemon=True).start()

    yield
    print("BACKEND: Shutdown backendu")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_inboxes_by_imap():
    """
    Endpoint to fetch the list of inboxes.
    """
    inboxes = get_inboxes()
    print(inboxes)
    return {"inboxes": inboxes}

@app.post("/api/metadata")
def get_metadata_from_db(query: EmailQuery):
    db = SessionLocal()
    try:
        db_query = db.query(DBEmail)

        # Filtrowanie dynamiczne
        if query.mailbox:
            db_query = db_query.filter(DBEmail.mailbox_name == query.mailbox)
        if query.sender:
            db_query = db_query.filter(DBEmail.sender == query.sender)
        if query.sender_name:
            db_query = db_query.filter(DBEmail.sender_name == query.sender_name)
        if query.subject:
            db_query = db_query.filter(DBEmail.subject.contains(query.subject))
        if query.keyword:
            db_query = db_query.filter(
                or_(
                    DBEmail.subject.contains(query.keyword),
                    DBEmail.content_preview.contains(query.keyword)
                )
            )
        if query.since:
            try:
                since_dt = datetime.strptime(query.since, "%Y-%m-%d")
                db_query = db_query.filter(DBEmail.date >= since_dt.isoformat())
            except ValueError:
                raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'since'")
        if query.before:
            try:
                before_dt = datetime.strptime(query.before, "%Y-%m-%d")
                db_query = db_query.filter(DBEmail.date <= before_dt.isoformat())
            except ValueError:
                raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'before'")

        # Wykonanie zapytania
        result = db_query.all()
        return [email.__dict__ for email in result]

    finally:
        db.close()

@app.post("/api/get_email")
def get_email_by_imap(query: GetEmail):
    try:
        mails = fetch_email_data(query.mailbox, query.uid)
        return mails  # Obiekty BaseModel są automatycznie serializowane do JSON, więc nie trzeba ich konwertować na słownik
    except HTTPException as e:
        raise e


@app.post("/api/send_email")
def send_email_by_stmp(email: SendEmail):
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

