import uvicorn # Pakiet do uruchamiania aplikacji FastAPI
import threading # Pakiet do obsługi wątków
from pathlib import Path # Pakiet do obsługi ścieżek plików
from datetime import datetime # Pakiet do obsługi dat i czasu
import base64 # Pakiet do kodowania i dekodowania base64
from fastapi import FastAPI, HTTPException # Pakiety FastAPI do tworzenia API
from fastapi.middleware.cors import CORSMiddleware # Middleware do obsługi CORS
from contextlib import asynccontextmanager # Pakiet do zarządzania kontekstem asynchronicznym
from sqlalchemy import or_, and_ # Funkcje logiczne do tworzenia zapytań SQLAlchemy


from base_models import * # Import modeli Pydantic, które definiują struktury danych dla API
from database import * # Import modułów do obsługi bazy danych, w tym silnika, sesji i bazowej klasy modeli
from db_models import * # Import modeli bazy danych, które są mapowane na tabele w bazie danych

from mailbox_functions import send_email, fetch_emails, handle_opeation_on_imap, fetch_mailboxes
from db_functions import background_sync


from loadconfig import _load_config 


# Asynchroniczny menedżer kontekstu, tj. taka "asynchroniczna werjsa with"
"""
Menedżer kontekstu to konstrukcja programistyczna, która zarządza zasobami w określonym zakresie działania — zapewnia automatyczne wykonanie kodu 
przy wejściu i wyjściu z „kontekstu”, np. otwieranie i zamykanie pliku, otwieranie i zwalnianie połączenia z bazą danych, itp.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Metoda zarządzająca cyklem życia aplikacji FastAPI.
    '''
    ### Kod wykonywany przy otwarciu zasobu - uruchomienia FastAPI
    print("BACKEND: Start backendu")
    # Inicjalizacja bazy danych, ta funkcja tworzy wszystkie tabele w bazie danych na podstawie zdefiniowanych modeli w Base
    # Jeśli tabele już istnieją, nie zostaną ponownie utworzone.
    Base.metadata.create_all(bind=engine)
    # Wczytanie konfiguracji z pliku config.json
    config = _load_config()
    # Sprawdzenie czy synchronizacja ma być uruchomiona przy starcie
    if config.get("sync_on_startup"):
        threading.Thread(target=background_sync, daemon=True).start()
        
    ### Kod wykonywany przy zamknięciu zasobu - zamknięcia FastAPI
    yield
    print("BACKEND: Shutdown backendu")

# Tworzenie instancji FastAPI z menedżerem cyklu życia
app = FastAPI(lifespan=lifespan)

# Dodanie middleware CORS, aby umożliwić dostęp z innych domen (w tym wypadku z frontendu przez elektron)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Endpointy API
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
def get_mailboxes_by_imap():
    """
    Endpoint do pobierania listy skrzynek pocztowych z serwera IMAP.
    """
    try:
        inboxes = handle_opeation_on_imap(lambda mail: fetch_mailboxes(mail))
        return {"inboxes": inboxes}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

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
def get_email_by_imap(query: GetEmails):
    try:
        emails = handle_opeation_on_imap(lambda mail: fetch_emails(query, mail))
        return emails
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

@app.post("/api/send_email")
def send_email_by_smtp(email: SendEmail):
    try:
        status = send_email(email)
        return status
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# build: pyinstaller --onefile --name main main.py
# CMD znajdz proces: netstat -ano | findstr :8000
# CMD zabij proces: taskkill /PID {tuWstawPID} /F /T
# reczne odpalanie backendu: uvicorn main:app --reload --port 8000

