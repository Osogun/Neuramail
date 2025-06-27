# Neuramail
Aplikacja klienta pocztowego z agentem AI

## Konfiguracja backendu

1. Skopiuj plik `config.example.json` do `backend/dist/config.json`.
2. Uzupełnij w nim dane logowania do serwera IMAP (`host_imap`, `email`, `hasło`, `host_smtp`).
3. Hasło do poczty GMAIL musi być hasłem aplikacji - https://myaccount.google.com/security -> Weryfikacja dwuetapowa.
4. Zmiana pola `sync_on_startup` na `flase` wyłaczy synchronizację bazy danych z skrzynką pocztową (tryb deweloperski).

Dysk z dokumentami dla projektu: https://drive.google.com/drive/folders/1joA6oAuo0ZnhBmkR9xbgm5WahEPIE2Fn?fbclid=IwY2xjawLJ2JRleHRuA2FlbQIxMABicmlkETBialVvYmJBWENvdk9Galh4AR67-hZQzLzESMGP_ghe2DWgVbVzPOGtclciwaooPDQVof4HVY2lMX7kfOOUBg_aem_KY6acSCggMjWqA-XpQGxTQ

