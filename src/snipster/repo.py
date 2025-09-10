from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Sequence

from rapidfuzz import process as rapidfuzz_process
from sqlalchemy import Text, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError, TagNotAssociatedError, TagNotFoundError
from .models import Snippet, SnippetCreate, SnippetTag, Tag


class AbstractSnippetRepo(ABC):  # pragma: no cover
    @abstractmethod
    def add(self, snippet: SnippetCreate) -> Snippet | None:
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

    @abstractmethod
    def toggle_favorite(self, snippet_id: int) -> Snippet | None:
        pass

    @abstractmethod
    def add_tag(self, snippet_id: int, tag_name: str) -> Snippet | None:
        pass

    @abstractmethod
    def remove_tag(self, snippet_id: int, tag_name: str) -> Snippet | None:
        pass

    @abstractmethod
    def search(self, query: str) -> Sequence[Snippet]:
        pass


class DatabaseBackedSnippetRepo(AbstractSnippetRepo):
    # Good to use a single session across calls incase
    # there are multiple operations called at call site
    # Therefore, let the call site handle session management
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, snippet: SnippetCreate) -> Snippet:
        stored_snippet = Snippet.create_snippet(**snippet.model_dump())
        self.session.add(stored_snippet)
        self.session.commit()
        self.session.refresh(stored_snippet)
        return stored_snippet

    def get(self, snippet_id: int) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError
        return snippet

    def list(self) -> Sequence[Snippet]:
        return list(self.session.exec(select(Snippet)).all())

    def delete(self, snippet_id: int):
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        self.session.delete(snippet)
        self.session.commit()

    def toggle_favorite(self, snippet_id: int) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        self.session.commit()
        self.session.refresh(snippet)
        return snippet

    def add_tag(self, snippet_id: int, tag_name: str) -> Snippet | None:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")

        tag_name = tag_name.strip().lower()

        tag: Tag | None = self.session.exec(
            select(Tag).where(Tag.name == tag_name)
        ).one_or_none()
        if tag is None:
            tag = Tag(name=tag_name)
            self.session.add(tag)
            self.session.flush()  # populates tag.id without committing
        try:
            assert tag.id is not None  # narrows the type of tag.id to int
            self.session.add(SnippetTag(snippet_id=snippet_id, tag_id=tag.id))
            self.session.commit()
        except IntegrityError:
            self.session.rollback()  # link already exists or FK issue; proceed

        # load snippet w/ tags in one go
        stmt = (
            select(Snippet)
            .options(selectinload(Snippet.tags))  # type: ignore
            .where(Snippet.id == snippet_id)
        )
        return self.session.exec(stmt).one()

    def remove_tag(self, snippet_id: int, tag_name: str) -> Snippet:
        snippet = self.session.get(Snippet, snippet_id)
        if snippet is None:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")

        tag_name = tag_name.strip().lower()
        tag: Tag | None = self.session.exec(
            select(Tag).where(Tag.name == tag_name)
        ).one_or_none()
        if tag is None:
            raise TagNotFoundError(f"Tag '{tag_name}' not found.")  # Custom exception

        # Ensure tag.id is not None before using it in the query
        if tag.id is None:
            raise TagNotFoundError(f"Tag '{tag_name}' has no ID.")

        # Find the SnippetTag record first, then delete it
        snippet_tag = self.session.exec(
            select(SnippetTag).where(
                SnippetTag.snippet_id == snippet_id,
                SnippetTag.tag_id == tag.id,
            )
        ).one_or_none()

        if snippet_tag is None:
            raise TagNotAssociatedError(
                f"Tag '{tag_name}' not associated with snippet {snippet_id}."
            )

        self.session.delete(snippet_tag)

        self.session.commit()

        # Refresh the existing snippet object instead of new query
        self.session.refresh(snippet, ["tags"])
        return snippet

    def search(self, query: str) -> Sequence[Snippet]:
        stmt = select(Snippet).where(
            or_(
                Snippet.title.ilike(f"%{query}%"),  # type: ignore
                Snippet.code.ilike(f"%{query}%"),  # type: ignore
                Snippet.description.ilike(f"%{query}%"),  # type: ignore
                # This should work for both Sqlite and Postgres
                Snippet.tags.cast(Text).ilike(f"%{query}%"),  # type: ignore
            )
        )
        results = self.session.exec(stmt).all()
        return [snippet for snippet in results]

    def fuzzy_search(self, query: str) -> Sequence[Snippet]:
        all_snippets = self.session.exec(select(Snippet)).all()
        snippet_dict = {s.title.lower(): s for s in all_snippets}
        # Normalize query to lowercase for better matching
        normalized_query = query.lower()
        matches = rapidfuzz_process.extract(
            normalized_query, snippet_dict.keys(), limit=5, score_cutoff=70
        )
        results = [snippet_dict[m[0]] for m in matches]
        return results


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

    def toggle_favorite(self, snippet_id: int) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")
        snippet.favorite = not snippet.favorite
        return snippet

    def add_tag(self, snippet_id: int, tag_name: str) -> Snippet | None:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")

        # Check if tag already exists
        existing_tag = next((tag for tag in snippet.tags if tag.name == tag_name), None)
        if existing_tag is None:
            # Create a new tag
            tag = Tag(name=tag_name)
            snippet.tags.append(tag)
            return snippet

    def remove_tag(self, snippet_id: int, tag_name: str) -> Snippet:
        snippet = self.snippets.get(snippet_id)
        if not snippet:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found.")

        # Find the tag to remove
        tag_to_remove = next(
            (tag for tag in snippet.tags if tag.name == tag_name), None
        )
        if tag_to_remove is None:
            raise ValueError(
                f"Tag {tag_name} not found on snippet with id {snippet_id}."
            )

        snippet.tags.remove(tag_to_remove)
        return snippet

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
                # Check if query matches any tag name
                if any(query in tag.name.lower() for tag in snippet.tags):
                    hit = True
            if hit:
                results.append(snippet)
        return list(results)

    def fuzzy_search(self, query: str) -> Sequence[Snippet]:
        snippet_dict = {s.title.lower(): s for s in self.snippets.values()}
        # Normalize query to lowercase for better matching
        normalized_query = query.lower()
        matches = rapidfuzz_process.extract(
            normalized_query, snippet_dict.keys(), limit=5, score_cutoff=70
        )
        results = [snippet_dict[m[0]] for m in matches]
        return results
