import time
from datetime import datetime
from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, Query, status
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


@app.get("/snippets/{snippet_id}")
def get_snippet(snippet_id: int, repo=Depends(get_repo)) -> Snippet:
    try:
        return repo.get(snippet_id)
    except SnippetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with id {snippet_id} not found",
        )


@app.delete("/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet(snippet_id: int, repo=Depends(get_repo)):
    try:
        repo.delete(snippet_id)
        return
    except SnippetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with id {snippet_id} not found",
        )


@app.post("/snippets/{snippet_id}/toggle-favorite")
def toggle_favorite(snippet_id: int, repo=Depends(get_repo)) -> Snippet:
    try:
        return repo.toggle_favorite(snippet_id)
    except SnippetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with id {snippet_id} not found",
        )


class TagsPayload(BaseModel):
    tags: list[str]


@app.post("/snippets/{snippet_id}/add-tags", status_code=status.HTTP_201_CREATED)
def add_tags(
    snippet_id: int,
    tags_payload: Annotated[
        TagsPayload, Body()
    ],  # Example: {"tags": ["python", "fastapi", "web"]}
    repo=Depends(get_repo),
):
    try:
        repo.get(snippet_id)
    except SnippetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet with id {snippet_id} not found",
        )
    for t in tags_payload.tags:
        repo.add_tag(snippet_id, t)

    return repo.get(snippet_id)


@app.get("/search")
def search(
    q: Annotated[
        str,
        Query(
            ...,  # Required
            min_length=3,
            max_length=25,
            pattern=r".*\S.*",  # Must contain non-whitespace
            description="3-25 chars; Must contain non-whitespace",
        ),
    ],
    repo=Depends(get_repo),
):
    return repo.fuzzy_search(q.strip().lower())
