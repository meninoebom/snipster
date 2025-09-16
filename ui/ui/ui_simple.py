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

    async def load_all_snippets(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE_URL}/snippets")
                if response.status_code == 200:
                    self.snippets = response.json()
                    print(f"Loaded {len(self.snippets)} snippets")
                else:
                    print(f"Failed to load snippets: {response.status_code}")
        except Exception as e:
            print(f"Error loading snippets: {e}")
            self.snippets = []

    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form

    def select_snippet(self, snippet_id: int):
        if self.selected_snippet_id == snippet_id:
            self.selected_snippet_id = 0
        else:
            self.selected_snippet_id = snippet_id


def snippet_card(snippet: dict):
    tags_text = ""
    if snippet.get("tags") and len(snippet["tags"]) > 0:
        tags_text = f"Tags: {', '.join(snippet['tags'])}"

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(snippet["title"], weight="bold", size="3"),
                rx.badge(snippet.get("language", "text"), variant="surface"),
                rx.spacer(),
                width="100%",
            ),
            rx.cond(
                tags_text,
                rx.text(tags_text, size="2", color="gray"),
                rx.box(),
            ),
            rx.cond(
                State.selected_snippet_id == snippet.get("id"),
                rx.code_block(
                    snippet["code"],
                    language=snippet.get("language", "text"),
                    show_line_numbers=True,
                ),
                rx.text(snippet["code"], size="2", color="gray"),
            ),
            spacing="2",
            width="100%",
            on_click=lambda snippet_id=snippet["id"]: State.select_snippet(snippet_id),
            cursor="pointer",
        ),
        width="100%",
        margin_bottom="2",
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("Snipster v1", size="6", margin_bottom="4"),
            rx.button(
                "Load Snippets",
                on_click=State.load_all_snippets,
                variant="solid",
            ),
            rx.button(
                "Toggle Form",
                on_click=State.toggle_add_form,
                variant="outline",
            ),
            rx.cond(
                State.show_add_form,
                rx.card(
                    rx.text("Add form would go here"),
                    width="100%",
                    margin_bottom="4",
                ),
            ),
            rx.cond(
                len(State.snippets) == 0,
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
