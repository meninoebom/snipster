from abc import ABC, abstractmethod
from typing import Sequence

from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError
from .models import SnippetCreate, SnippetORM, SnippetPublic


class AbstractSnippetRepo(ABC):
    @abstractmethod
    def add(self, snippet: SnippetCreate) -> SnippetPublic | None:
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
    return SnippetPublic(
        id=orm.id, title=orm.title, code=orm.code, language=orm.language
    )


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate) -> SnippetPublic:
        snippet_orm = SnippetORM(
            title=snippet.title, code=snippet.code, language=snippet.language
        )
        self.session.add(snippet_orm)
        self.session.commit()
        self.session.refresh(snippet_orm)
        return to_public(snippet_orm)

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

    def add(self, snippet: SnippetCreate) -> SnippetPublic:
        snippet_public = SnippetPublic(
            id=self._next_id,
            title=snippet.title,
            code=snippet.code,
            language=snippet.language,
        )
        self.snippets[self._next_id] = snippet_public
        self._next_id += 1
        return snippet_public

    def get(self, snippet_id: int) -> SnippetPublic | None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[SnippetPublic]:
        return list(self.snippets.values())

    def delete(self, snippet_id: int) -> None:
        self.snippets.pop(snippet_id, None)
