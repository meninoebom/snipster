from typer import Typer

app = Typer()


@app.command()
def list():
    print("list")


@app.command()
def add():
    print("add")


@app.command()
def delete():
    print("delete")


@app.command()
def toggle_favorite():
    print("favorite")


@app.command()
def search():
    print("search")


if __name__ == "__main__":
    app()
