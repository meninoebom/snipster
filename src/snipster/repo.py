from abc import ABC, abstractmethod
from typing import Sequence

from sqlmodel import select

from .db import get_session
from .models import Snippet, SnippetORM


class AbstractSnippetRepo(ABC):
    @abstractmethod
    def add(self, snippet: Snippet) -> None:
        pass

    @abstractmethod
    def get(self, snippet_id) -> Snippet | None:
        pass

    @abstractmethod
    def list(self) -> Sequence[Snippet]:
        pass

    @abstractmethod
    def delete(self, snippet_id: int) -> None:
        pass


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    def add(self, snippet: Snippet):
        snippet_orm = SnippetORM(id=snippet.id, title=snippet.title, code=snippet.code)
        with get_session() as session:
            session.add(snippet_orm)
            session.commit()
            session.refresh(snippet_orm)

    def get(self, snippet_id) -> Snippet | None:
        with get_session() as session:
            snippet_orm = session.get(SnippetORM, snippet_id)
        if snippet_orm:
            return Snippet(
                id=snippet_orm.id, title=snippet_orm.title, code=snippet_orm.code
            )

    def list(self) -> Sequence[Snippet]:
        with get_session() as session:
            snippet_orms = session.exec(select(SnippetORM)).all()
            return [
                Snippet(id=orm.id, title=orm.title, code=orm.code)
                for orm in snippet_orms
            ]

    def delete(self, snippet_id: int):
        with get_session() as session:
            snippet = session.get(SnippetORM, snippet_id)
            if snippet:
                session.delete(snippet)
                session.commit()


class InMemorySnippetRepo(AbstractSnippetRepo):
    def __init__(self):
        self.snippets: dict[int, Snippet] = {}

    def add(self, snippet: Snippet) -> None:
        if snippet.id is None:
            snippet.id = max(self.snippets.keys(), default=0) + 1
        self.snippets[snippet.id] = snippet

    def get(self, snippet_id) -> Snippet | None:
        snippet = self.snippets[snippet_id]
        if snippet:
            return snippet
        else:
            return None

    def list(self) -> Sequence[Snippet]:
        return list(self.snippets.values())

    def delete(self, snippet_id: int) -> None:
        del self.snippets[snippet_id]


class JsonBackedSnippetRepo(AbstractSnippetRepo):
    def add(self, snippet: Snippet) -> None:
        pass

    def get(self, snippet_id) -> Snippet | None:
        pass

    def list(self) -> Sequence[Snippet]:
        pass

    def delete(self, snippet_id: int) -> None:
        pass
