from typing import Generator

import pytest
from sqlmodel import SQLModel, create_engine
from testcontainers.postgres import PostgresContainer

from src.snipster.db import SessionFactory
from src.snipster.models import Language, SnippetCreate
from src.snipster.repo import DatabaseBackedSnippetRepo, InMemorySnippetRepo

# =============================================================================
# Database Fixtures
# =============================================================================


# Spins up Postgres once per module
@pytest.fixture(scope="module")
def postgres_container():
    """Spin up a PostgreSQL container for testing."""
    # Note: We set `driver=None` in the PostgresContainer so that
    # `get_connection_url()` returns a plain `postgresql://...` string
    # (without assuming psycopg2). Then we call `.replace("postgresql://",
    # "postgresql+psycopg://")` so SQLAlchemy uses psycopg3 explicitly. See below.
    postgres = PostgresContainer("postgres:14", driver=None)
    postgres.start()
    try:
        yield postgres
    finally:
        postgres.stop()


@pytest.fixture(scope="function")
def test_session_factory(postgres_container):
    """Provide a SessionFactory with a PostgreSQL database for tests."""
    # See above note about `driver=None` in `postgres_container` fixture.
    url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+psycopg://"
    )
    test_engine = create_engine(
        url,
        future=True,
        pool_pre_ping=True,
    )

    SQLModel.metadata.create_all(test_engine)

    # A SessionFactory here is our wrapper around SQLAlchemy's sessionmaker—
    # it produces new DB sessions tied to the same engine, so each test can
    # work with a clean, properly configured session.
    factory = SessionFactory(test_engine)

    yield factory

    # Clean up the database after each test
    SQLModel.metadata.drop_all(test_engine)
    # Close all sessions and dispose of the engine
    factory.close_all_sessions()
    # Dispose of the engine
    # This is important to do after all tests have finished
    # to avoid resource leaks
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
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return [
        {
            "title": "Hello World",
            "code": "print('Hello, world!')",
            "language": "python",
            "description": "Classic first program",
            "tags": [f"beginner-{unique_id}", f"basics-{unique_id}"],
            "favorite": False,
        },
        {
            "title": "Array Map",
            "code": "const doubled = arr.map(x => x * 2)",
            "language": "javascript",
            "description": "Double array values",
            "tags": [f"array-{unique_id}", f"functional-{unique_id}"],
            "favorite": True,
        },
        {
            "title": "Hello Rust",
            "code": 'fn main() { println!("Hello, Rust!"); }',
            "language": "rust",
            "description": "Basic Rust program",
            "tags": [f"beginner-rust-{unique_id}"],
            "favorite": False,
        },
    ]


@pytest.fixture
def sample_snippets_for_testing_search():
    """Define sample snippet data for testing search functionality."""
    return [
        {
            "title": "Foo",
            "code": "print('foo')",
            "language": "python",
            "description": "This is a foo snippet",
            "tags": [],
            "favorite": False,
        },
        {
            "title": "Bar",
            "code": "print('bar')",
            "language": "python",
            "description": "This is a bar snippet",
            "tags": [],
            "favorite": False,
        },
        {
            "title": "Baz",
            "code": "print('baz')",
            "language": "python",
            "description": "This is a baz snippet",
            "tags": [],
            "favorite": False,
        },
        {
            "title": "Super Foo",
            "code": "print('foo foo foo')",
            "language": "python",
            "description": "This is a foo snippet but even more so",
            "tags": [],
            "favorite": False,
        },
        {
            "title": "Blah",
            "code": "print('blah blah blah')",
            "language": "python",
            "description": "This is a blah snippet",
            "tags": ["foo"],
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
    )
    stored_snippet5 = repo.add(snippet=snippet5)
    repo.add_tag(stored_snippet5.id, "foo")
