from sqlmodel import Field, SQLModel


class Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str

    @classmethod
    # "Snippet" is a forward reference that allows
    # type hints to reference the class from inside itself
    def from_dict(cls, **kwargs) -> "Snippet":
        return cls(**kwargs)
