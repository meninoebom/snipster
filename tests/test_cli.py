import pytest
from typer.testing import CliRunner

import src.snipster.cli as cli_module

app = cli_module.app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_db(test_session_factory):
    """Fixture to temporarily replace the CLI's session factory with a test one.

    This fixture runs automatically before each test and:
    1. Stores the original session factory
    2. Replaces it with a test session factory that uses an in-memory SQLite database
    3. Yields control to the test
    4. Restores the original session factory after the test completes

    Args:
        test_session_factory: A SessionFactory fixture that provides an in-memory database
    """
    original = cli_module.cli_session_factory
    cli_module.cli_session_factory = test_session_factory
    yield
    cli_module.cli_session_factory = original


def test_add_snippet():
    result = runner.invoke(
        app, ["add", "--title", "Test", "--code", "print('hi')", "--language", "python"]
    )
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.stdout}")
    print(f"Error: {result.stderr}")
    assert result.exit_code == 0

    # Try to list snippets to see what's in the database
    list_result = runner.invoke(app, ["list"])
    print(f"List exit code: {list_result.exit_code}")
    print(f"List output: {list_result.stdout}")
    print(f"List error: {list_result.stderr}")


def test_language_debug():
    """Debug the language input issue."""
    print("Testing language input...")

    # Test with explicit language
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Debug Test",
            "--code",
            "print('debug')",
            "--language",
            "python",
        ],
    )
    print(f"Language debug - Exit code: {result.exit_code}")
    print(f"Language debug - Output: {result.stdout}")
    print(f"Language debug - Error: {result.stderr}")

    # Test without language (should prompt)
    result2 = runner.invoke(
        app,
        ["add", "--title", "Debug Test 2", "--code", "print('debug2')"],
        input="python\n",
    )  # Provide input for the prompt
    print(f"Language debug 2 - Exit code: {result2.exit_code}")
    print(f"Language debug 2 - Output: {result2.stdout}")
    print(f"Language debug 2 - Error: {result2.stderr}")


def test_add_snippet_with_description():
    """Test adding a snippet with description via CLI."""
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Hello World",
            "--code",
            "print('Hello, World!')",
            "--language",
            "python",
            "--description",
            "A simple greeting function",
        ],
    )
    assert result.exit_code == 0


def test_add_javascript_snippet():
    """Test adding a JavaScript snippet via CLI."""
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "JS Function",
            "--code",
            "console.log('Hello from JS');",
            "--language",
            "javascript",
        ],
    )
    assert result.exit_code == 0


def test_add_rust_snippet():
    """Test adding a Rust snippet via CLI."""
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Rust Main",
            "--code",
            'fn main() { println!("Hello, Rust!"); }',
            "--language",
            "rust",
        ],
    )
    assert result.exit_code == 0


def test_add_snippet_without_description():
    """Test adding a snippet without description (should work)."""
    result = runner.invoke(
        app,
        ["add", "--title", "Simple Code", "--code", "x = 1", "--language", "python"],
    )
    assert result.exit_code == 0


def test_add_snippet_missing_title():
    """Test adding a snippet without title (should fail)."""
    result = runner.invoke(
        app, ["add", "--code", "print('test')", "--language", "python"]
    )
    assert result.exit_code != 0  # Should fail


def test_add_snippet_missing_code():
    """Test adding a snippet without code (should fail)."""
    result = runner.invoke(app, ["add", "--title", "Test", "--language", "python"])
    assert result.exit_code != 0  # Should fail


def test_add_snippet_missing_language():
    """Test adding a snippet without language (should fail)."""
    result = runner.invoke(app, ["add", "--title", "Test", "--code", "print('test')"])
    assert result.exit_code != 0  # Should fail


def test_add_snippet_invalid_language():
    """Test adding a snippet with invalid language (should fail)."""
    result = runner.invoke(
        app,
        ["add", "--title", "Test", "--code", "print('test')", "--language", "invalid"],
    )
    assert result.exit_code != 0  # Should fail


