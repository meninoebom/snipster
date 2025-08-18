import os

import httpx
import reflex as rx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class State(rx.State):
    snippets: list[dict] = []
    search_query: str = ""
    show_add_form: bool = False
    selected_snippet_id: int = 0

    # Form fields
    new_title: str = ""
    new_code: str = ""
    new_language: str = "python"
    new_tags: str = ""

    async def search(self, query: str):
        self.search_query = query
        try:
            if query.strip():
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{API_BASE_URL}/search", params={"q": query}
                    )
                    if response.status_code == 200:
                        self.snippets = response.json()
            else:
                await self.load_all_snippets()
        except Exception:
            pass

    async def load_all_snippets(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE_URL}/snippets")
                if response.status_code == 200:
                    self.snippets = response.json()
        except Exception:
            self.snippets = []

    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form

    def select_snippet(self, snippet_id: int):
        if self.selected_snippet_id == snippet_id:
            self.selected_snippet_id = 0
        else:
            self.selected_snippet_id = snippet_id

    async def add_snippet(self):
        if not self.new_title.strip() or not self.new_code.strip():
            return
        try:
            async with httpx.AsyncClient() as client:
                tags = [t.strip() for t in self.new_tags.split(",") if t.strip()]
                response = await client.post(
                    f"{API_BASE_URL}/create",
                    json={
                        "title": self.new_title,
                        "code": self.new_code,
                        "language": self.new_language,
                        "tags": tags,
                    },
                )
                if response.status_code == 201:
                    self.show_add_form = False
                    self.new_title = ""
                    self.new_code = ""
                    self.new_tags = ""
                    await self.load_all_snippets()
        except Exception:
            pass

    async def delete_snippet(self, snippet_id: int):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{API_BASE_URL}/snippets/{snippet_id}")
                if response.status_code == 200:
                    await self.load_all_snippets()
        except Exception:
            pass


def add_form():
    return rx.cond(
        State.show_add_form,
        rx.card(
            rx.vstack(
                rx.heading("Add New Snippet", size="4"),
                rx.input(
                    placeholder="Title",
                    value=State.new_title,
                    on_change=State.set_new_title,
                ),
                rx.select(
                    ["python", "javascript", "rust"],
                    value=State.new_language,
                    on_change=State.set_new_language,
                ),
                rx.text_area(
                    placeholder="Paste your code here...",
                    value=State.new_code,
                    on_change=State.set_new_code,
                    rows="10",
                ),
                rx.input(
                    placeholder="Tags (comma-separated)",
                    value=State.new_tags,
                    on_change=State.set_new_tags,
                ),
                rx.hstack(
                    rx.button(
                        "Cancel", on_click=State.toggle_add_form, variant="surface"
                    ),
                    rx.button("Add Snippet", on_click=State.add_snippet),
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
            margin_bottom="4",
        ),
    )


def snippet_card(snippet: dict):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(snippet["title"], weight="bold", size="3"),
                rx.badge(snippet.get("language", "text"), variant="surface"),
                rx.spacer(),
                width="100%",
            ),
            rx.cond(
                State.selected_snippet_id == snippet.get("id"),
                rx.vstack(
                    rx.code_block(
                        snippet["code"],
                        language=snippet.get("language", "text"),
                        show_line_numbers=True,
                    ),
                    rx.hstack(
                        rx.button(
                            "Delete",
                            on_click=lambda: State.delete_snippet(snippet["id"]),
                            size="1",
                            variant="surface",
                            color="red",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                ),
                rx.text(snippet["code"], size="2", color="gray"),
            ),
            spacing="2",
            width="100%",
            on_click=lambda: State.select_snippet(snippet["id"]),
            cursor="pointer",
        ),
        width="100%",
        margin_bottom="2",
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("Snipster v1", size="6", margin_bottom="4"),
            rx.card(
                rx.vstack(
                    rx.text("Environment Info:", weight="bold", size="2"),
                    rx.text(f"API_BASE_URL: {API_BASE_URL}", size="2", color="blue"),
                    rx.text(
                        f"Environment: {'Production' if 'reflex.run' in API_BASE_URL else 'Local'}",
                        size="2",
                        color="gray",
                    ),
                    spacing="1",
                ),
                width="100%",
                margin_bottom="4",
                variant="surface",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Search snippets...",
                    value=State.search_query,
                    on_change=State.search,
                    width="100%",
                ),
                rx.button(
                    "+ New",
                    on_click=State.toggle_add_form,
                    variant="solid",
                ),
                width="100%",
                spacing="2",
            ),
            add_form(),
            rx.cond(
                State.snippets.length() == 0,
                rx.center(
                    rx.text("No snippets found", color="gray"),
                    padding="8",
                ),
                rx.vstack(
                    rx.foreach(State.snippets, snippet_card),
                    width="100%",
                ),
            ),
            width="100%",
            padding="4",
        ),
        max_width="800px",
    )


app = rx.App()
app.add_page(index, on_load=State.load_all_snippets)
