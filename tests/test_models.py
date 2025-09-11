import pytest

from src.snipster.models import Language, Snippet, Tag, TagCreate


def test_saving_snippet_to_database(get_test_session):
    snippet = Snippet(
        title="Test Snippet",
        code="print('foo')",
        language=Language.python,
    )
    with get_test_session as session:
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
            language=Language.python,
        )
    assert "Code must be at least 3 characters." in str(exception.value)

    with pytest.raises(ValueError) as exception:
        Snippet.create_snippet(
            title="_",
            code="print('foo')",
            language=Language.python,
        )
    assert "Title must be at least 3 characters." in str(exception.value)


def test_saving_tag_to_database(get_test_session):
    with get_test_session as session:
        tag = Tag(name="test-tag")
        session.add(tag)
        session.commit()
        session.refresh(tag)

    assert tag.name == "test-tag"
    assert tag.id is not None


def test_tag_creation_validation():
    # Test tag name length validation
    with pytest.raises(ValueError) as exception:
        TagCreate(name="")  # Too short
    assert "String should have at least 1 character" in str(exception.value)

    with pytest.raises(ValueError) as exception:
        TagCreate(name="a" * 51)  # Too long
    assert "String should have at most 50 characters" in str(exception.value)

    # Test valid tag creation
    tag = TagCreate(name="test-tag")
    assert tag.name == "test-tag"

    # Test whitespace stripping
    tag = TagCreate(name="  hello  ")
    assert tag.name == "hello"

    # Test case normalization
    tag = TagCreate(name="HELLO")
    assert tag.name == "hello"

    # Test combined normalization
    tag = TagCreate(name="  Hello World  ")
    assert tag.name == "hello world"

    # Test special characters preserved
    tag = TagCreate(name="  Test-Tag_123  ")
    assert tag.name == "test-tag_123"
