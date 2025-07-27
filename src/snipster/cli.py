from enum import Enum

import typer
from typing_extensions import Annotated


class Language(str, Enum):
    javascript = "javascript"
    python = "python"
    rust = "rust"


app = typer.Typer()


@app.command()
def add(
    title: Annotated[
        str, typer.Option(..., "--title", "-t", help="Title of the snippet")
    ],
    code: Annotated[str, typer.Option(..., "--code", "-c", help="The snippet code")],
    language: Annotated[
        Language,
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
    print(f"title = {title}")
    print(f"code = {code}")
    print(f"description = {description}")
    print(f"language = {language}")

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
