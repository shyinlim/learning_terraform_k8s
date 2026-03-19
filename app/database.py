from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./items.db"

engine = create_engine(url=DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base() # The Item class in models.py will then inherit from it.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
