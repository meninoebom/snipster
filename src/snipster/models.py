from typing import Optional

from sqlmodel import Field, SQLModel


class SnippetORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str


class Snippet:
    @staticmethod
    def _validate_fields(title: str, code: str) -> None:
        """Validate title and code fields."""
        if not isinstance(title, str):
            raise TypeError("`title` must be a string")
        if len(title) < 3:
            raise ValueError("`title` must be at least 3 characters long")

        if not isinstance(code, str):
            raise TypeError("`code` must be a string")
        if not code.strip():
            raise ValueError("`code` cannot be empty")

    def __init__(self, id: Optional[int], title: str, code: str):
        self._validate_fields(title, code)
        self.id = id
        self.title = title
        self.code = code

    @classmethod
    def from_dict(cls, **kwargs) -> "Snippet":
        if "title" not in kwargs:
            raise ValueError("Missing required argument: 'title'")
        if "code" not in kwargs:
            raise ValueError("Missing required argument: 'code'")

        cls._validate_fields(kwargs["title"], kwargs["code"])
        return cls(**kwargs)
