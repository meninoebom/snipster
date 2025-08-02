from .db import default_session_factory
from .models import Language, Snippet

# Store snippet info outside session context
snippet_info = None

with default_session_factory.get_session() as session:
    snippet = Snippet(
        title="First Snip",
        code="print('foo')",
        language=Language.python,
    )
    session.add(snippet)
    session.commit()
    session.refresh(snippet)

    # Store basic info before session closes
    snippet_info = {
        "id": snippet.id,
        "title": snippet.title,
        "language": snippet.language.value,
        "favorite": snippet.favorite,
    }


def main() -> None:
    print("Hello from snipster!")
    print("Here is an item:")
    if snippet_info:
        favorite_star = "⭐️" if snippet_info["favorite"] else ""
        print(
            f"{snippet_info['id']}: {snippet_info['title']} ({snippet_info['language']}) {favorite_star}"
        )


if __name__ == "__main__":
    main()
