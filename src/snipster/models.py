from datetime import datetime, timezone
from enum import Enum
from typing import Any, List

from sqlalchemy import JSON, Column
from sqlalchemy.ext.mutable import MutableList
from sqlmodel import Field, SQLModel


class Language(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


class SnippetBase(SQLModel, table=False):
    title: str
    code: str
    language: Language
    description: str | None = None
    # This should work for both Sqlite and Postgres
    tags: List[str] = Field(
        default_factory=list, sa_column=Column(MutableList.as_mutable(JSON))
    )
    favorite: bool = False


class Snippet(SnippetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __str__(self) -> str:
        return f"{self.id}: {self.title} ({self.language.value}) {'⭐️' if self.favorite else ''}"

    @classmethod
    def create_snippet(cls, **kwargs: Any) -> "Snippet":
        title = kwargs.get("title")
        if title is None or len(title) < 3:
            raise ValueError("Title must be at least 3 characters.")
        code = kwargs.get("code")
        if code is None or len(code) < 3:
            raise ValueError("Code must be at least 3 characters.")
        return cls(**kwargs)


class SnippetCreate(SnippetBase, table=False):
    pass
