import time
from collections.abc import Callable

from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from party.postseason import Games
from party.season import Prediction

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
)
layout["header"].size = 3
layout["content"].split(
    Layout(name="The Wild League"),
    Layout(name="The Mild League"),
    direction="horizontal",
)


def update_standings(title: str, data: Prediction) -> None:
    layout["header"].update(Panel(Text(title, justify="center")))

    for subleague, rows in data.items():
        teams = Table.grid(expand=True)
        teams.add_column("Flag", width=2)
        teams.add_column("Name")
        teams.add_column("Championships", width=3, style="#FFEB57")
        teams.add_column("Wins", width=4, justify="right")
        teams.add_column("Record", width=6, justify="right")
        teams.add_column("Estimate", width=3, justify="right")
        for row in rows:
            teams.add_row(
                row.badge,
                Text.assemble((row.name, row.color), row.tiebreaker),
                row.championships,
                row.wins,
                row.record,
                row.estimate,
            )

        layout[subleague].update(Panel(
            teams,
            title=subleague,
            padding=0,
        ))


def update_postseason(title: str, data: Games) -> None:
    layout["header"].update(Panel(Text(title, justify="center")))

    for subleague, games in data.items():
        tables = []
        for game in games.values():
            table = Table.grid(expand=True)
            table.add_column("Seed", width=1)
            table.add_column("Name")
            table.add_column("Wins", width=1)
            for row in game:
                table.add_row(row.seed, Text(row.name, style=row.color), row.wins)
            tables.append(Layout(table))

        all_tables = Layout()
        all_tables.split(*tables)
        layout[subleague].update(Panel(
            all_tables,
            title=subleague,
            padding=0
        ))


def display_loop(func: Callable) -> None:
    func()
    with Live(layout) as live:
        while True:
            func()

            try:
                time.sleep(300)
            except KeyboardInterrupt:
                break
