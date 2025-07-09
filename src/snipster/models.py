from sqlmodel import Field, SQLModel


class Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str

    @classmethod
    # "Snippet" is a forward reference that allows
    # type hints to reference the class from inside itself
    def from_dict(cls, data: dict[str, str]) -> "Snippet":
        title = data["title"]
        code = data["code"]
        return cls(title=title, code=code)
