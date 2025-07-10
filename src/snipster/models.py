from sqlmodel import Field, SQLModel


class Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str

    @classmethod
    # "Snippet" is a forward reference that allows
    # type hints to reference the class from inside itself
    def from_dict(cls, **kwargs) -> "Snippet":
        if "title" not in kwargs:
            raise ValueError("Missing required argument: 'title'")
        if "code" not in kwargs:
            raise ValueError("Missing required argument: 'code'")
        if not isinstance(kwargs["title"], str):
            raise TypeError("'title' must be a string")
        if not isinstance(kwargs["code"], str):
            raise TypeError("'code' must be a string")
        if len(kwargs["title"]) < 3:
            raise ValueError("Title must be at least 3 chars long")
        return cls(**kwargs)
