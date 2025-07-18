from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.exceptions import SnippetNotFoundError
from src.snipster.models import Language, Snippet, SnippetCreate
from src.snipster.repo import DatabaseBackedSnippetRepo, InMemorySnippetRepo

# =============================================================================
# Fixtures
# =============================================================================


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
    session = Session(engine)
    try:
        yield DatabaseBackedSnippetRepo(session=session)
    finally:
        session.close()


# =============================================================================
# Helper Functions
# =============================================================================


def add_search_data(repo):
    snippet1 = SnippetCreate(
        title="Foo",
        code="print('foo')",
        description="This is a foo snippet",
        language=Language.PYTHON,
    )
    repo.add(snippet=snippet1)

    snippet2 = SnippetCreate(
        title="Bar",
        code="print('bar')",
        description="This is a bar snippet",
        language=Language.PYTHON,
    )
    repo.add(snippet=snippet2)

    snippet3 = SnippetCreate(
        title="Baz",
        code="print('baz')",
        description="This is a baz snippet",
        language=Language.PYTHON,
    )
    repo.add(snippet=snippet3)

    snippet4 = SnippetCreate(
        title="Super Foo",
        code="print('foo foo foo')",
        description="This is a foo snippet but even more so",
        language=Language.PYTHON,
    )
    repo.add(snippet=snippet4)

    snippet5 = SnippetCreate(
        title="Blah",
        code="print('blah blah blah')",
        description="This is a blah snippet",
        language=Language.PYTHON,
        tags=["foo"],
    )
    repo.add(snippet=snippet5)


# =============================================================================
# InMemorySnippetRepo Tests
# =============================================================================


def test_in_memory_repo_add(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, Snippet)


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


def test_in_memory_repo_toggle_favorite(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    im_repo.toggle_favorite(stored_snippet.id)
    updated_snippet = im_repo.get(stored_snippet.id)
    assert updated_snippet.favorite is True
    im_repo.toggle_favorite(stored_snippet.id)
    updated_snippet = im_repo.get(stored_snippet.id)
    assert updated_snippet.favorite is False
    with pytest.raises(SnippetNotFoundError):
        im_repo.toggle_favorite(9999)


def test_in_memory_repo_add_tag(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    im_repo.add_tag(stored_snippet.id, "foo")
    assert "foo" in im_repo.get(stored_snippet.id).tags
    im_repo.add_tag(stored_snippet.id, "bar")
    assert "bar" in im_repo.get(stored_snippet.id).tags
    with pytest.raises(SnippetNotFoundError):
        im_repo.add_tag(9999, "test")


def test_in_memory_repo_remove_tag(snippet, im_repo):
    stored_snippet = im_repo.add(snippet)
    im_repo.add_tag(stored_snippet.id, "test-tag")
    im_repo.remove_tag(stored_snippet.id, "test-tag")
    assert "test-tag" not in im_repo.get(stored_snippet.id).tags
    with pytest.raises(ValueError):
        im_repo.remove_tag(stored_snippet.id, "non-existent-tag")
    with pytest.raises(SnippetNotFoundError):
        im_repo.remove_tag(9999, "test-tag")


def test_in_memory_repo_search(im_repo):
    add_search_data(im_repo)
    assert len(im_repo.search("foo")) == 3
    assert len(im_repo.search("bar")) == 1
    assert len(im_repo.search("baz")) == 1
    assert len(im_repo.search("zap")) == 0


# =============================================================================
# DatabaseBackedSnippetRepo Tests
# =============================================================================


def test_db_repo_add(db_repo, snippet):
    stored_snippet = db_repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, Snippet)


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


def test_db_repo_toggle_favorite(snippet, db_repo):
    stored_snippet = db_repo.add(snippet)
    db_repo.toggle_favorite(stored_snippet.id)
    updated_snippet = db_repo.get(stored_snippet.id)
    assert updated_snippet.favorite is True
    db_repo.toggle_favorite(stored_snippet.id)
    updated_snippet = db_repo.get(stored_snippet.id)
    assert updated_snippet.favorite is False
    with pytest.raises(SnippetNotFoundError):
        db_repo.toggle_favorite(9999)


def test_db_repo_add_tag(snippet, db_repo):
    stored_snippet = db_repo.add(snippet)
    db_repo.add_tag(stored_snippet.id, "foo")
    assert "foo" in db_repo.get(stored_snippet.id).tags
    db_repo.add_tag(stored_snippet.id, "bar")
    assert "bar" in db_repo.get(stored_snippet.id).tags
    with pytest.raises(SnippetNotFoundError):
        db_repo.add_tag(9999, "test")


def test_db_repo_remove_tag(snippet, db_repo):
    stored_snippet = db_repo.add(snippet)
    db_repo.add_tag(stored_snippet.id, "test-tag")
    db_repo.remove_tag(stored_snippet.id, "test-tag")
    assert "test-tag" not in db_repo.get(stored_snippet.id).tags
    with pytest.raises(ValueError):
        db_repo.remove_tag(stored_snippet.id, "non-existent-tag")
    with pytest.raises(SnippetNotFoundError):
        db_repo.remove_tag(9999, "test-tag")


def test_db_repo_search(db_repo):
    add_search_data(db_repo)
    assert len(db_repo.search("bar")) == 1
    assert len(db_repo.search("baz")) == 1
    assert len(db_repo.search("zap")) == 0
    assert len(db_repo.search("foo")) == 3
