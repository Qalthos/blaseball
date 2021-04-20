import sys
import time
from typing import Any

import requests
from rich.progress import Progress

URL = "https://www.blaseball.com/database/renovationProgress"


def read_reno() -> dict[str, Any]:
    data = requests.get(URL, params={"id": sys.argv[1]}).json()

    mods = sorted([
        (float(mod["percent"]), mod["id"])
        for mod in data["stats"]
    ], reverse=True)
    return {
        "renos": data["progress"]["total"],
        "progress": data["progress"]["toNext"],
        "mods": mods,
    }


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
