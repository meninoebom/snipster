import atexit
import os
from enum import Enum

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from sqlmodel import Session, create_engine
from typing_extensions import Annotated

from .exceptions import SnippetNotFoundError
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
def get(
    ctx: typer.Context,
    snippet_id: Annotated[int, typer.Argument(help="ID of the snippet to retrieve")],
):
    """
    Get and display a snippet by its ID.
    """
    repo = ctx.obj
    console = Console()

    try:
        snippet = repo.get(snippet_id)

        title = Text(f"{snippet.title} ")
        if snippet.favorite:
            title.append("⭐️", style="yellow")

        description_panel = None
        if snippet.description:
            description_panel = Panel(
                snippet.description, title="Description", border_style="blue"
            )

        code = Syntax(
            snippet.code,
            snippet.language.value,
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
        )

        console.print()
        console.print(title, style="bold blue")
        if description_panel:
            console.print(description_panel)
        console.print(code)
        console.print(f"\nTags: {', '.join(snippet.tags)}" if snippet.tags else "")

    except Exception as e:
        if isinstance(e, SnippetNotFoundError):
            console.print(f"[red]Error: Snippet with ID {snippet_id} not found.[/red]")
        else:
            console.print(f"[red]Error: {str(e)}[/red]")


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
def list(ctx: typer.Context):
    """
    List all snippets
    """
    repo = ctx.obj
    console = Console()
    snippets = repo.list()
    sorted_list = sorted(snippets, key=lambda x: x.id)
    for snippet in sorted_list:
        console.print(snippet.__str__())


@app.command()
def toggle_favorite(ctx: typer.Context, id: Annotated[int, typer.Argument]):
    repo = ctx.obj
    console = Console()
    repo.toggle_favorite(id)
    snippet = repo.get(id)
    if snippet.favorite:
        console.print(f"Favorted: {snippet.__str__()}")
    else:
        console.print(f"Unfavorted: {snippet.__str__()}")


@app.command()
def search(
    ctx: typer.Context,
    query: Annotated[
        str,
        typer.Argument(help="Search for snippets by title, description, or tags"),
    ],
):
    repo = ctx.obj
    console = Console()
    snippets = repo.search(query)
    sorted_list = sorted(snippets, key=lambda x: x.id)
    for snippet in sorted_list:
        console.print(snippet.__str__())


@app.command()
def delete(
    ctx: typer.Context,
    id: Annotated[int, typer.Argument(help="The ID of the snippet to delete")],
):
    repo = ctx.obj
    console = Console()
    try:
        repo.delete(id)
    except Exception:
        console.print(f"No snippet with id #{id} exists")
    else:
        console.print(f"Deleted snippet with id #{id}")


if __name__ == "__main__":
    app()
