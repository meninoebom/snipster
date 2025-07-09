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
    # do something
    snippet = Snippet(title="Test Snippet", code="print('foo')")
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
    # hardcode expected results
    # check the result with assert
    assert snippet.id is not None
    assert snippet.title == "Test Snippet"
    assert snippet.code == "print('foo')"
