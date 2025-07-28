import atexit
import os
from enum import Enum

import typer
from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from typing_extensions import Annotated

from .models import Language as ModelLanguageEnum
from .models import Snippet
from .repo import DatabaseBackedSnippetRepo as db_repo

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///snipster.sqlite")
engine = create_engine(db_url)


class LanguageEnum(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


app = typer.Typer()


@app.callback(invoke_without_command=True)
def setup(ctx: typer.Context):
    session = Session(engine)
    ctx.obj = db_repo(session=session)

    atexit.register(session.close)


@app.command()
def add(
    ctx: typer.Context,
    title: Annotated[
        str, typer.Option(..., "--title", "-t", help="Title of the snippet")
    ],
    code: Annotated[str, typer.Option(..., "--code", "-c", help="The snippet code")],
    language: Annotated[
        LanguageEnum,
        typer.Option(
            ...,
            "--language",
            "--lang",
            "-l",
            help="Which language is your snippet written in? Javascript, Python, or Rust",
            case_sensitive=False,
            prompt="Choose a language",
            show_choices=True,
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            ...,
            "--description",
            "--desc",
            "-d",
            help="The snippet code",
            rich_help_panel="Optional",
        ),
    ] = "",
):
    """
    Add a new code snippet to the repository.
    """
    repo = ctx.obj
    enum_map = {
        "python": ModelLanguageEnum["PYTHON"],
        "javascript": ModelLanguageEnum["JAVASCRIPT"],
        "rust": ModelLanguageEnum["RUST"],
    }
    snippet = Snippet.create_snippet(
        title=title,
        code=code,
        description=description,
        language=enum_map[LanguageEnum(language).value],
    )
    repo.add(snippet)

    @app.command()
    def list():
        """
        List all snippets
        """
        print("list")

    @app.command()
    def toggle_favorite():
        print("favorite")

    @app.command()
    def search(
        query: Annotated[
            str,
            typer.Argument(help="Search for snippets by title, description, or tags"),
        ],
    ):
        print(f"searching for {query}")

    @app.command()
    def delete(
        id: Annotated[int, typer.Argument(help="The ID of the snippet to delete")],
    ):
        print(f"deleting snipper with id{id}")

    if __name__ == "__main__":
        app()
