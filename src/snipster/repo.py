from abc import ABC, abstractmethod
from typing import Sequence

from sqlmodel import Session, select

from .models import SnippetCreate, SnippetORM, SnippetPublic


class AbstractSnippetRepo(ABC):
    @abstractmethod
    def add(self, snippet: SnippetCreate) -> None:
        pass

    @abstractmethod
    def get(self, snippet_id) -> SnippetPublic | None:
        pass

    @abstractmethod
    def list(self) -> Sequence[SnippetPublic]:
        pass

    @abstractmethod
    def delete(self, snippet_id: int) -> None:
        pass


def to_public(orm: SnippetORM) -> SnippetPublic:
    assert orm.id is not None
    return SnippetPublic(id=orm.id, title=orm.title, code=orm.code)


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate):
        snippet_orm = SnippetORM(title=snippet.title, code=snippet.code)
        self.session.add(snippet_orm)
        self.session.commit()
        self.session.refresh(snippet_orm)

    def get(self, snippet_id) -> SnippetPublic | None:
        snippet_orm = self.session.get(SnippetORM, snippet_id)
        if snippet_orm:
            to_public(snippet_orm)

    def list(self) -> Sequence[SnippetPublic]:
        snippet_orms = self.session.exec(select(SnippetORM)).all()
        return [to_public(orm) for orm in snippet_orms]

    def delete(self, snippet_id: int):
        snippet = self.session.get(SnippetORM, snippet_id)
        if snippet:
            self.session.delete(snippet)
            self.session.commit()


class InMemorySnippetRepo(AbstractSnippetRepo):
    def __init__(self):
        self.snippets: dict[int, SnippetPublic] = {}
        self._next_id = 1

    def add(self, snippet: SnippetCreate) -> None:
        snippet_public = SnippetPublic(
            id=self._next_id,
            title=snippet.title,
            code=snippet.code,
        )
        self.snippets[self._next_id] = snippet_public
        self._next_id += 1

    def get(self, snippet_id: int) -> SnippetPublic | None:
        return self.snippets.get(snippet_id)

    def list(self) -> Sequence[SnippetPublic]:
        return list(self.snippets.values())

    def delete(self, snippet_id: int) -> None:
        self.snippets.pop(snippet_id, None)


# class JsonBackedSnippetRepo(AbstractSnippetRepo):
#     def add(self, snippet: SnippetCreate) -> None:
#         pass

#     def get(self, snippet_id) -> SnippetCreate | None:
#         pass

#     def list(self) -> Sequence[SnippetCreate]:
#         pass

#     def delete(self, snippet_id: int) -> None:
#         pass
