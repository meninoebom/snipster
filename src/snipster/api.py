import time
from datetime import datetime

from fastapi import Depends, FastAPI, status
from pydantic import BaseModel

from .db import default_session_factory
from .models import Snippet, SnippetCreate
from .repo import DatabaseBackedSnippetRepo as db_repo

app = FastAPI()

start_time = time.time()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime_seconds=time.time() - start_time,
    )


def get_session():
    with default_session_factory.get_session() as session:
        yield session


def get_repo(session=Depends(get_session)):
    return db_repo(session=session)


@app.post("/create", response_model=Snippet, status_code=status.HTTP_201_CREATED)
def create_snippet(snippet: SnippetCreate, repo=Depends(get_repo)):
    return repo.add(snippet)