def test_add_snippet_case_insensitive_language():
    """Test that language is case insensitive."""
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test",
            "--code",
            "print('test')",
            "--language",
            "PYTHON",  # Uppercase
        ],
    )
    print(f"Case insensitive test - Exit code: {result.exit_code}")
    print(f"Case insensitive test - Output: {result.stdout}")
    print(f"Case insensitive test - Error: {result.stderr}")
    assert result.exit_code == 0


def test_add_snippet_invalid_language_debug():
    """Test adding a snippet with invalid language and see the error."""
    result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test",
            "--code",
            "print('test')",
            "--language",
            "py",  # Short form - should fail
        ],
    )
    print(f"Invalid language test - Exit code: {result.exit_code}")
    print(f"Invalid language test - Output: {result.stdout}")
    print(f"Invalid language test - Error: {result.stderr}")
    assert result.exit_code != 0  # Should fail


def test_get_snippet():
    """Test getting a snippet via CLI."""
    add_result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test Get Snippet",
            "--code",
            "print('Hello from get test')",
            "--language",
            "python",
        ],
    )
    assert add_result.exit_code == 0

    # Then try to get it (assuming it gets ID 1)
    get_result = runner.invoke(app, ["get", "1"])
    print(f"Get test - Exit code: {get_result.exit_code}")
    print(f"Get test - Output: {get_result.stdout}")
    print(f"Get test - Error: {get_result.stderr}")
    assert get_result.exit_code == 0


def test_list_snippets():
    """Test listing snippets via CLI."""
    add_result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test List Snippet",
            "--code",
            "print('Hello from list test')",
            "--language",
            "python",
        ],
    )
    assert add_result.exit_code == 0

    # Then list all snippets
    list_result = runner.invoke(app, ["list"])
    print(f"List test - Exit code: {list_result.exit_code}")
    print(f"List test - Output: {list_result.stdout}")
    print(f"List test - Error: {list_result.stderr}")
    assert list_result.exit_code == 0
    assert "Test List Snippet" in list_result.stdout


def test_toggle_favorite():
    """Test toggling favorite status via CLI."""
    add_result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test Toggle Snippet",
            "--code",
            "print('Hello from toggle test')",
            "--language",
            "python",
        ],
    )
    assert add_result.exit_code == 0

    toggle_result = runner.invoke(app, ["toggle-favorite", "1"])
    print(f"Toggle test - Exit code: {toggle_result.exit_code}")
    print(f"Toggle test - Output: {toggle_result.stdout}")
    print(f"Toggle test - Error: {toggle_result.stderr}")
    assert toggle_result.exit_code == 0
    assert "Favorited:" in toggle_result.stdout
    assert "Test Toggle Snippet" in toggle_result.stdout


def test_search_snippets():
    """Test searching snippets via CLI."""
    add_result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test Search Snippet",
            "--code",
            "print('Hello from search test')",
            "--language",
            "python",
        ],
    )
    assert add_result.exit_code == 0

    # Then search for it
    search_result = runner.invoke(app, ["search", "Test"])
    print(f"Search test - Exit code: {search_result.exit_code}")
    print(f"Search test - Output: {search_result.stdout}")
    print(f"Search test - Error: {search_result.stderr}")
    assert search_result.exit_code == 0
    assert "Test Search Snippet" in search_result.stdout


def test_delete_snippet():
    """Test deleting a snippet via CLI."""
    add_result = runner.invoke(
        app,
        [
            "add",
            "--title",
            "Test Delete Snippet",
            "--code",
            "print('Hello from delete test')",
            "--language",
            "python",
        ],
    )
    print(f"Delete test - Add exit code: {add_result.exit_code}")
    print(f"Delete test - Add output: {add_result.stdout}")
    print(f"Delete test - Add error: {add_result.stderr}")
    assert add_result.exit_code == 0

    # Then delete it (assuming it gets ID 1)
    delete_result = runner.invoke(app, ["delete", "1"])
    print(f"Delete test - Delete exit code: {delete_result.exit_code}")
    print(f"Delete test - Delete output: {delete_result.stdout}")
    print(f"Delete test - Delete error: {delete_result.stderr}")
    assert delete_result.exit_code == 0
