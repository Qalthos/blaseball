#!/usr/bin/env python
import sys
import time
from typing import Any

import requests
from rich.progress import BarColumn, Progress

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
        "complete": data["progress"]["total"],
        "progress": data["progress"]["toNext"],
        "items": mods,
    }


def update(progress: Progress, overall: int, items: dict[str, tuple[int, str]], stats: dict[str, Any]) -> None:
    progress.update(
        overall,
        description=f"{stats['complete']} Renovations Complete",
        completed=stats["progress"],
    )
    for item in stats["items"]:
        progress.update(
            items[item[1]],
            completed=item[0],
        )


def main() -> None:
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    )
    with progress:
        stats = read_reno()
        overall = progress.add_task(f"{stats['complete']} Reonovations Complete", total=1)
        mods = {}
        for mod in stats["items"]:
            mods[mod[1]] = progress.add_task(mod[1])
        while True:
            update(progress, overall, mods, read_reno())

            try:
                time.sleep(60)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
