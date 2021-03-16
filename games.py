#!/usr/bin/env python3
import json
from datetime import datetime, timezone

from blaseball_mike import models

from party.teams import collect_records


def main():
    sim = models.SimulationData.load()
    teams, records = collect_records(sim.season)

    bundle = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "team_data": records,
        "teams": teams,
    }
    with open("/tmp/teams.json", "w") as json_file:
        json.dump(bundle, json_file, default=lambda o: o.to_tuple())


if __name__ == "__main__":
    main()
