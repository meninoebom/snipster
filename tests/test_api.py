import pytest
from fastapi.testclient import TestClient

from src.snipster.api import app, get_repo
from src.snipster.models import SnippetCreate
from src.snipster.repo import InMemorySnippetRepo

client = TestClient(app)


def get_test_repo():
    return InMemorySnippetRepo()


app.dependency_overrides[get_repo] = get_test_repo


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


def test_create_snippet():
    response = client.post(
        "/create",
        json={
            "title": "Test",
            "code": "console.log('foo')",
            "description": "Blah blah blah",
            "language": "javascript",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Test"
    assert payload["code"] == "console.log('foo')"
    assert payload["description"] == "Blah blah blah"
    assert payload["language"] == "javascript"


def test_create_snippet_short_title():
    """
    Example 422 response body
    {
    "detail": [
        {
        "loc": ["body", "title"],
        "msg": "String should have at least 3 characters",
        "type": "string_too_short"
        }
    ]
    }
    """
    response = client.post(
        "/create",
        json={
            "title": "T",
            "code": "console.log('foo')",
            "description": "Blah blah blah",
            "language": "javascript",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "title"), None)
    assert error is not None
    assert error["msg"] == "String should have at least 3 characters"
    assert error["type"] == "string_too_short"


def test_create_snippet_short_code():
    response = client.post(
        "/create",
        json={
            "title": "Test Title",
            "code": "ab",
            "description": "Blah blah blah",
            "language": "javascript",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "code"), None)
    assert error is not None
    assert error["msg"] == "String should have at least 3 characters"
    assert error["type"] == "string_too_short"


def test_create_snippet_missing_title():
    response = client.post(
        "/create",
        json={
            "code": "console.log('foo')",
            "description": "Blah blah blah",
            "language": "javascript",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "title"), None)
    assert error is not None
    assert error["type"] == "missing"


def test_create_snippet_missing_code():
    response = client.post(
        "/create",
        json={
            "title": "Test Title",
            "description": "Blah blah blah",
            "language": "javascript",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "code"), None)
    assert error is not None
    assert error["type"] == "missing"


def test_create_snippet_missing_language():
    response = client.post(
        "/create",
        json={
            "title": "Test Title",
            "code": "console.log('foo')",
            "description": "Blah blah blah",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "language"), None)
    assert error is not None
    assert error["type"] == "missing"


def test_create_snippet_invalid_language():
    response = client.post(
        "/create",
        json={
            "title": "Test Title",
            "code": "console.log('foo')",
            "description": "Blah blah blah",
            "language": "invalid_language",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    error = next((e for e in body["detail"] if e["loc"][-1] == "language"), None)
    assert error is not None
    assert error["type"] == "enum"
