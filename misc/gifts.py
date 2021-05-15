import sys
import time
from typing import Any

import requests
from rich.progress import Progress

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
        "gifts": data["teamProgress"][team_id]["total"],
        "progress": data["teamProgress"][team_id]["toNext"],
        "wishlist": wishes,
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
        description=f"{stats['gifts']} Gifts Obtained",
        completed=stats["progress"],
    )
    for mod in stats["wishlist"]:
        progress.update(
            mods[mod[1]],
            completed=mod[0],
        )


def main() -> None:
    with Progress() as progress:
        stats = read_gift()
        overall = progress.add_task(f"{stats['gifts']} Gifts Obtained", total=1)
        gifts = {}
        for gift in stats["wishlist"]:
            gifts[gift[1]] = progress.add_task(gift[1], total=1)
        while True:
            update(progress, overall, gifts, read_gift())

            try:
                time.sleep(60)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
