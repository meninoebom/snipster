from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import or_
from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError
from .models import Snippet, SnippetCreate


class AbstractSnippetRepo(ABC):
    @abstractmethod  # pragma: no cover
    def add(self, snippet: SnippetCreate) -> Snippet | None:
        pass

    @abstractmethod  # pragma: no cover
    def get(self, snippet_id) -> Snippet | None:
        pass

    @abstractmethod  # pragma: no cover
    def list(self) -> Sequence[Snippet]:
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
    def search(self, query: str) -> Sequence[Snippet]:
        pass


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate) -> Snippet:
        snippet_orm = Snippet.create_snippet(**snippet.model_dump())
        self.session.add(snippet_orm)
        self.session.commit()
        self.session.refresh(snippet_orm)
        return snippet_orm

    def get(self, snippet_id) -> Snippet:
        snippet_orm = self.session.get(Snippet, snippet_id)
        if snippet_orm:
            return snippet_orm
        raise SnippetNotFoundError

    def list(self) -> Sequence[Snippet]:
        snippet_orms = self.session.exec(select(Snippet)).all()
        return [snippet for snippet in snippet_orms]

    def delete(self, snippet_id: int):
        snippet = self.session.get(Snippet, snippet_id)
        if snippet:
            self.session.delete(snippet)
            self.session.commit()

    def toggle_favorite(self, snippet_id: int) -> None:
        snippet = self.session.get(Snippet, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        self.session.commit()
        self.session.refresh(snippet)

    def add_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.session.get(Snippet, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            snippet.tags.append(tag)
            self.session.commit()
            self.session.refresh(snippet)

    def remove_tag(self, snippet_id: int, tag: str) -> None:
        snippet = self.session.get(Snippet, snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        if tag not in snippet.tags:
            raise ValueError(f"Tag {tag} not found on snippet with id {snippet_id}.")
        snippet.tags.remove(tag)
        self.session.commit()
        self.session.refresh(snippet)

    def search(self, query: str) -> Sequence[Snippet]:
        stmt = select(Snippet).where(
            or_(
                Snippet.title.ilike(f"%{query}%"),  # type: ignore
                Snippet.code.ilike(f"%{query}%"),  # type: ignore
                Snippet.description.ilike(f"%{query}%"),  # type: ignore
            )
        )
        string_search_results = self.session.exec(stmt).all()

        all_snippets = self.session.exec(select(Snippet)).all()
        tag_search_results = [
            snippet for snippet in all_snippets if query in snippet.tags
        ]

        results = {
            s.id: s for s in list(string_search_results) + tag_search_results
        }.values()
        return [snippet for snippet in results]


class InMemorySnippetRepo(AbstractSnippetRepo):
    def __init__(self):
        self.snippets: dict[int, Snippet] = {}
        self._next_id = 1

    def add(self, snippet: SnippetCreate) -> Snippet:
        stored_snippet = Snippet.create_snippet(
            **snippet.model_dump(),
            id=self._next_id,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
        )
        self.snippets[self._next_id] = stored_snippet
        self._next_id += 1
        return stored_snippet

    def get(self, snippet_id: int) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[Snippet]:
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

    def search(self, query: str) -> Sequence[Snippet]:
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
