from __future__ import annotations

from datetime import datetime, timezone

import reflex as rx

THEMES: list[str] = [
    "material-theme-darker",
    "monokai",
    "solarized-dark",
    "andromeeda",
    "aurora-x",
    "ayu-dark",
    "catppuccin-frappe",
    "catppuccin-macchiato",
    "catppuccin-mocha",
    "dark-plus",
    "dracula",
    "everforest-dark",
    "github-dark",
    "houston",
    "laserwave",
    "material-theme",
    "material-theme-ocean",
    "material-theme-palenight",
    "min-dark",
    "night-owl",
    "nord",
    "one-dark-pro",
    "plastic",
    "poimandres",
    "rose-pine",
    "rose-pine-moon",
    "slack-dark",
    "synthwave-84",
    "tokyo-night",
    "vesper",
    "vitesse-black",
    "vitesse-dark",
]


class State(rx.State):
    """The app state."""

    theme: str = "material-theme-darker"
    date_now: datetime = datetime.now(timezone.utc)

    def change_theme(
        self: State,
        theme: str,
    ) -> None:
        self.theme = theme

    def increment_theme(
        self: State,
        _,  # trunk-ignore(ruff/ANN001)
    ) -> None:
        del _
        theme_index = THEMES.index(self.theme)
        self.theme = THEMES[(theme_index + 1) % len(THEMES)]

    @rx.var
    def code_to_display(
        self,  # trunk-ignore(ruff/ANN101)
    ) -> str:
        return f"""
def index() -> rx.Component:
    return rx.container(
        rx._x.code_block(
            RECURSION,
            language='python',
            show_line_numbers=True,
            theme='{self.theme}',
        ),
    )"""


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.box(
                rx._x.code_block(  # trunk-ignore(ruff/SLF001)
                    State.code_to_display,
                    language="python",
                    show_line_numbers=True,
                    theme=State.theme,
                ),
                min_width="500px",
            ),
            rx.spacer(),
            rx.text(State.theme),
            rx.spacer(),
            rx.radio_group(
                THEMES,
                value=State.theme,
                on_change=State.change_theme,
                direction="column",
            ),
            rx.moment(
                format="",
                interval=1000,
                on_change=State.increment_theme,
            ),
        ),
    )


app = rx.App()
app.add_page(index)
