from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, field_validator
from sqlmodel import Field, ForeignKeyConstraint, Index, Relationship, SQLModel, text


class Language(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


# ---------- snippet tags ----------
class SnippetTag(SQLModel, table=True):
    __tablename__ = "snippet_tag"  # type: ignore
    __table_args__ = (
        # UniqueConstraint("snippet_id", "tag_id", name="uq_snippet_tag"),
        ForeignKeyConstraint(["snippet_id"], ["snippet.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        Index("ix_snippet_tag_snippet_id", "snippet_id"),
        Index("ix_snippet_tag_tag_id", "tag_id"),
    )

    snippet_id: int = Field(primary_key=True)
    tag_id: int = Field(primary_key=True)


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
        back_populates="snippets",
        link_model=SnippetTag,
        sa_relationship_kwargs={
            "lazy": "selectin",  # efficient M2M loads
            "passive_deletes": True,  # rely on DB ON DELETE for join rows
        },
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


class CreateSnippetRequest(SnippetBase):
    """Request model specifically for the /create endpoint"""

    tags: list[str] = []


class SnippetResponse(BaseModel):
    """Response model for snippets"""

    id: int | None
    title: str
    code: str
    language: str
    description: str | None
    favorite: bool
    created_at: datetime
    updated_at: datetime | None
    tags: list[str] = []

    @classmethod
    def from_snippet(cls, snippet: Snippet) -> "SnippetResponse":
        """Convert a Snippet model to SnippetResponse."""
        return cls(
            id=snippet.id,
            title=snippet.title,
            code=snippet.code,
            language=snippet.language,
            description=snippet.description,
            favorite=snippet.favorite,
            created_at=snippet.created_at,
            updated_at=snippet.updated_at,
            tags=[tag.name for tag in snippet.tags],  # Extract tag names as list
        )


# ---------- tags ----------
class TagBase(SQLModel, table=False):
    name: str = Field(
        index=True, min_length=1, max_length=50, description="Name of the tag"
    )

    @field_validator("name")
    @classmethod
    def _normalize(cls, v: str) -> str:
        v = v.strip().lower()
        if not (1 <= len(v) <= 50):
            raise ValueError("Tag length must be 1–50.")
        return v


class Tag(TagBase, table=True):
    __tablename__ = "tag"
    __table_args__ = (Index("uq_tag_name_lower", text("lower(name)"), unique=True),)
    id: int | None = Field(default=None, primary_key=True)
    snippets: list["Snippet"] = Relationship(
        back_populates="tags", link_model=SnippetTag
    )


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int
