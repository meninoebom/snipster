from typing import Optional

from sqlmodel import Field, SQLModel


class SnippetORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str


#     @classmethod
#     # "Snippet" is a forward reference that allows
#     # type hints to reference the class from inside itself
#     def from_dict(cls, **kwargs) -> "Snippet":
#    if "title" not in kwargs:
#         raise ValueError("Missing required argument: 'title'")
#     if "code" not in kwargs:
#         raise ValueError("Missing required argument: 'code'")
#     if not isinstance(kwargs["title"], str):
#         raise TypeError("'title' must be a string")
#     if not isinstance(kwargs["code"], str):
#         raise TypeError("'code' must be a string")
#     if len(kwargs["title"]) < 3:
#         raise ValueError("Title must be at least 3 chars long")
#     return cls(**kwargs)


class Snippet:
    def __init__(self, id: Optional[int], title: str, code: str):
        if not isinstance(title, str):
            raise TypeError("`title` must be a string")
        if len(title) < 3:
            raise ValueError("`title` must be at least 3 characters long")

        if not isinstance(code, str):
            raise TypeError("`code` must be a string")
        if not code.strip():
            raise ValueError("`code` cannot be empty")

        self.id = id
        self.title = title
        self.code = code
