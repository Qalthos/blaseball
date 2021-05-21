#!/usr/bin/env python
import sys
import time
from typing import Any

import requests
from rich.progress import Progress

URL = "https://www.blaseball.com/database/renovationProgress"


def read_reno() -> dict[str, Any]:
    try:
        data = requests.get(URL, params={"id": sys.argv[1]}).json()
    except requests.exceptions.ConnectionError:
        # Uh-oh, retry?
        time.sleep(10)
        return read_reno()

    mods = sorted([
        (float(mod["percent"]), mod["id"])
        for mod in data["stats"]
    ], reverse=True)
    return {
        "renos": data["progress"]["total"],
        "progress": data["progress"]["toNext"],
        "mods": mods,
    }


def extrapolate():
    data = read_reno()
    locked = sum(4**i for i in range(data["renos"])) * 1000000
    next = 4**data["renos"] * 1000000
    complete = next * data["progress"]
    print(f"{next - complete:,.0f} needed for next renovation")
    for mod in data["mods"]:
        try:
            estimate = (locked + complete) * mod[0] / 100
        except ZeroDivisionError:
            estimate = 0
        print(f"{mod[1]}: {estimate:,.0f} coins")


def update(progress: Progress, overall: int, mods: dict[str, tuple[int, str]], stats: dict[str, Any]) -> None:
    progress.update(
        overall,
        description=f"{stats['renos']} Renovations Complete",
        completed=stats["progress"],
    )
    for mod in stats["mods"]:
        progress.update(
            mods[mod[1]],
            completed=mod[0],
        )


def main() -> None:
    with Progress() as progress:
        stats = read_reno()
        overall = progress.add_task(f"{stats['renos']} Reonovations Complete", total=1)
        mods = {}
        for mod in stats["mods"]:
            mods[mod[1]] = progress.add_task(mod[1])
        while True:
            update(progress, overall, mods, read_reno())

            try:
                time.sleep(60)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
