import pytest

from src.snipster.exceptions import SnippetNotFoundError
from src.snipster.models import Language, Snippet, SnippetCreate

from .conftest import add_search_data

# =============================================================================
# Repo Tests
# =============================================================================


def test_repo_add(snippet, repo):
    # This test is incorrectly named - it's testing both in-memory and DB repos
    # due to the parametrize decorator above
    stored_snippet = repo.add(snippet)
    assert stored_snippet.id is not None
    assert stored_snippet.title == snippet.title
    assert stored_snippet.code == snippet.code
    assert stored_snippet.language == snippet.language
    assert isinstance(stored_snippet, Snippet)


def test_repo_get(snippet, repo):
    stored_snippet = repo.add(snippet)
    retrieved = repo.get(stored_snippet.id)
    assert retrieved is not None
    assert retrieved.id == stored_snippet.id
    assert retrieved.title == snippet.title
    assert retrieved.code == snippet.code
    assert retrieved.language == snippet.language
    with pytest.raises(SnippetNotFoundError):
        repo.get(9999)


def test_repo_list(snippet, another_snippet, repo):
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


def test_repo_delete(snippet, repo):
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


def test_repo_toggle_favorite(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.toggle_favorite(stored_snippet.id)
    updated_snippet = repo.get(stored_snippet.id)
    assert updated_snippet.favorite is True
    repo.toggle_favorite(stored_snippet.id)
    updated_snippet = repo.get(stored_snippet.id)
    assert updated_snippet.favorite is False
    with pytest.raises(SnippetNotFoundError):
        repo.toggle_favorite(9999)


def test_repo_add_tag(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.add_tag(stored_snippet.id, "foo")
    assert "foo" in repo.get(stored_snippet.id).tags
    repo.add_tag(stored_snippet.id, "bar")
    assert "bar" in repo.get(stored_snippet.id).tags
    with pytest.raises(SnippetNotFoundError):
        repo.add_tag(9999, "test")


def test_repo_remove_tag(snippet, repo):
    stored_snippet = repo.add(snippet)
    repo.add_tag(stored_snippet.id, "test-tag")
    repo.remove_tag(stored_snippet.id, "test-tag")
    assert "test-tag" not in repo.get(stored_snippet.id).tags
    with pytest.raises(ValueError):
        repo.remove_tag(stored_snippet.id, "non-existent-tag")
    with pytest.raises(SnippetNotFoundError):
        repo.remove_tag(9999, "test-tag")


def test_repo_search(repo):
    add_search_data(repo)
    assert len(repo.search("foo")) == 3
    assert len(repo.search("bar")) == 1
    assert len(repo.search("baz")) == 1
    assert len(repo.search("zap")) == 0


def test_repo_fuzzy_search(repo):
    # Test exact match
    snippet1 = SnippetCreate(
        title="Hello World",
        code="print('Hello World')",
        description="A simple greeting",
        language=Language.PYTHON,
    )
    repo.add(snippet1)
    results = repo.fuzzy_search("Hello World")
    assert len(results) == 1
    assert results[0].title == "Hello World"

    # Test close match with typo
    snippet2 = SnippetCreate(
        title="Calculate Average",
        code="def avg(x, y): return (x + y) / 2",
        description="Calculate average of two numbers",
        language=Language.PYTHON,
    )
    repo.add(snippet2)
    results = repo.fuzzy_search("Calculate Averge")  # Intentional typo
    assert len(results) == 1
    assert results[0].title == "Calculate Average"

    # Test partial match
    snippet3 = SnippetCreate(
        title="Parse JSON String",
        code="json.loads(str)",
        description="Parse JSON",
        language=Language.PYTHON,
    )
    repo.add(snippet3)
    results = repo.fuzzy_search("JSON")
    assert len(results) == 1
    assert results[0].title == "Parse JSON String"

    # Test no match below threshold
    results = repo.fuzzy_search("Something Completely Different")
    assert len(results) == 0
