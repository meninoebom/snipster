from typing import Generator

import pytest
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
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(test_engine)
    factory = SessionFactory(test_engine)

    yield factory

    factory.close_all_sessions()
    test_engine.dispose()


@pytest.fixture(scope="function")
def get_session(test_session_factory):
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
        # yield here to allow the SessionFactory teardown code to run (still grokking this)
        yield DatabaseBackedSnippetRepo(session=session)


@pytest.fixture(params=["im_repo", "db_repo"])
def repo(request, im_repo, db_repo):
    """Parametrized fixture that provides both repository types for testing."""
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
        title="My Snippet", code="print('stuff')", language=Language.PYTHON
    )


@pytest.fixture
def another_snippet() -> SnippetCreate:
    """Provide a basic JavaScript snippet for testing."""
    return SnippetCreate(
        title="My Snippet", code="console.log('stuff')", language=Language.JAVASCRIPT
    )


# =============================================================================
# Helper Functions
# =============================================================================


def add_search_data(repo):
    """Add test data for search functionality testing."""
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
