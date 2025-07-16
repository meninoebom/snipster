from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import or_
from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError
from .models import SnippetCreate, SnippetORM, SnippetPublic


class AbstractSnippetRepo(ABC):
    @abstractmethod  # pragma: no cover
    def add(self, snippet: SnippetCreate) -> SnippetPublic | None:
        pass

    @abstractmethod  # pragma: no cover
    def get(self, snippet_id) -> SnippetPublic | None:
        pass

    @abstractmethod  # pragma: no cover
    def list(self) -> Sequence[SnippetPublic]:
        pass

    @abstractmethod  # pragma: no cover
    def delete(self, snippet_id: int) -> None:
        pass

    @abstractmethod  # pragma: no cover
    def toggle_favorite(self, snippet_id: int) -> None:
        pass

    @abstractmethod  # pragma: no cover
    def add_tag(self, snippet_id: int, tag: str) -> None:
        pass

    @abstractmethod  # pragma: no cover
    def remove_tag(self, snippet_id: int, tag: str) -> None:
        pass

    @abstractmethod  # pragma: no cover
    def search(self, query: str) -> Sequence[SnippetPublic]:
        pass


def to_public(orm: SnippetORM) -> SnippetPublic:
    assert orm.id is not None
    return SnippetPublic(
        id=orm.id,
        title=orm.title,
        code=orm.code,
        language=orm.language,
        description=orm.description,
        tags=orm.tags,
        favorite=orm.favorite,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate) -> SnippetPublic:
        snippet_orm = SnippetORM(
            title=snippet.title,
            code=snippet.code,
            language=snippet.language,
            description=snippet.description,
            tags=snippet.tags,
            favorite=snippet.favorite,
            created_at=snippet.created_at,
            updated_at=snippet.updated_at,
        )
        self.session.add(snippet_orm)
        self.session.commit()
        self.session.refresh(snippet_orm)
        return to_public(snippet_orm)

    def get(self, snippet_id) -> SnippetPublic:
        snippet_orm = self.session.get(SnippetORM, snippet_id)
        if snippet_orm:
            return to_public(snippet_orm)
        raise SnippetNotFoundError

    def list(self) -> Sequence[SnippetPublic]:
        snippet_orms = self.session.exec(select(SnippetORM)).all()
        return [to_public(orm) for orm in snippet_orms]

    def delete(self, snippet_id: int):
        snippet = self.session.get(SnippetORM, snippet_id)
        if snippet:
            self.session.delete(snippet)
            self.session.commit()

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.session.get(SnippetORM, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        self.session.commit()
        self.session.refresh(snippet)

    def add_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.session.get(SnippetORM, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            snippet.tags.append(tag)
            self.session.commit()
            self.session.refresh(snippet)

    def remove_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.session.get(SnippetORM, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            raise ValueError(f"Tag {tag} not found on snippet with id {snippet_id}.")
        snippet.tags.remove(tag)
        self.session.commit()
        self.session.refresh(snippet)

    def search(self, query: str) -> Sequence[SnippetPublic]:
        stmt = select(SnippetORM).where(
            or_(
                SnippetORM.title.ilike(f"%{query}%"),  # type: ignore
                SnippetORM.code.ilike(f"%{query}%"),  # type: ignore
                SnippetORM.description.ilike(f"%{query}%"),  # type: ignore
            )
        )
        string_search_results = self.session.exec(stmt).all()

        all_snippets = self.session.exec(select(SnippetORM)).all()
        tag_search_results = [
            snippet for snippet in all_snippets if query in snippet.tags
        ]

        results = {
            s.id: s for s in list(string_search_results) + tag_search_results
        }.values()
        return [to_public(orm) for orm in results]


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
            tags=snippet.tags,
            favorite=snippet.favorite,
            description=snippet.description,
            created_at=snippet.created_at or datetime.now(timezone.utc),
            # mimicing auto update by the database
            updated_at=datetime.now(timezone.utc),
        )
        self.snippets[self._next_id] = snippet_public
        self._next_id += 1
        return snippet_public

    def get(self, snippet_id: int) -> SnippetPublic:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[SnippetPublic]:
        return list(self.snippets.values())

    def delete(self, snippet_id: int) -> None:
        self.snippets.pop(snippet_id, None)

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite

    def add_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            snippet.tags.append(tag)

    def remove_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            raise ValueError(f"Tag {tag} not found on snippet with id {snippet_id}.")
        snippet.tags.remove(tag)

    def search(self, query: str) -> Sequence[SnippetPublic]:
        query = query.lower()
        results = []
        for snippet in self.snippets.values():
            hit = False
            if query in snippet.title.lower():
                hit = True
            if query in snippet.code.lower():
                hit = True
            if snippet.description:
                if query in snippet.description.lower():
                    hit = True
            if len(snippet.tags) > 0:
                print(snippet.tags)
                if query in snippet.tags:
                    hit = True
            if hit:
                results.append(snippet)
        return list(results)
