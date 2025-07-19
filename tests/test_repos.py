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


def add_fuzzy_search_test_data(repo):
    """
    Populates repository with diverse test data for fuzzy search testing.
    Includes various patterns to test different fuzzy matching scenarios.
    """

    # Basic exact matches
    snippet1 = SnippetCreate(
        title="Hello World",
        code="print('Hello, World!')",
        description="Basic hello world example",
        language=Language.PYTHON,
    )
    repo.add(snippet=snippet1)

    # Partial word matching
    snippet2 = SnippetCreate(
        title="Authentication Helper",
        code="def authenticate_user(username, password):\n    return True",
        description="Helper function for user authentication",
        language=Language.PYTHON,
        tags=["auth", "security"],
    )
    repo.add(snippet=snippet2)

    # Typo-tolerant matches
    snippet3 = SnippetCreate(
        title="Database Connection",
        code="import sqlite3\nconn = sqlite3.connect('db.sqlite')",
        description="Connect to SQLite database",
        language=Language.PYTHON,
        tags=["database", "sqlite"],
    )
    repo.add(snippet=snippet3)

    # Acronym matching
    snippet4 = SnippetCreate(
        title="HTTP Request Handler",
        code="import requests\nresponse = requests.get('https://api.example.com')",
        description="Make HTTP requests using requests library",
        language=Language.PYTHON,
        tags=["http", "api", "requests"],
    )
    repo.add(snippet=snippet4)

    # Multi-word fuzzy matching
    snippet5 = SnippetCreate(
        title="File System Operations",
        code="import os\nos.listdir('/path/to/directory')",
        description="List files in directory",
        language=Language.PYTHON,
        tags=["filesystem", "files"],
    )
    repo.add(snippet=snippet5)

    # Similar titles for ranking tests
    snippet6 = SnippetCreate(
        title="JSON Parser",
        code="import json\ndata = json.loads(json_string)",
        description="Parse JSON string into Python object",
        language=Language.PYTHON,
        tags=["json", "parsing"],
    )
    repo.add(snippet=snippet6)

    snippet7 = SnippetCreate(
        title="JSON Generator",
        code="import json\njson_string = json.dumps(data)",
        description="Convert Python object to JSON string",
        language=Language.PYTHON,
        tags=["json", "serialization"],
    )
    repo.add(snippet=snippet7)

    # Different languages for language-specific search
    snippet8 = SnippetCreate(
        title="Hello World JS",
        code="console.log('Hello, World!');",
        description="Basic hello world in JavaScript",
        language=Language.JAVASCRIPT,
        tags=["basic"],
    )
    repo.add(snippet=snippet8)

    # Long descriptions for content matching
    snippet9 = SnippetCreate(
        title="Data Validator",
        code="def validate_email(email):\n    import re\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None",
        description="Comprehensive email validation function using regular expressions to check email format compliance with RFC standards",
        language=Language.PYTHON,
        tags=["validation", "email", "regex"],
    )
    repo.add(snippet=snippet9)

    # Edge cases for fuzzy matching
    snippet10 = SnippetCreate(
        title="Cache Manager",
        code="class CacheManager:\n    def __init__(self):\n        self.cache = {}\n    \n    def get(self, key):\n        return self.cache.get(key)\n    \n    def set(self, key, value):\n        self.cache[key] = value",
        description="Simple in-memory cache implementation for storing key-value pairs",
        language=Language.PYTHON,
        tags=["cache", "memory", "storage"],
    )
    repo.add(snippet=snippet10)

    # Common misspellings test cases
    snippet11 = SnippetCreate(
        title="Configuration Loader",
        code="import configparser\nconfig = configparser.ConfigParser()\nconfig.read('config.ini')",
        description="Load application configuration from INI file",
        language=Language.PYTHON,
        tags=["config", "ini", "settings"],
    )
    repo.add(snippet=snippet11)

    # Substring and partial matches
    snippet12 = SnippetCreate(
        title="String Utilities",
        code="def capitalize_words(text):\n    return ' '.join(word.capitalize() for word in text.split())",
        description="Utility functions for string manipulation and formatting",
        language=Language.PYTHON,
        tags=["string", "text", "utility"],
    )
    repo.add(snippet=snippet12)

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
