import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.snipster.models import Snippet

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)
    # SQLite gives us clean up for free
    # yield
    # SQLModel.metadata.drop_all(engine)


def test_create_snippet():
    snippet = Snippet(title="Test Snippet", code="print('foo')")
    with Session(engine) as session:
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
    assert snippet.id is not None
    assert snippet.title == "Test Snippet"
    assert snippet.code == "print('foo')"


def test_create_snippet_with_from_dict_cls_method():
    snippet_dict = {"title": "Amazing Snippet", "code": "print('Be amazed!')"}
    snippet = Snippet.from_dict(snippet_dict)
    with Session(engine) as session:
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
        assert snippet.id is not None
        assert snippet.title == "Amazing Snippet"
        assert snippet.code == "print('Be amazed!')"
