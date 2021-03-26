#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

from blaseball_mike import models

from party import teams


def main(season_no=None):
    if season_no is None:
        sim = models.SimulationData.load()
        season_no = sim.season

    teams, records = teams.collect_records(season_no)
    json_path = Path("/srv/blaseball")

    bundle = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "season": season_no,
        "team_data": records,
        "teams": teams,
    }
    json_file_path = json_path / f"teams.{season_no}.json"
    with open(json_file_path, "w") as json_file:
        json.dump(bundle, json_file, default=lambda o: o.to_json())

    if season_no is not None:
        # Atomically replace existing symlink
        temp_link = json_path / "teams.tmp"
        temp_link.unlink(missing_ok=True)
        temp_link.symlink_to(json_file_path)
        final_link = json_path / "teams.json"
        temp_link.replace(final_link)


if __name__ == "__main__":
    main()
