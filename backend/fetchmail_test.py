import imapclient
import pyzmail
import json
from pathlib import Path

# Dane logowania
host = "imap.gmail.com"  # lub inny serwer IMAP
email = "oskargum@gmail.com"
password = "epkiiqlfgiztqpee"  # epki iqlf gizt qpee

# Połączenie i logowanie
mail = imapclient.IMAPClient(host, ssl=True)
mail.login(email, password)

# Wybieramy skrzynkę odbiorczą
mail.select_folder("INBOX", readonly=True)

# Szukamy maili (tu: wszystkie nieprzeczytane)
uids = mail.search(["UNSEEN"])  # lub ['ALL'], ['FROM', 'adres@kogoś.pl'], itd.

for uid in uids:
    raw_message = mail.fetch([uid], ["BODY[]", "FLAGS"])
    message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"])

    subject = message.get_subject()
    from_ = message.get_addresses("from")
    to_ = message.get_addresses("to")
    date = message.get_decoded_header("date")

    if message.text_part:
        body = message.text_part.get_payload().decode(message.text_part.charset)
    elif message.html_part:
        body = message.html_part.get_payload().decode(message.html_part.charset)
    else:
        body = "Brak treści"

    print("📩 Temat:", subject)
    print("📨 Od:", from_)
    print("📥 Do:", to_)
    print("📅 Data:", date)
    # print('📃 Treść:', body)
    print("📃 Treść:", body[:300])  # tylko fragment
    print("-" * 40)

