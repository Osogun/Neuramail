import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fetchmail import get_inbox_list, fetch_emails
from base_models import Email, EmailQuery
from datetime import datetime


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/inboxes")
def get_inboxes():
    """
    Endpoint to fetch the list of inboxes.
    """
    inboxes = get_inbox_list()
    return {"inboxes": inboxes}

@app.post("/api/emails")
def get_emails(query: EmailQuery):
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

    mails = fetch_emails(query.inbox, filtr)
    return mails  # Obiekty BaseModel są automatycznie serializowane do JSON, więc nie trzeba ich konwertować na słownik


def format_imap_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%d-%m-%Y") # zamiana formatu DD-MM-YYYY na datetime
    return dt.strftime("%d-%b-%Y")  # zamiana datetime na format IMAP 'DD-Mon-YYYY'



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# build: pyinstaller --onefile --name main main.py
# CMD znajdz proces: netstat -ano | findstr :8000
# CMD zabij proces: taskkill /PID {tuWstawPID} /F /T
# reczne odpalanie backendu: uvicorn main:app --reload --port 8000
