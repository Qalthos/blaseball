#!/usr/bin/env python
import time

import requests
from blaseball_mike import database
from rich.console import RenderGroup
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

URL = "https://www.blaseball.com/api/getIdols"
PLAYER_URL = "https://www.blaseball.com/player"


def get_idols() -> tuple[list[str], list[str]]:
    resp = requests.get(URL).json()
    idols = resp["idols"][:resp["data"]["strictlyConfidential"] + 1]
    non_idols = resp["idols"][resp["data"]["strictlyConfidential"] + 1:]

    players = database.get_player(resp["idols"])
    return (
        [f"[link={PLAYER_URL}/{player}]{players[player]['name']}[/link]" for player in idols],
        [f"[link={PLAYER_URL}/{player}]{players[player]['name']}[/link]" for player in non_idols],
    )


def format_row(index: int, player: str, previous: list[str]) -> tuple[str, str, str]:
    last = ""
    if player != previous[index]:
        try:
            last_index = previous.index(player)
            if last_index > index:
                last = f"[green]▲{last_index - index}[/]"
            else:
                last = f"[red]▼{index - last_index}[/]"
        except ValueError:
            last = "->"
        player = f"[yellow]{player}"

    return (last, f"{index + 1}", player)


def main() -> None:
    previous: list[str] = [""] * 20
    with Live() as live:
        while True:
            mvp, non_mvp = get_idols()

            above = Table.grid(expand=True)
            above.add_column(width=2)
            above.add_column(width=3)
            above.add_column()
            for i, player in enumerate(mvp):
                above.add_row(*format_row(i, player, previous))

            noodle = r"[yellow]\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"

            below = Table.grid(expand=True)
            below.add_column(width=2)
            below.add_column(width=3)
            below.add_column()
            for j, player in enumerate(non_mvp):
                below.add_row(*format_row(i + j + 1, player, previous))

            live.update(Panel(RenderGroup(above, noodle, below)))
            previous = mvp + non_mvp
            time.sleep(30)


if __name__ == "__main__":
    main()
