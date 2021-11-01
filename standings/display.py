from rich.columns import Columns
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.game import SimData
from standings.postseason import PlayoffStandings
from standings.season import Prediction

TEAM_URL = "[{color}][link=https://www.blaseball.com/team/{id!s}]{name}[/]"

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
)
layout["header"].size = 1


def clip_championships(row) -> str:
    champs = row.championships % 3, row.underchampionships % 3
    if sum(champs) == 3:
        champs = (0, 0)
    elif sum(champs) == 4:
        if champs[0]:
            champs = (1, 0)
        else:
            champs = (0, 1)
    championships = ""
    if champs[0]:
        championships += f"[#FFEB57]{'●' * champs[0]}"
    if champs[1]:
        championships += f"{' ' * (2 - sum(champs))}[#A16DC3]{'●' * champs[1]}"

    return championships


def update_standings(data: Prediction, sim: SimData) -> None:
    layout["header"].update(
        Text(f"Season {sim.season + 1} Day {sim.day + 1}", justify="center")
    )
    widgets = []
    for subleague, rows in data.items():
        table = Table.grid(padding=(0, 1), expand=True)
        table.add_column("Division", width=1)
        table.add_column("Tiebreaker", width=2, justify="right")
        table.add_column("Name")
        table.add_column("Championships", width=2)
        table.add_column("Wins", width=3, justify="right")
        table.add_column("WANG", width=3, justify="right")
        table.add_column("Record", width=5, justify="right")
        table.add_column("Postseason", width=2, justify="right")
        for row in rows:

            wang = f"{row.wins - row.nonlosses:+}"

            postseason = str(row.over)
            if row.over < 0 or row.over > 99:
                postseason = ""
            elif row.over <= sim.day:
                postseason = "👑"

            table.add_row(
                # First word in the division is the Subleague again, skip it
                row.division.split(" ", 1)[1][0],
                str(row.tiebreaker),
                TEAM_URL.format(name=row.name, id=row.id, color=row.color),
                clip_championships(row),
                f"{'*' if row.in_progress else ''}{row.wins}",
                wang,
                f"{row.nonlosses}-{row.losses}",
                postseason,
            )

        widgets.append(Panel(
            table,
            title=subleague,
            padding=0,
        ))
    layout["content"].update(Columns(widgets, expand=True))


def update_postseason(data: PlayoffStandings) -> None:
    layout["header"].update(
        Text(f"{data['name']} {data['round']}", justify="center")
    )
    for subleague, games in data["games"].items():
        tables = []
        for game in games.values():
            table = Table.grid(expand=True)
            table.add_column("Seed", width=1)
            table.add_column("Name")
            table.add_column("Championships", width=2)
            table.add_column("Wins", width=1)
            for row in game:
                table.add_row(
                    str(row.seed),
                    f"[{row.color}]{row.name}[/]",
                    clip_championships(row),
                    str(row.wins),
                )
            tables.append(Layout(table))

        all_tables = Layout()
        all_tables.split(*tables)
        layout[subleague].update(Panel(
            all_tables,
            title=subleague,
            padding=0
        ))
