from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from standings.postseason import Brackets
from standings.season import Prediction

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
    Layout(name="footer"),
)
layout["header"].size = 3
layout["footer"].size = 3
layout["content"].split(
    Layout(name="overbracket"),
    Layout(name="underbracket"),
)
for bracket in ("overbracket", "underbracket"):
    layout[bracket].split_row(
        Layout(name="The Wild League"),
        Layout(name="The Mild League"),
    )


def update_standings(data: Prediction) -> None:
    layout["header"].update(Panel(Text("data.name", justify="center")))

    for subleague, rows in data.items():
        teams = Table.grid(expand=True)
        teams.add_column("Flag", width=2)
        teams.add_column("Name")
        teams.add_column("Championships", width=3, style="#FFEB57")
        teams.add_column("Wins", width=4, justify="right")
        teams.add_column("Record", width=6, justify="right")
        teams.add_column("Estimate", width=3, justify="right")
        for row in rows:
            if not row:
                teams.add_row()
            else:
                teams.add_row(
                    row.badge,
                    Text.assemble((row.name, row.color), f"[{row.tiebreaker}]"),
                    "●" * row.championships if row.championships < 4 else f"●x{row.championships}",
                    f"{'*' if row.in_progress else ''}{row.wins}",
                    f"{row.nonlosses}-{row.losses}",
                    row.estimate,
                )

        layout[subleague].update(Panel(
            teams,
            title=subleague,
            padding=0,
        ))


def update_postseason(data: Brackets) -> None:
    for bracket, leagues in data.items():
        if bracket == "overbracket":
            layout["header"].update(Panel(
                Text(f"{leagues['name']} {leagues['round']}", justify="center")
            ))
        else:
            layout["footer"].update(Panel(
                Text(f"{leagues['name']} {leagues['round']}", justify="center")
            ))
        for subleague, games in leagues["games"].items():
            tables = []
            for game in games.values():
                table = Table.grid(expand=True)
                table.add_column("Seed", width=1)
                table.add_column("Name")
                table.add_column("Championships", style="#FFEB57", width=4)
                table.add_column("Wins", width=1)
                for row in game:
                    table.add_row(
                        row.seed,
                        f"[{row.color}]{row.name}[/]",
                        "●" * row.championships if row.championships < 4 else f"●x{row.championships}",
                        row.wins,
                    )
                tables.append(Layout(table))

            all_tables = Layout()
            all_tables.split(*tables)
            layout[bracket][subleague].update(Panel(
                all_tables,
                title=subleague,
                padding=0
            ))
