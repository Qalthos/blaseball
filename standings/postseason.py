from collections import defaultdict
from typing import Dict, List, NamedTuple, TypedDict

from models.game import GamesData
from models.league import LeagueData

BRACKETS = ("overbracket", "underbracket")


class Row(NamedTuple):
    seed: str
    name: str
    color: str
    championships: int
    wins: str


Games = Dict[str, Dict[str, List[Row]]]


class PlayoffStandings(TypedDict):
    name: str
    round: str
    games: Games


Brackets = dict[str, PlayoffStandings]


def get_playoffs(game_data: GamesData, league: LeagueData) -> Brackets:
    brackets: Brackets = {}
    for bracket, postseason in zip(BRACKETS, game_data.postseasons):
        games: Games = {subleague.name: defaultdict(list) for subleague in league.subleagues}
        for matchup in postseason.matchups:
            if matchup.away_team and matchup.away_seed:
                try:
                    away_team = league.get_team(matchup.away_team)
                    subleague = league.get_team_subleague(matchup.away_team)
                except KeyError:
                    continue
                games[subleague.name][str(matchup.id)].append(Row(
                    seed=str(matchup.away_seed + 1),
                    name=away_team.nickname,
                    color=away_team.main_color,
                    championships=away_team.championships,
                    wins=str(matchup.away_wins),
                ))
            if matchup.home_team and matchup.home_seed:
                try:
                    home_team = league.get_team(matchup.home_team)
                    subleague = league.get_team_subleague(matchup.home_team)
                except KeyError:
                    continue
                games[subleague.name][str(matchup.id)].append(Row(
                    seed=str(matchup.home_seed + 1),
                    name=home_team.nickname,
                    color=home_team.main_color,
                    championships=home_team.championships,
                    wins=str(matchup.home_wins),
                ))

        brackets[bracket] = {
            "name": postseason.playoffs.name,
            "round": postseason.round.name,
            "games": games,
        }

    return brackets
