from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.game import SimData
from standings.postseason import Brackets
from standings.season import Prediction

BRACKETS = ("overbracket", "underbracket")

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
    Layout(name="footer"),
)
layout["header"].size = 1
layout["footer"].size = 1
layout["content"].split(
    Layout(name=BRACKETS[0]),
    Layout(name=BRACKETS[1]),
)
for bracket in BRACKETS:
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


def update_standings(data: Prediction, sim: SimData) -> None:
    layout["header"].update(
        Text(f"Season {sim.season + 1} Day {sim.day + 1}", justify="center")
    )
    for subleague, rows in data.items():
        teams = []
        for row in rows:

            wang = f"{row.wins - row.nonlosses:+}"

            closest = min(row.over, row.under)
            if closest < 0:
                postseason = ""
            elif closest > 99:
                postseason = "🃏"
            elif closest <= sim.day:
                postseason = "👑"
            else:
                postseason = str(closest)

            if row.party < 0:
                party = ""
            elif row.party > 99:
                party = "😐"
            elif row.party <= sim.day:
                party = "🥳"
            else:
                party = str(row.party)

            teams.append((
                row.division.split()[1][0],
                Text.assemble((row.name, row.color), f"[{row.tiebreaker}]"),
                clip_championships(row),
                f"{'*' if row.in_progress else ''}{row.wins}",
                wang,
                f"{row.nonlosses}-{row.losses}",
                party,
                postseason,
            ))

        for i, bracket in enumerate(BRACKETS):
            table = Table.grid(expand=True)
            table.add_column("Division", width=1)
            table.add_column("Name")
            table.add_column("Championships", width=2)
            table.add_column("Wins", width=3, justify="right")
            table.add_column("WANG", width=3, justify="right")
            table.add_column("Record", width=5, justify="right")
            table.add_column("Party", width=2, justify="right")
            table.add_column("Postseason", width=2, justify="right")
            slice_size = len(teams) // len(BRACKETS)
            for team in teams[i * slice_size:(i + 1) * slice_size]:
                table.add_row(*team)
            layout[bracket][subleague].update(Panel(
                table,
                title=subleague,
                padding=0,
            ))


def update_postseason(data: Brackets) -> None:
    for bracket, leagues in data.items():
        if bracket == "overbracket":
            layout["header"].update(
                Text(f"{leagues['name']} {leagues['round']}", justify="center")
            )
        else:
            layout["footer"].update(
                Text(f"{leagues['name']} {leagues['round']}", justify="center")
            )
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
