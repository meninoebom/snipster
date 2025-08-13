import pytest
from fastapi.testclient import TestClient

from src.snipster.api import app, get_session
from src.snipster.models import SnippetCreate


@pytest.fixture(autouse=True)
def override_db(get_test_session):
    app.dependency_overrides[get_session] = lambda: get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_db(db_repo, sample_snippets):
    """
    Database with sample snippets already inserted.
    We can use db_repo fixture here bc it relies on the
    test_session_factory that use the Sqlite engine
    """
    # Create and add snippets
    for snippet_data in sample_snippets:
        snippet = SnippetCreate(**snippet_data)
        db_repo.add(snippet)


@pytest.fixture(scope="function")
def client():
    """
    This fixture creates a new TestClient instance for each test function
    preventing any state or side effects from previous tests
    from affecting the current test (isolation and reliability)
    """
    with TestClient(app) as client:
        yield client


# =============================================================================
# POST /create
# =============================================================================


def test_create_snippet(client):
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


def test_create_snippet_short_title(client):
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


def test_create_snippet_short_code(client):
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


def test_create_snippet_missing_title(client):
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


def test_create_snippet_missing_code(client):
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


def test_create_snippet_missing_language(client):
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


def test_create_snippet_invalid_language(client):
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


# =============================================================================
# GET /snippets
# =============================================================================


@pytest.mark.usefixtures("seed_db")
def test_list_snippets(client):
    """Test that the /snippets endpoint returns all snippets with correct structure."""
    response = client.get("/snippets")

    # Check response status and structure
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0

    hello_world_snippet = next((s for s in body if s["title"] == "Hello World"), None)
    assert hello_world_snippet is not None, "Hello World snippet not found in response"
    assert hello_world_snippet["title"] == "Hello World"
    assert hello_world_snippet["code"] == "print('Hello, world!')"
    assert hello_world_snippet["description"] == "Classic first program"
    assert hello_world_snippet["language"] == "python"
    assert hello_world_snippet["tags"] == ["beginner", "basics"]
    assert hello_world_snippet["favorite"] is False

    for snippet in body:
        assert "id" in snippet
        assert "title" in snippet
        assert "code" in snippet
        assert "language" in snippet
        assert "created_at" in snippet
        assert "updated_at" in snippet
        assert "favorite" in snippet
        assert "tags" in snippet
        assert "description" in snippet
        assert snippet["language"] in ["javascript", "python", "rust"]
        assert len(snippet["title"]) >= 3
        assert len(snippet["code"]) >= 3


# =============================================================================
# GET /snippets/{id}
# =============================================================================


@pytest.mark.usefixtures("seed_db")
def test_get_snippet(snippet, db_repo, client):
    created_snippet = db_repo.add(snippet)
    response = client.get(f"/snippets/{created_snippet.id}")
    body = response.json()

    assert response.status_code == 200
    assert body["title"] == snippet.title
    assert body["code"] == snippet.code
    assert body["language"] == snippet.language
    assert body["description"] == snippet.description


def test_get_snippet_invalid_id(client):
    response = client.get("/snippets/foo")

    assert response.status_code == 422

    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["type"] == "int_parsing"
    assert detail[0]["loc"] == ["path", "snippet_id"]
    assert "valid integer" in detail[0]["msg"]


def test_get_snippet_missing_id(client):
    response = client.get("/snippets/0")

    assert response.status_code == 404

    detail = response.json()["detail"]
    assert detail == "Snippet with id 0 not found"


# =============================================================================
# DELETE /snippets/{id}
# =============================================================================


@pytest.mark.usefixtures("seed_db")
def test_delete_snippet(snippet, db_repo, client):
    created_snippet = db_repo.add(snippet)
    response = client.delete(f"/snippets/{created_snippet.id}")

    assert response.status_code == 204


def test_delete_snippet_invalid_id(client):
    response = client.delete("/snippets/foo")

    assert response.status_code == 422

    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["type"] == "int_parsing"
    assert detail[0]["loc"] == ["path", "snippet_id"]
    assert "valid integer" in detail[0]["msg"]


def test_delete_snippet_missing_id(client):
    response = client.delete("/snippets/0")

    assert response.status_code == 404

    detail = response.json()["detail"]
    assert detail == "Snippet with id 0 not found"


# =============================================================================
# POST /snippets/{id}/toggle-favorite
# =============================================================================


def test_toggle_favorite(snippet, db_repo, client):
    created_snippet = db_repo.add(snippet)
    assert created_snippet.favorite is False

    response = client.post(f"/snippets/{created_snippet.id}/toggle-favorite")
    assert response.status_code == 200

    body = response.json()
    assert body["favorite"] is True

    updated_snippet_response = client.get(f"/snippets/{body["id"]}")
    updated_snippet_dict = updated_snippet_response.json()
    assert updated_snippet_dict["favorite"] is True

    response = client.post(f"/snippets/{created_snippet.id}/toggle-favorite")
    assert response.status_code == 200

    updated_snippet_response = client.get(f"/snippets/{body["id"]}")
    updated_snippet_dict = updated_snippet_response.json()
    assert updated_snippet_dict["favorite"] is False


def test_toggle_favorite_snippet_invalid_id(client):
    response = client.post("/snippets/foo/toggle-favorite")

    assert response.status_code == 422

    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["type"] == "int_parsing"
    assert detail[0]["loc"] == ["path", "snippet_id"]
    assert "valid integer" in detail[0]["msg"]


def test_toggle_favorite_snippet_missing_id(client):
    response = client.post("/snippets/0/toggle-favorite")

    assert response.status_code == 404

    detail = response.json()["detail"]
    assert detail == "Snippet with id 0 not found"
