import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///snippet.sqlite")

engine = create_engine(db_url, echo=False)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session"""
    return Session(engine)
