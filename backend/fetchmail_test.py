import imapclient
import pyzmail
import json
from pathlib import Path

config_path = Path(__file__).with_name("config.json")
if not config_path.exists():
    raise FileNotFoundError(
        "Brak pliku config.json. Utwórz go na podstawie config.example.json"
    )
with config_path.open() as f:
    config = json.load(f)

host = config.get("host")
email = config.get("email")
password = config.get("password")

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

