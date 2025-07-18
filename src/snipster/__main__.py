from .db import get_session
from .models import Language, Snippet

with get_session() as session:
    snippet = Snippet(
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
