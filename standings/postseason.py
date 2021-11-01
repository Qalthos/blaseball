from collections import defaultdict
from typing import Dict, List, NamedTuple, TypedDict

from blaseball_mike.models import Subleague, Team
from blaseball_mike.stream_model import StreamGames, StreamLeagues


class Row(NamedTuple):
    seed: int
    name: str
    color: str
    championships: int
    underchampionships: int
    wins: int


Games = Dict[str, Dict[str, List[Row]]]


class PlayoffStandings(TypedDict):
    name: str
    round: str
    games: Games


def get_team(league_data: StreamLeagues, team_id: str) -> Team:
    for team in league_data.teams:
        if team.id == team_id:
            return team
    raise ValueError(f"Team {team_id!s} not found")


def get_team_subleague(league_data: StreamLeagues, team_id: str) -> Subleague:
    for subleague in league_data.subleagues:
        for division in league_data.divisions:
            if division.id not in subleague.divisions:
                continue
            if team_id in division.teams:
                return subleague
    raise ValueError(f"Team {team_id!s} not found")


def get_playoffs(game_data: StreamGames, league_data: StreamLeagues) -> PlayoffStandings:
    postseason = game_data.postseason
    games: Games = {
        subleague.name: defaultdict(list)
        for subleague in league_data.subleagues
    }
    for matchup in postseason.matchups:
        if matchup.away_team and matchup.away_seed is not None:
            try:
                away_team = get_team(league_data, matchup.away_team)
                subleague = get_team_subleague(league_data, matchup.away_team)
            except KeyError:
                pass
            else:
                games[subleague.name][str(matchup.id)].append(Row(
                    seed=matchup.away_seed + 1,
                    name=away_team.nickname,
                    color=away_team.main_color,
                    championships=away_team.championships,
                    underchampionships=away_team.underchampionships,
                    wins=matchup.away_wins,
                ))
        if matchup.home_team and matchup.home_seed is not None:
            try:
                home_team = get_team(league_data, matchup.home_team)
                subleague = get_team_subleague(league_data, matchup.home_team)
            except KeyError:
                pass
            else:
                games[subleague.name][str(matchup.id)].append(Row(
                    seed=matchup.home_seed + 1,
                    name=home_team.nickname,
                    color=home_team.main_color,
                    championships=home_team.championships,
                    underchampionships=home_team.underchampionships,
                    wins=matchup.home_wins,
                ))

    return {
        "name": postseason.playoffs.name,
        "round": postseason.round.name,
        "games": games,
    }

