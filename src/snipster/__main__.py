from .db import create_db_and_tables, get_session
from .models import Snippet

create_db_and_tables()

with get_session() as session:
    snippet = Snippet(title="First Snip", code='print("foo")')
    session.add(snippet)
    session.commit()
    session.refresh(snippet)


def main() -> None:
    print("Hello from snipster!")
    print("Here is an item:")
    print(snippet)


if __name__ == "__main__":
    main()
