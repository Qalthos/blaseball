#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

from blaseball_mike import models

from party import season


def main(season_no=None):
    sim = models.SimulationData.load()
    if season_no is None:
        season_no = sim.season
        day_no = sim.day
    else:
        day_no = 99

    league = season.get_league(sim.league.id)
    standings = season.get_game_data(season_no, day_no, league)
    json_path = Path("/srv/blaseball")

    bundle = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "league": sim.league.name,
        "season": season_no,
        "standings": standings,
    }
    json_file_path = json_path / f"standings.{season_no}.json"
    with open(json_file_path, "w") as json_file:
        json.dump(bundle, json_file)

    if season_no is not None:
        # Atomically replace existing symlink
        temp_link = json_path / "standings.tmp"
        temp_link.unlink(missing_ok=True)
        temp_link.symlink_to(json_file_path)
        final_link = json_path / "standings.json"
        temp_link.replace(final_link)


if __name__ == "__main__":
    main()
