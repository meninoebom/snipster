import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///snipster.sqlite")
engine = create_engine(db_url, echo=False)


@contextmanager
def get_session():
    """Yield a database session, properly closing it after use."""
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
