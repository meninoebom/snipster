import pytest

from src.snipster.exceptions import SnippetNotFoundError
from src.snipster.models import Language, SnippetCreate, SnippetPublic
from src.snipster.repo import InMemorySnippetRepo


@pytest.fixture
def snippet() -> SnippetCreate:
    return SnippetCreate(
        title="My Snippet", code="print('stuff')", language=Language.PYTHON
    )


@pytest.fixture
def another_snippet() -> SnippetCreate:
    return SnippetCreate(
        title="My Snippet", code="print('stuff')", language=Language.PYTHON
    )


@pytest.fixture(scope="function")
def repo() -> InMemorySnippetRepo:
    return InMemorySnippetRepo()


def test_in_memory_repo_add(snippet, repo):
    stored_snippet = repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, SnippetPublic)


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
