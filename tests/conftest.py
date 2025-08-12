from typing import Generator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from src.snipster.db import SessionFactory
from src.snipster.models import Language, SnippetCreate
from src.snipster.repo import DatabaseBackedSnippetRepo, InMemorySnippetRepo

# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def test_session_factory():
    """Provide a SessionFactory with in-memory SQLite for tests."""
    test_engine = create_engine(
        "sqlite://",
        # This allows multiple threads to use the same connection
        # otherwise you'll get an error:
        # "SQLite objects created in a thread can only be used in that same thread"
        connect_args={"check_same_thread": False},
        # StaticPool maintains a single connection shared by all threads to avoid
        # "database is locked" errors with in-memory SQLite
        poolclass=StaticPool,
        # Disable SQL query logging to keep test output clean
        echo=False,
    )
    SQLModel.metadata.create_all(test_engine)
    factory = SessionFactory(test_engine)

    yield factory

    factory.close_all_sessions()
    test_engine.dispose()


@pytest.fixture(scope="function")
def get_test_session(test_session_factory):
    """Provide a database session for tests that use SessionFactory."""
    with test_session_factory.get_session() as session:
        # Without `yield` the with block would end immediately
        # and session.commit() and session.close() would get called
        # This allows the test to finish before closing the with block and
        # then triggering teardown in the SessionFactory.get_session() method
        yield session


# =============================================================================
# Repository Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def im_repo() -> InMemorySnippetRepo:
    """Provide an in-memory repository for testing."""
    return InMemorySnippetRepo()


@pytest.fixture(scope="function")
def db_repo(test_session_factory) -> Generator[DatabaseBackedSnippetRepo, None, None]:
    """Provide a database-backed repository for testing."""
    with test_session_factory.get_session() as session:
        # The yield statement here is important for two reasons:
        # 1. It allows the test to use the repo before the session is closed
        # 2. When the test finishes, execution returns here and continues into
        #    the SessionFactory.get_session() context manager's finally block,
        #    which properly closes the session
        yield DatabaseBackedSnippetRepo(session=session)


@pytest.fixture(params=["im_repo", "db_repo"])
def repo(request, im_repo, db_repo):
    """
    Parametrized fixture that provides both repository types for testing.
    The two params serve as flags for different test runs.
    """
    if request.param == "im_repo":
        return im_repo
    elif request.param == "db_repo":
        return db_repo


# =============================================================================
# Snippet Fixtures
# =============================================================================


@pytest.fixture
def snippet() -> SnippetCreate:
    """Provide a basic Python snippet for testing."""
    return SnippetCreate(
        title="My Snippet", code="print('stuff')", language=Language.python
    )


@pytest.fixture
def another_snippet() -> SnippetCreate:
    """Provide a basic JavaScript snippet for testing."""
    return SnippetCreate(
        title="My Snippet", code="console.log('stuff')", language=Language.javascript
    )


@pytest.fixture
def sample_snippets():
    """Define sample snippet data for tests."""
    return [
        {
            "title": "Hello World",
            "code": "print('Hello, world!')",
            "language": "python",
            "description": "Classic first program",
            "tags": ["beginner", "basics"],
            "favorite": False,
        },
        {
            "title": "Array Map",
            "code": "const doubled = arr.map(x => x * 2)",
            "language": "javascript",
            "description": "Double array values",
            "tags": ["array", "functional"],
            "favorite": True,
        },
        {
            "title": "Hello Rust",
            "code": 'fn main() { println!("Hello, Rust!"); }',
            "language": "rust",
            "description": "Basic Rust program",
            "tags": ["beginner"],
            "favorite": False,
        },
    ]


# =============================================================================
# Helper Functions
# =============================================================================


def add_search_data(repo):
    """Add test data for search functionality testing."""
    snippet1 = SnippetCreate(
        title="Foo",
        code="print('foo')",
        description="This is a foo snippet",
        language=Language.python,
    )
    repo.add(snippet=snippet1)

    snippet2 = SnippetCreate(
        title="Bar",
        code="print('bar')",
        description="This is a bar snippet",
        language=Language.python,
    )
    repo.add(snippet=snippet2)

    snippet3 = SnippetCreate(
        title="Baz",
        code="print('baz')",
        description="This is a baz snippet",
        language=Language.python,
    )
    repo.add(snippet=snippet3)

    snippet4 = SnippetCreate(
        title="Super Foo",
        code="print('foo foo foo')",
        description="This is a foo snippet but even more so",
        language=Language.python,
    )
    repo.add(snippet=snippet4)

    snippet5 = SnippetCreate(
        title="Blah",
        code="print('blah blah blah')",
        description="This is a blah snippet",
        language=Language.python,
        tags=["foo"],
    )
    repo.add(snippet=snippet5)
