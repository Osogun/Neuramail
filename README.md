# Neuramail
Aplikacja klienta pocztowego z agentem AI.

## Konfiguracja backendu
`Punkty 1-4 wykonujemy tylko przy pierwszej konfiguracji projektu. Punkt 5 przy każdej nowej łatce!`

1. Skopiuj plik `config.example.json` do `backend/dist/config.json`.
2. Uzupełnij w nim dane logowania do serwera IMAP (`host_imap`, `email`, `hasło`, `host_smtp`).
3. Hasło do poczty GMAIL musi być hasłem aplikacji - [link](https://myaccount.google.com/security) -> Weryfikacja dwuetapowa.
4. Zmiana pola `sync_on_startup` na `false` wyłaczy synchronizację bazy danych z skrzynką pocztową (można przestawiać w razie potrzeby w trybie deweloperskim).
5. Przejdź do /backend i zbuduj aplikację komendą `pyinstaller --onefile --name main main.py`

## Konfiguracja frontendu

1. Przejdź do /frontend i zbuduj aplikację komena `npm run build`

## Uruchomienie aplikacji

1. W katalogu głównym odpal program komendą `npm run start`
2. Gdy aplikacja jest uruchomiona endpointy API można testować pod adresem: http://localhost:8000/docs

Dysk z dokumentami dla projektu: [Dysk Google](https://drive.google.com/drive/folders/1joA6oAuo0ZnhBmkR9xbgm5WahEPIE2Fn?fbclid=IwY2xjawLJ2JRleHRuA2FlbQIxMABicmlkETBialVvYmJBWENvdk9Galh4AR67-hZQzLzESMGP_ghe2DWgVbVzPOGtclciwaooPDQVof4HVY2lMX7kfOOUBg_aem_KY6acSCggMjWqA-XpQGxTQ)

Mail pomocniczy do testowania: neuramail2025@gmail.com
Hasło: neuram@il_dev

