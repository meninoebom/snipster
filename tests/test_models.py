import pytest

from src.snipster.models import Language, Snippet


def test_saving_snippet_to_database(get_session):
    snippet = Snippet(
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
    assert snippet.id is not None


def test_create_snippet_method_validation():
    with pytest.raises(ValueError) as exception:
        Snippet.create_snippet(
            title="Test Snippet",
            code="_",
            language=Language.PYTHON,
        )
    assert "Code must be at least 3 characters." in str(exception.value)

    with pytest.raises(ValueError) as exception:
        Snippet.create_snippet(
            title="_",
            code="print('foo')",
            language=Language.PYTHON,
        )
    assert "Title must be at least 3 characters." in str(exception.value)
