from sqlalchemy import create_engine # SQLAlchemy do połączenia z bazą danych
from sqlalchemy.orm import sessionmaker, declarative_base # SQLAlchemy do tworzenia sesji oraz danych w stylu ORM (klasa-tabela)
DATABASE_URL = "sqlite:///./dist/mailapp.db"

# Silnik połączenia do bazy danych SQLite, z argumentem do obsługi wielu wątków
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) 
# Obiekt do tworzenia sesji do bazy danych, z autocommit i autoflush wyłączonymi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
"""
Autocommit=false wyłącza automatyczne zatwierdzanie transakcji
Autoflush=false wyłącza tymczasowe przesyłanie obiektów do bazy danych wykonywane przed commitowaniem transakcji, dzięki czemu transakcja wykonywana jest w całości lub w ogóle (ACID)
"""
# Deklaratywna baza danych, która będzie używana do tworzenia modeli; dzięki niej możemy tworzyć klasy, które będą mapowane na tabele w bazie danych
Base = declarative_base()
"""
ORM (Object-Relational Mapping, czyli mapowanie obiektowo-relacyjne) to technika programowania, która pozwala pracować z bazą danych
jak z obiektami w kodzie — bez konieczności pisania SQL-a ręcznie.
"""