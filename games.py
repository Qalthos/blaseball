#!/usr/bin/env python3
import json

from blaseball_mike import models

from party.teams import collect_records


def main():
    sim = models.SimulationData.load()
    records = collect_records(sim.season)

    with open("/tmp/teams.json", "w") as json_file:
        json.dump(records, json_file, default=lambda o: o.to_tuple())


if __name__ == "__main__":
    main()
