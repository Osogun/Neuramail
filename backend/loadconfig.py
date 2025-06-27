import sys
from pathlib import Path
import json

def _load_config() -> dict:
    """
    Wczytuje plik konfiguracyjny z danymi logowania.
    """

    if getattr(sys, "frozen", False):
        # Jeśli aplikacja jest uruchomiona jako skompilowany plik .exe
        config_path = Path(sys.executable).resolve().parent / "config.json"
        # - sys.executable wskazuje na ścieżkę do pliku wykonywalnego (.exe) po kompilacji,
        # - .resolve().parent pobiera folder, w którym ten plik .exe się znajduje,
        # - / "config.json" dodaje nazwę pliku konfiguracyjnego do tej ścieżki.
    else:
        # Jeśli aplikacja jest uruchomiona jako skrypt Pythona
        config_path = Path(__file__).resolve().parent / "dist/config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Brak pliku konfiguracyjnego: {config_path}")

    with config_path.open() as f:
        return json.load(f)
