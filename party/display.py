import time
from collections.abc import Callable

from rich.columns import Columns
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from party.season import Prediction

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
)
layout["header"].size = 3


def update_standings(title: str, data: Prediction) -> None:
    layout["header"].update(Panel(Text(title, justify="center")))

    widgets = []
    for conference, rows in data.items():
        teams = Table.grid(expand=True)
        teams.add_column("Name")
        teams.add_column("Wins", width=4, justify="right")
        teams.add_column("Record", width=6, justify="right")
        teams.add_column("Estimate", width=3, justify="right")
        for row in rows:
            if not row:
                teams.add_row()
            else:
                teams.add_row(
                    Text(row.name, row.color),
                    str(row.wins),
                    row.record,
                    row.estimate,
                )

        widgets.append(
            Panel(
                teams,
                title=conference,
                padding=0,
            )
        )
    layout["content"].update(Columns(widgets, expand=True))


def display_loop(func: Callable) -> None:
    func()
    with Live(layout) as live:
        while True:
            func()

            try:
                time.sleep(300)
            except KeyboardInterrupt:
                break
