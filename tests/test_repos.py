from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.exceptions import SnippetNotFoundError
from src.snipster.models import Language, SnippetCreate, SnippetPublic
from src.snipster.repo import DatabaseBackedSnippetRepo, InMemorySnippetRepo


@pytest.fixture
def snippet() -> SnippetCreate:
    return SnippetCreate(
        title="My Snippet", code="print('stuff')", language=Language.PYTHON
    )


@pytest.fixture
def another_snippet() -> SnippetCreate:
    return SnippetCreate(
        title="My Snippet", code="console.log('stuff')", language=Language.JAVASCRIPT
    )


@pytest.fixture(scope="function")
def im_repo() -> InMemorySnippetRepo:
    return InMemorySnippetRepo()


@pytest.fixture(scope="function")
def db_repo() -> Generator[DatabaseBackedSnippetRepo, None, None]:
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield DatabaseBackedSnippetRepo(session=session)


def test_in_memory_repo_add(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, SnippetPublic)


def test_in_memory_repo_get(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    retrieved = im_repo.get(stored_snippet.id)
    assert retrieved is not None
    assert retrieved.id == stored_snippet.id
    assert retrieved.title == snippet.title
    assert retrieved.code == snippet.code
    assert retrieved.language == snippet.language
    with pytest.raises(SnippetNotFoundError):
        im_repo.get(9999)


def test_in_memory_repo_list(snippet, another_snippet, im_repo):
    im_repo.add(snippet)
    list = im_repo.list()
    assert len(list) == 1
    stored_snippet = list[0]
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    im_repo.add(another_snippet)
    list = im_repo.list()
    assert len(list) == 2


def test_in_memory_repo_delete(snippet, im_repo):
    im_repo.add(snippet)
    list = im_repo.list()
    stored_snippet = list[0]
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    im_repo.delete(stored_snippet.id)
    with pytest.raises(SnippetNotFoundError):
        im_repo.get(stored_snippet.id)


def test_db_repo_add(db_repo, snippet):
    stored_snippet = db_repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, SnippetPublic)


def test_db_repo_get(db_repo, snippet):
    stored_snippet = db_repo.add(snippet)
    retrieved_snippet = db_repo.get(stored_snippet.id)
    assert retrieved_snippet is not None
    assert retrieved_snippet.id == stored_snippet.id
    assert retrieved_snippet.title == snippet.title
    assert retrieved_snippet.code == snippet.code
    assert retrieved_snippet.language == snippet.language
    with pytest.raises(SnippetNotFoundError):
        db_repo.get(9999)


def test_db_repo_list(db_repo, snippet, another_snippet):
    db_repo.add(snippet=snippet)
    assert len(db_repo.list()) == 1
    db_repo.add(snippet=another_snippet)
    assert len(db_repo.list()) == 2


def test_db_repo_delete(db_repo, snippet):
    db_repo.add(snippet=snippet)
    assert len(db_repo.list()) == 1
    retrieved_snippet = db_repo.list()[0]
    db_repo.delete(retrieved_snippet.id)
    assert len(db_repo.list()) == 0
