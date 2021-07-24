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


def update_standings(data: Prediction, day: int) -> None:
    for subleague, rows in data.items():
        teams = Table.grid(expand=True)
        teams.add_column("Division", width=1)
        teams.add_column("Name")
        teams.add_column("Championships", width=2)
        teams.add_column("Wins", width=3, justify="right")
        teams.add_column("WANG", width=3, justify="right")
        teams.add_column("Record", width=5, justify="right")
        teams.add_column("Party", width=2, justify="right")
        teams.add_column("Postseason", width=2, justify="right")
        for row in rows:

            wang = f"{row.wins - row.nonlosses:+}"

            closest = min(row.over, row.under)
            if closest < day:
                postseason = "👑"
            elif closest > 99:
                postseason = "🃏"
            else:
                postseason = str(closest)

            if row.party < day:
                party = "🥳"
            elif row.party > 99:
                party = "😐"
            else:
                party = str(row.party)

            teams.add_row(
                row.division.split()[1][0],
                Text.assemble((row.name, row.color), f"[{row.tiebreaker}]"),
                clip_championships(row),
                f"{'*' if row.in_progress else ''}{row.wins}",
                wang,
                f"{row.nonlosses}-{row.losses}",
                party,
                postseason,
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
            layout[bracket][subleague].update(Panel(
                all_tables,
                title=subleague,
                padding=0
            ))
