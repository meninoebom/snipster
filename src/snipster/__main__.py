from .db import get_session
from .models import Language, SnippetORM

with get_session() as session:
    snippet = SnippetORM(
        title="First Snip",
        code="print('foo')",
        language=Language.PYTHON,
    )
    session.add(snippet)
    session.commit()
    session.refresh(snippet)


def main() -> None:
    print("Hello from snipster!")
    print("Here is an item:")
    print(snippet)


if __name__ == "__main__":
    main()
