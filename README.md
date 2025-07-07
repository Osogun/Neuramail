# Neuramail
Aplikacja klienta pocztowego z agentem AI.

## Konfiguracja backendu
**UWAGA: Punkty 1-4 wykonujemy tylko przy pierwszej konfiguracji projektu. Punkt 5 przy każdej nowej łatce!**

1. Skopiuj plik `config.example.json` do `backend/dist/config.json`.
2. Uzupełnij w nim dane logowania do serwera IMAP (`host_imap`, `email`, `hasło`, `host_smtp`).
3. Hasło do poczty GMAIL musi być hasłem aplikacji - [link](https://myaccount.google.com/security) -> Weryfikacja dwuetapowa.
4. Zmiana pola `sync_on_startup` na `false` wyłaczy synchronizację bazy danych z skrzynką pocztową (można przestawiać w razie potrzeby w trybie deweloperskim).
5. Przejdź do /backend i zbuduj aplikację komendą `pyinstaller --onefile --name main main.py`

*Na dysku Google znajduje się poprawnie skonfigurowany plik config.json*

## Konfiguracja frontendu

1. Przejdź do /frontend i zbuduj aplikację komendą `npm run build`

## Uruchomienie aplikacji

1. W katalogu głównym odpal program komendą `npm run start`
2. Gdy aplikacja jest uruchomiona endpointy API można testować pod adresem: http://localhost:8000/docs

## Różne
1. Dysk z dokumentami dla projektu: [Dysk Google](https://drive.google.com/drive/folders/1joA6oAuo0ZnhBmkR9xbgm5WahEPIE2Fn?fbclid=IwY2xjawLJ2JRleHRuA2FlbQIxMABicmlkETBialVvYmJBWENvdk9Galh4AR67-hZQzLzESMGP_ghe2DWgVbVzPOGtclciwaooPDQVof4HVY2lMX7kfOOUBg_aem_KY6acSCggMjWqA-XpQGxTQ)
2. Mail pomocniczy do testowania: neuramail2025@gmail.com

*Na dysku Google znajduje się hasło do pcozty w pliku HASLO_DO_POCZTY.txt*

## Technologia
1. Aplikacja zbudowana w Electron.js
2. Frontend zbudowany w React + Tailwind
3. Backend zbudowany w FastAPI
4. Baza danych zbudowana w SQLite
5. Model LLM GPT-4o / Llama 4

## Zbudowanie i uruchomienie aplikacji na Linuxie 
>uwaga, testowane na systemie Debian 12

### budowa backendu
1. W folderze backend stwórz wirtualne środowisko - `python3 -m venv venv`
2. Aktywuj wirtualne środowisko - `source venv/bin/activate`
3. Zainstaluj potrzebne biblioteki - `pip install -r requirements.txt`
4. Zainstaluj pyinstaller - `pip install pyinstaller`
5. Zbuduj backend - `pyinstaller --onefile --name main main.py`
6. Pobierz `config.json` i umieść go w `backend/dist/`

### budowa frontendu
1. Przejdź do folderu `frontend/` i zainstaluj zależności - `npm i`
2. Zbuduj aplikację - `npm run build`

### uruchomienie elektrona
1. Zainstaluj nvm - `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`
2. Zrestartuj basha - `source ~/.bashrc`
3. Zainstaluj i użyj Node 20.19.1 - `nvm install 20.19.1`, a następnie `nvm use 20.19.1`
4. Potwierdź wersję - `node -v`
5. `rm -rf node_modules package-lock.json`
6. `npm install`
7. `npm install --save-dev electron`
8. `npm start`
