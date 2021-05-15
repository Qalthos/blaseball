#!/usr/bin/env python
import requests
from rich.live import Live
from rich.table import Table
from blaseball_mike import database

URL = "https://www.blaseball.com/api/getIdols"


def get_idols() -> tuple[list[str]]:
    resp = requests.get(URL).json()
    idols = resp["idols"][:resp["data"]["strictlyConfidential"] + 1]
    non_idols = resp["idols"][resp["data"]["strictlyConfidential"] + 1:]

    players = database.get_player(resp["idols"])
    return (
        [players[player]["name"] for player in idols],
        [players[player]["name"] for player in non_idols],
    )


def main() -> None:
    mvp, non_mvp = get_idols()

    for i, player in enumerate(mvp):
        print(f"{i + 1: 2.0f} {player}")
    print(r"\/\/\/\/\/\/\/\/\/")
    for j, player in enumerate(non_mvp):
        print(f"{i + j + 2: 2.0f} {player}")


if __name__ == "__main__":
    main()
