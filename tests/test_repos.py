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


@pytest.fixture(params=["im_repo", "db_repo"])
def repo(request, im_repo, db_repo):
    if request.param == "im_repo":
        return im_repo
    elif request.param == "db_repo":
        return db_repo


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
# Repo Tests
# =============================================================================


def test_in_memory_repo_add(snippet, repo):
    # This test is incorrectly named - it's testing both in-memory and DB repos
    # due to the parametrize decorator above
    stored_snippet = repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, Snippet)


def test_in_memory_repo_get(snippet, repo):
    stored_snippet = repo.add(snippet)
    retrieved = repo.get(stored_snippet.id)
    assert retrieved is not None
    assert retrieved.id == stored_snippet.id
    assert retrieved.title == snippet.title
    assert retrieved.code == snippet.code
    assert retrieved.language == snippet.language
    with pytest.raises(SnippetNotFoundError):
        repo.get(9999)


def test_in_memory_repo_list(snippet, another_snippet, repo):
    repo.add(snippet)
    list = repo.list()
    assert len(list) == 1
    stored_snippet = list[0]
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    repo.add(another_snippet)
    list = repo.list()
    assert len(list) == 2


def test_in_memory_repo_delete(snippet, repo):
    repo.add(snippet)
    list = repo.list()
    stored_snippet = list[0]
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    repo.delete(stored_snippet.id)
    with pytest.raises(SnippetNotFoundError):
        repo.get(stored_snippet.id)


def test_in_memory_repo_toggle_favorite(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.toggle_favorite(stored_snippet.id)
    updated_snippet = repo.get(stored_snippet.id)
    assert updated_snippet.favorite is True
    repo.toggle_favorite(stored_snippet.id)
    updated_snippet = repo.get(stored_snippet.id)
    assert updated_snippet.favorite is False
    with pytest.raises(SnippetNotFoundError):
        repo.toggle_favorite(9999)


def test_in_memory_repo_add_tag(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.add_tag(stored_snippet.id, "foo")
    assert "foo" in repo.get(stored_snippet.id).tags
    repo.add_tag(stored_snippet.id, "bar")
    assert "bar" in repo.get(stored_snippet.id).tags
    with pytest.raises(SnippetNotFoundError):
        repo.add_tag(9999, "test")


def test_in_memory_repo_remove_tag(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.add_tag(stored_snippet.id, "test-tag")
    repo.remove_tag(stored_snippet.id, "test-tag")
    assert "test-tag" not in repo.get(stored_snippet.id).tags
    with pytest.raises(ValueError):
        repo.remove_tag(stored_snippet.id, "non-existent-tag")
    with pytest.raises(SnippetNotFoundError):
        repo.remove_tag(9999, "test-tag")


def test_in_memory_repo_search(repo):
    add_search_data(repo)
    assert len(repo.search("foo")) == 3
    assert len(repo.search("bar")) == 1
    assert len(repo.search("baz")) == 1
    assert len(repo.search("zap")) == 0
