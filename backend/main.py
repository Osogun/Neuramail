import uvicorn # Pakiet do uruchamiania aplikacji FastAPI
import threading # Pakiet do obsługi wątków
from pathlib import Path # Pakiet do obsługi ścieżek plików
from datetime import datetime, timedelta # Pakiet do obsługi dat i czasu
import base64 # Pakiet do kodowania i dekodowania base64
from fastapi import FastAPI, HTTPException, Request # Pakiety FastAPI do tworzenia API
from fastapi.middleware.cors import CORSMiddleware # Middleware do obsługi CORS
from contextlib import asynccontextmanager # Pakiet do zarządzania kontekstem asynchronicznym
from sqlalchemy import or_, and_ # Funkcje logiczne do tworzenia zapytań SQLAlchemy
import logging # Pakiet do logowania 

from base_models import * # Import modeli Pydantic, które definiują struktury danych dla API
from database import * # Import modułów do obsługi bazy danych, w tym silnika, sesji i bazowej klasy modeli
from db_models import * # Import modeli bazy danych, które są mapowane na tabele w bazie danych

from mailbox_functions import send_email, fetch_emails, handle_opeation_on_imap, delete_emails
from db_functions import background_sync


from loadconfig import _load_config 

status_flag = False # Flaga do sprawdzania statusu synchronizacji

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
    
    
    # Zrób test diagnostyczny
    db_path = Path("./mailapp.db")
    try:
        db_path.parent.mkdir(exist_ok=True)  # Upewnij się, że folder istnieje
        with open(db_path, "a"):
            pass
        print("Plik bazy danych dostępny/zapisywalny.")
    except Exception as e:
        print(f"BŁĄD PLIKU BAZY: {e}")
    
    
    # Inicjalizacja bazy danych, ta funkcja tworzy wszystkie tabele w bazie danych na podstawie zdefiniowanych modeli w Base
    # Jeśli tabele już istnieją, nie zostaną ponownie utworzone.
    Base.metadata.create_all(bind=engine)
    # Wczytanie konfiguracji z pliku config.json
    config = _load_config()
    # Sprawdzenie czy synchronizacja ma być uruchomiona przy starcie
    if config.get("sync_on_startup"):
        threading.Thread(target=background_sync(status_flag), daemon=True).start()
  
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"Zadanie HTTP: {request.method} {request.url.path} BODY: {body}")
    response = await call_next(request)
    return response

### Endpointy API
@app.get("/root")
async def root():
    """
    Endpoint informujący, że backend odpalił i działa poprawnie.
    """
    return {"status": "ok"}
        
@app.get("/api/inboxes")
def get_mailboxes_from_db():
    """
    Endpoint do pobierania listy skrzynek pocztowych z bazy danych.
    """
    try:
        db = SessionLocal()  # Tworzenie sesji do bazy danych
        db_query = SessionLocal().query(DBMailbox)  # Tworzenie zapytania do bazy danych
        result = db_query.all()  # Pobranie wszystkich wyników zapytania
        return {"inboxes": result, "status_flag": status_flag}  # Zwrócenie listy skrzynek pocztowych i statusu synchronizacji
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
    finally:
        db.close()

@app.post("/api/metadata")
def get_metadata_from_db(query: EmailQuery):
    db = SessionLocal()
    try:
        db_query = db.query(DBEmail) # Tworzenie zapytania do bazy danych

        # Filtrowanie dynamiczne
        if query.mailbox_name:
            db_query = db_query.filter(DBEmail.mailbox_name == query.mailbox_name)
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
        if query.date:
            try:
                date_dt = datetime.strptime(query.date, "%Y-%m-%d")
                # Filtrowanie tylko po konkretnym dniu (od początku dnia do końca dnia)
                date_end = date_dt + timedelta(days=1)
                db_query = db_query.filter(
                    and_(
                        DBEmail.date >= date_dt,
                        DBEmail.date < date_end
                    )
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'date'")
        if query.since and not query.date and not query.before:
            try:
                since_dt = datetime.strptime(query.since, "%Y-%m-%d")
                db_query = db_query.filter(DBEmail.date > since_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'since'")
        if query.before and not query.date and not query.since:
            try:
                before_dt = datetime.strptime(query.before, "%Y-%m-%d")
                # Dodajemy jeden dzień i porównujemy z <, aby uwzględnić cały dzień "before"
                before_dt_end = before_dt + timedelta(days=1)
                db_query = db_query.filter(DBEmail.date < before_dt_end)
            except ValueError:
                raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'before'")

        # Wykonanie zapytania
        result = db_query.all() # Pobranie wszystkich wyników zapytania
        if not result:
            raise HTTPException(status_code=404, detail="Nie znaleziono żadnych wiadomości spełniających kryteria")
        return {"emails": [email.__dict__ for email in result], "status_flag": status_flag}  # Zwrócenie listy wiadomości i statusu synchronizacji
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
    finally:
        db.close()

@app.post("/api/get_email")
def get_email_by_imap(query: GetEmails):
    try:
        email = handle_opeation_on_imap(lambda mail: fetch_emails(query, mail))
        return email
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

@app.post("/api/delete_emails")
def delete_emails_from_imap(query: DeleteEmails):
    """
    Endpoint do usuwania wiadomości z serwera IMAP.
    """
    try:
        handle_opeation_on_imap(lambda mail: delete_emails(query, mail))
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
    finally:
        sync_mailbox()  # Uruchomienie synchronizacji skrzynki po usunięciu wiadomości
    
@app.get("/api/sync")
def sync_mailbox(): 
    """
    Endpoint do ręcznego uruchomienia synchronizacji skrzynki pocztowej.
    """
    try:
        if status_flag:
            raise HTTPException(status_code=400, detail="Synchronizacja już trwa")
        threading.Thread(target=background_sync(status_flag), daemon=True).start()
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")   
    
# build: pyinstaller --onefile --name main main.py
# CMD znajdz proces: netstat -ano | findstr :8000
# CMD zabij proces: taskkill /PID {tuWstawPID} /F /T
# reczne odpalanie backendu: uvicorn main:app --reload --port 8000

