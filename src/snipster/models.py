from pydantic import field_validator
from sqlmodel import Field, SQLModel


class SnippetORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str


class SnippetCreate(SQLModel, table=False):
    title: str
    code: str

    @field_validator("title")
    def check_title(cls, value):
        if len(value) < 3:
            raise ValueError("Title must be at least 3 characters.")
        return value

    @field_validator("code")
    def check_code(cls, value):
        if len(value) < 3:
            raise ValueError("Code must be at least 3 characters.")
        return value
