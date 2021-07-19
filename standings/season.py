from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

from models.game import GamesData, Standings
from models.league import League, LeagueData, Subleague, Tiebreakers
from models.team import Team


class Row(NamedTuple):
    badge: str
    name: str
    color: str
    tiebreaker: int
    championships: int
    in_progress: bool
    wins: int
    losses: int
    nonlosses: int
    earliest: str
    estimate: Optional[str]
    id: str


Prediction = Dict[str, List[Optional[Row]]]


def format_row(team: Team, day: int, standings: Standings, tiebreaker: Tiebreakers) -> Row:
    games_played = standings.games_played[team.id]
    losses = standings.losses[team.id]
    return Row(
        id=str(team.id),
        name=team.nickname,
        color=team.main_color.as_hex(),
        championships=team.championships % 3,
        in_progress=bool(games_played < (day + 1) < 100),
        wins=standings.wins[team.id],
        losses=losses,
        nonlosses=games_played - losses,
        badge="",
        tiebreaker=tiebreaker.order.index(team.id) + 1,
        earliest="",
        estimate="",
    )


def teams_in_subleague(subleague: Subleague, league: LeagueData) -> list[Team]:
    return [
        t
        for d in league.divisions if d.id in subleague.divisions
        for t in league.teams if t.id in d.teams
    ]


def sort_teams(teams: list[Team], standings: Standings, tiebreakers: Tiebreakers) -> list[Team]:
    return sorted(
        teams,
        key=lambda t: (
            standings.wins[t.id],
            -tiebreakers.order.index(t.id),
        ),
        reverse=True,
    )


def get_standings(game_data: GamesData, league: LeagueData) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    tiebreaker = league.tiebreakers[-1]
    predictions: Prediction = defaultdict(list)
    for subleague in league.subleagues:
        subleague_teams = teams_in_subleague(subleague, league)
        subleague_teams = sort_teams(subleague_teams, game_data.standings, tiebreaker)
        for team in subleague_teams:
            predictions[subleague.name].append(format_row(team, game_data.sim.day, game_data.standings, tiebreaker))

    return predictions
