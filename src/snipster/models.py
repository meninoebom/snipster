from datetime import datetime, timezone
from enum import Enum

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class Language(Enum):
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    RUST = "rust"


class SnippetBase(SQLModel, table=False):
    title: str
    code: str
    language: Language
    description: str | None = None
    tags: str | None = None
    favorite: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None


class SnippetORM(SnippetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class SnippetCreate(SnippetBase, table=False):
    @field_validator("title")
    @classmethod
    def check_title(cls, value):
        if len(value) < 3:
            raise ValueError("Title must be at least 3 characters.")
        return value

    @field_validator("code")
    @classmethod
    def check_code(cls, value):
        if len(value) < 3:
            raise ValueError("Code must be at least 3 characters.")
        return value


class SnippetPublic(SnippetBase, table=False):
    id: int
