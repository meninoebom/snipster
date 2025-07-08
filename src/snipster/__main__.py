import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

from .models import Item

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")

engine = create_engine(db_url, echo=False)

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    item = Item(name="Laptop", price=999.99)
    session.add(item)
    session.commit()
    session.refresh(item)


def main() -> None:
    print("Hello from snipster!")
    print("Here is an item:")
    print(item)


if __name__ == "__main__":
    main()
