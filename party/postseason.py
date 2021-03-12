import copy
from typing import TypedDict

from blaseball_mike import models
from rich.table import Table
from rich.text import Text

Prediction = TypedDict(
    "Prediction",
    {
        "league": str,
        "name": str,
        "day": int,
        "games": dict[str, Table],
    },
)


def subleague_for_team(subleagues: list[models.Subleague], team: models.Team) -> models.Subleague:
    for subleague in subleagues:
        if team in subleague.teams.values():
            return subleague
    raise KeyError("Can't find subleague for team")


def get_playoffs(sim_data: models.SimulationData) -> Prediction:
    playoff = models.Playoff.load_by_season(sim_data.season)
    subleagues = sim_data.league.subleagues.values()

    tables = {}
    for subleague in subleagues:
        games = Table.grid(expand=True, padding=(0, 1))
        games.add_column("Seed", width=1)
        games.add_column("Name")
        games.add_column("Wins", width=1)
        tables[subleague.name] = games

    for round in playoff.rounds:
        for matchup in round.matchups:
            if matchup.away_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.away_team)
                except KeyError:
                    continue
                tables[subleague.name].add_row(
                    str(matchup.away_seed + 1),
                    Text(matchup.away_team.nickname, style=matchup.away_team.main_color),
                    str(matchup.away_wins),
                )
            if matchup.home_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.home_team)
                except KeyError:
                    continue
                tables[subleague.name].add_row(
                    str(matchup.home_seed + 1),
                    Text(matchup.home_team.nickname, style=matchup.home_team.main_color),
                    str(matchup.home_wins)
                )
            tables[subleague.name].add_row()

    game_data: Prediction = {
        "league": sim_data.league.name,
        "name": playoff.name,
        "day": sim_data.day + 1,
        "games": tables,
    }
    return game_data
