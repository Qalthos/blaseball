#!/usr/bin/env python
import time

import requests
from blaseball_mike import database
from rich.console import RenderGroup
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

URL = "https://www.blaseball.com/api/getIdols"


def get_idols() -> tuple[list[str], list[str]]:
    resp = requests.get(URL).json()
    idols = resp["idols"][:resp["data"]["strictlyConfidential"] + 1]
    non_idols = resp["idols"][resp["data"]["strictlyConfidential"] + 1:]

    players = database.get_player(resp["idols"])
    return (
        [players[player]["name"] for player in idols],
        [players[player]["name"] for player in non_idols],
    )


def main() -> None:
    with Live() as live:
        while True:
            mvp, non_mvp = get_idols()

            above = Table.grid(expand=True)
            above.add_column(width=3)
            above.add_column()
            for i, player in enumerate(mvp):
                above.add_row(f"{i + 1}", player)

            noodle = r"\/\/\/\/\/\/\/\/\/"

            below = Table.grid(expand=True)
            below.add_column(width=3)
            below.add_column()
            for j, player in enumerate(non_mvp):
                below.add_row(f"{i + j + 2}", player)

            live.update(Panel(RenderGroup(above, noodle, below)))
            time.sleep(30)


if __name__ == "__main__":
    main()
