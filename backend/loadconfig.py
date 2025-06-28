import sys
from pathlib import Path
import json

def _load_config() -> dict:
    """
    Wczytuje plik konfiguracyjny z danymi logowania.
    """
    # Sprawdzenie, czy aplikacja jest uruchomiona jako skompilowany plik .exe (np. z PyInstaller) czy jako skrypt Pythona.
    """
    gattr(sys, "frozen", False) sprawdza, czy aplikacja jest uruchomiona jako skompilowany plik .exe (np. z PyInstaller),
    a jeśli nie, to zwraca False. Jeżeli aplikacja jest uruchomiona jako skrypt Pythona, to sys.frozen będzie False. W przeciwnym razie będzie True.
    - sys.executable zwraca ścieżkę do pliku wykonywalnego Pythona, który jest aktualnie uruchomiony (skrypt lub skompilowany plik .exe),
    - Path(sys.executable) tworzy obiekt Path z tej ścieżki,
    - .resolve() przekształca tę ścieżkę do pełnej, absolutnej ścieżki,
    - .parent pobiera folder, w którym ten plik wykonywalny się znajduje,
    """
    if getattr(sys, "frozen", False):
        config_path = Path(sys.executable).resolve().parent / "config.json"
    else:
        # Jeśli aplikacja jest uruchomiona jako skrypt Pythona
        config_path = Path(__file__).resolve().parent / "dist/config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Brak pliku konfiguracyjnego: {config_path}")

    with config_path.open() as f:
        return json.load(f)
