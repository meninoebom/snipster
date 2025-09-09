from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import field_validator
from sqlmodel import Field, Index, Relationship, SQLModel, UniqueConstraint, func


class Language(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


# ---------- snippets ----------
class SnippetBase(SQLModel, table=False):
    title: str = Field(description="Title of the snippet", min_length=3)
    code: str = Field(description="The actual code snippet content", min_length=3)
    language: str = Field(description="Programming language of the snippet")
    description: str | None = Field(
        default=None, description="Optional description of the snippet"
    )
    favorite: bool = Field(
        default=False, description="Whether this snippet is marked as favorite"
    )

    @field_validator("language")
    def validate_language(cls, v):
        if isinstance(v, str):
            v = v.lower()
        allowed = ["javascript", "python", "rust"]
        if v not in allowed:
            raise ValueError(f"Language must be one of: {allowed}")
        return v


class Snippet(SnippetBase, table=True):
    __tablename__ = "snippet"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None
    tags: list["Tag"] = Relationship(
        back_populates="snippets", link_model=lambda: SnippetTag
    )

    def __str__(self) -> str:
        return (
            f"{self.id}: {self.title} ({self.language}) {'⭐️' if self.favorite else ''}"
        )

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


# ---------- tags ----------
class TagBase(SQLModel):
    name: str

    @field_validator("name")
    @classmethod
    def _normalize(cls, v: str) -> str:
        v = v.strip().lower()
        if not (2 <= len(v) <= 50):
            raise ValueError("Tag length must be 2–50.")
        return v


class Tag(TagBase, table=True):
    __tablename__ = "tag"  # type: ignore
    __table_args__ = (Index("uq_tag_name_lower", func.lower("name"), unique=True),)
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        index=True, min_length=1, max_length=50, description="Name of the tag"
    )  # normalize via validator above
    snippets: list[Snippet] = Relationship(
        back_populates="tags", link_model=lambda: SnippetTag
    )


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int


# ---------- snippet tags ----------
class SnippetTag(SQLModel, table=True):
    __tablename__ = "snippet_tag"  # type: ignore
    __table_args__ = (
        UniqueConstraint("snippet_id", "tag_id", name="uq_snippet_tag"),
        Index("ix_snippet_tag_snippet_id", "snippet_id"),
        Index("ix_snippet_tag_tag_id", "tag_id"),
    )

    snippet_id: int = Field(foreign_key="snippet.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
