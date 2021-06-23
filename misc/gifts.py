#!/usr/bin/env python
import sys
import time
from typing import Any

import requests
from rich.progress import Progress, BarColumn

URL = "https://www.blaseball.com/database/giftProgress"


def read_gift() -> dict[str, Any]:
    try:
        data = requests.get(URL).json()
    except requests.exceptions.ConnectionError:
        # Uh-oh, retry?
        time.sleep(10)
        return read_gift()

    team_id = sys.argv[1]
    wishes = sorted([
        (float(gift["percent"]), gift["bonus"])
        for gift in data["teamWishLists"][team_id]
    ], reverse=True)
    return {
        "complete": data["teamProgress"][team_id]["total"],
        "progress": data["teamProgress"][team_id]["toNext"],
        "items": wishes,
    }


def update(progress: Progress, overall: int, items: dict[str, tuple[int, str]], stats: dict[str, Any]) -> None:
    progress.update(
        overall,
        description=f"{stats['complete']} Gifts Obtained",
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
        stats = read_gift()
        overall = progress.add_task(f"{stats['complete']} Gifts Obtained", total=1)
        gifts = {}
        for gift in stats["items"]:
            gifts[gift[1]] = progress.add_task(gift[1], total=1)
        while True:
            update(progress, overall, gifts, read_gift())

            try:
                time.sleep(60)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
