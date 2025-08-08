import pytest

from src.snipster.api import create_snippet
from src.snipster.models import SnippetCreate


@pytest.fixture
def invalid_snippet_factory():
    def _create_invalid_snippet(
        title=None, code=None, description=None, language=None, **kwargs
    ):
        data = {
            "title": title or "Fake Title",
            "code": code or "print('test')",
            "language": language or "python",
            "description": description or None,
            **kwargs,
        }
        return SnippetCreate(**data)

    return _create_invalid_snippet


def test_create_snippet(snippet, repo):
    response = create_snippet(snippet=snippet, repo=repo)
    assert response is not None
    assert response.title == snippet.title
    assert response.code == snippet.code
    assert response.language == snippet.language
