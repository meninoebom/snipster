import time
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from .db import default_session_factory
from .exceptions import SnippetNotFoundError
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


@app.post("/create", status_code=status.HTTP_201_CREATED)
def create_snippet(snippet: SnippetCreate, repo=Depends(get_repo)) -> Snippet:
    return repo.add(snippet)


@app.get("/snippets", status_code=status.HTTP_200_OK)
def list_snippets(repo=Depends(get_repo)) -> list[Snippet]:
    return repo.list()


@app.get("/snippet/{snippet_id}")
async def get_snippet(snippet_id: int, repo=Depends(get_repo)) -> Snippet:
    try:
        return repo.get(snippet_id)
    except SnippetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with id {snippet_id} not found",
        )
