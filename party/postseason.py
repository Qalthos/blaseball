from collections import defaultdict
from typing import Dict, List, NamedTuple, TypedDict

from blaseball_mike import models


class Row(NamedTuple):
    seed: str
    name: str
    color: str
    wins: str


Games = Dict[str, Dict[str, List[Row]]]


class PlayoffStandings(TypedDict):
    name: str
    round: str
    games: Games


def subleague_for_team(subleagues: List[models.Subleague], team: models.Team) -> str:
    for subleague in subleagues:
        if team in subleague.teams.values():
            return subleague.name
    raise KeyError("Can't find subleague for team")


def get_playoffs(sim_data: models.SimulationData) -> PlayoffStandings:
    playoff = models.Playoff.load_by_season(sim_data.season)
    subleagues = sim_data.league.subleagues.values()

    games: Games
    current_round: models.PlayoffRound
    for playoff_round in playoff.rounds:
        if not playoff_round.games:
            break

        current_round = playoff_round
        games = {subleague.name: defaultdict(list) for subleague in subleagues}
        for matchup in current_round.matchups:
            if matchup.away_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.away_team)
                except KeyError:
                    continue
                games[subleague][matchup.id].append(Row(
                    seed=str(matchup.away_seed + 1),
                    name=matchup.away_team.nickname,
                    color=matchup.away_team.main_color,
                    wins=str(matchup.away_wins),
                ))
            if matchup.home_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.home_team)
                except KeyError:
                    continue
                games[subleague][matchup.id].append(Row(
                    seed=str(matchup.home_seed + 1),
                    name=matchup.home_team.nickname,
                    color=matchup.home_team.main_color,
                    wins=str(matchup.home_wins),
                ))

    game_data: PlayoffStandings = {
        "name": playoff.name,
        "round": current_round.name,
        "games": games,
    }
    return game_data
