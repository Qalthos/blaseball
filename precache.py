#!/usr/bin/env python3
import json
from datetime import datetime, timezone

from blaseball_mike import models

from party import season


def main():
    sim = models.SimulationData.load()
    league = season.get_league(sim.league.id)
    standings = season.get_game_data(sim.season, sim.day, league)

    bundle = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "league": sim.league.name,
        "season": sim.season,
        "standings": standings,
    }
    with open("/tmp/standings.json", "w") as json_file:
        json.dump(bundle, json_file)


if __name__ == "__main__":
    main()
