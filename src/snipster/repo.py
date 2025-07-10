from abc import ABC, abstractmethod
from typing import Sequence

from sqlmodel import Session, select

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
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: Snippet):
        snippet_orm = SnippetORM(id=snippet.id, title=snippet.title, code=snippet.code)
        self.session.add(snippet_orm)
        self.session.commit()
        self.session.refresh(snippet_orm)

    def get(self, snippet_id) -> Snippet | None:
        snippet_orm = self.session.get(SnippetORM, snippet_id)
        if snippet_orm:
            return Snippet(
                id=snippet_orm.id, title=snippet_orm.title, code=snippet_orm.code
            )

    def list(self) -> Sequence[Snippet]:
        snippet_orms = self.session.exec(select(SnippetORM)).all()
        return [
            Snippet(id=orm.id, title=orm.title, code=orm.code) for orm in snippet_orms
        ]

    def delete(self, snippet_id: int):
        snippet = self.session.get(SnippetORM, snippet_id)
        if snippet:
            self.session.delete(snippet)
            self.session.commit()


class InMemorySnippetRepo(AbstractSnippetRepo):
    def __init__(self):
        self.snippets: dict[int, Snippet] = {}

    def add(self, snippet: Snippet) -> None:
        if snippet.id is None:
            snippet.id = max(self.snippets.keys(), default=0) + 1
        self.snippets[snippet.id] = snippet

    def get(self, snippet_id) -> Snippet | None:
        snippet = self.snippets[snippet_id]
        if snippet is None:
            return None
        return snippet

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
