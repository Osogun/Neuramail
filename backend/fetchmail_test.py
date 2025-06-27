import imapclient
import pyzmail
import json
from pathlib import Path
from pydantic import BaseModel

class Email(BaseModel):
    subject: str
    from_name: str
    from_mail: str
    to_name: str
    to_mail: str
    date: str
    body: str

# Dane logowania
host_imap = "imap.gmail.com"  # lub inny serwer IMAP
email = "oskargum@gmail.com"
password = "epkiiqlfgiztqpee"  # epki iqlf gizt qpee

# Połączenie i logowanie
mail = imapclient.IMAPClient(host_imap, ssl=True)
mail.login(email, password)

# Wybieramy skrzynkę odbiorczą
mail.select_folder("INBOX", readonly=True)

# Szukamy maili (tu: wszystkie nieprzeczytane)
uids = mail.search(["UNSEEN"])  # lub ['ALL'], ['FROM', 'adres@kogoś.pl'], itd.

mails=[]


for uid in uids:
    raw_message = mail.fetch([uid], ["BODY[]", "FLAGS"])
    message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"])

    subject = message.get_subject()
    from_ = message.get_addresses("from")
    to_ = message.get_addresses("to")
    date = message.get_decoded_header("date")

    if message.html_part:
        body = message.html_part.get_payload().decode(message.html_part.charset)
    elif message.text_part:
        body = message.text_part.get_payload().decode(message.text_part.charset)
    else:
        body = "Brak treści"
        
    # Tworzenie obiektu Email
    email_data = Email(
        subject=subject,
        from_name=from_[0][0] if from_ else "Nieznany nadawca",
        from_mail=from_[0][1] if from_ else "Nieznany nadawca",
        to_name=to_[0][0] if to_ else "Nieznany odbiorca",
        to_mail=to_[0][1] if to_ else "Nieznany odbiorca",
        date=date,
        body=body
    )

    mails.append(email_data)
    
inboxes = mail.list_folders()
print(inboxes)
folder_names = [name for _, _, name in inboxes]
print(folder_names[0])



    #print("📩 Temat:", subject)
    #print("📨 Od:", from_)
    #print("📥 Do:", to_)
    #print("📅 Data:", date)
    # print('📃 Treść:', body)
    #print("📃 Treść:", body[:300])  # tylko fragment
    #print("-" * 40)

