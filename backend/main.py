import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fetchmail import fetch_emails

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


@app.get("/api/test")
def test():
    mails = fetch_emails()
    mail = mails[0] if mails else None
    if mail:
        return {
            "subject": mail["subject"],
            "from": mail["from"],
            "to": mail["to"],
            "date": mail["date"],
            "body": mail["body"][:300]  # Zwracamy tylko fragment treści
        }
    else:
        return {"message": "No new emails found."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


# build: pyinstaller --onefile --name main main.py
# CMD znajdz proces: -ano | findstr :8000
# CMD zabij proces: taskkill /PID {tuWstawPID} /F /T
