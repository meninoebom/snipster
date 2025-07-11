import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.models import SnippetCreate, SnippetORM

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)


def test_create_snippet():
    snippet = SnippetORM(title="Test Snippet", code="print('foo')")
    with Session(engine) as session:
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
    assert snippet.title == "Test Snippet"
    assert snippet.code == "print('foo')"


def test_snippet_validation():
    with pytest.raises(ValueError) as exception:
        SnippetCreate(title="Test Snippet", code="_")
    assert "Code must be at least 3 characters." in str(exception.value)

    with pytest.raises(ValueError) as exception:
        SnippetCreate(title="_", code="print('foo')")
    assert "Title must be at least 3 characters." in str(exception.value)
