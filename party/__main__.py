from typing import List

import requests
from pydantic import parse_obj_as

from party import display, season
from party.models.sim import Sim
from party.models.team import Team

API_BASE = "https://api2.sibr.dev/mirror/"


def main() -> None:
    # Pull data
    sim = requests.get(API_BASE + "sim").json()
    sim = parse_obj_as(Sim, sim)
    teams = requests.get(API_BASE + "teams").json()
    teams = parse_obj_as(List[Team], teams)

    # Calcualte positions
    predictions = season.make_predictions(sim, teams)
    display.update_standings(
        f"{sim.simData.currentLeagueData.name} Season {sim.simData.currentSeasonNumber + 1} Day {sim.simData.currentDay + 1}",
        predictions,
    )
    print(display.layout)


if __name__ == "__main__":
    display.display_loop(main)
