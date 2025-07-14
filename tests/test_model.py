import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.models import Language, SnippetCreate, SnippetORM

# TODO: Is this missing tests for SnippetPublic?
# TODO: Should this be called test_models.py?


@pytest.fixture(scope="function")
def get_session():
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_create_snippet(get_session):
    snippet = SnippetORM(
        title="Test Snippet",
        code="print('foo')",
        language=Language.PYTHON,
    )
    with get_session as session:
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
    assert snippet.title == "Test Snippet"
    assert snippet.code == "print('foo')"


def test_snippet_validation():
    with pytest.raises(ValueError) as exception:
        SnippetCreate(
            title="Test Snippet",
            code="_",
            language=Language.PYTHON,
        )
    assert "Code must be at least 3 characters." in str(exception.value)

    with pytest.raises(ValueError) as exception:
        SnippetCreate(
            title="_",
            code="print('foo')",
            language=Language.PYTHON,
        )
    assert "Title must be at least 3 characters." in str(exception.value)
