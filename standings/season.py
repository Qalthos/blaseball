from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

from models.game import GamesData
from models.league import League, LeagueData, Subleague
from models.team import Team


class Row(NamedTuple):
    badge: str
    name: str
    color: str
    tiebreaker: int
    championships: int
    in_progress: bool
    wins: int
    record: str
    earliest: str
    estimate: Optional[str]
    id: str


Prediction = Dict[str, List[Optional[Row]]]


def format_row(league: League, subleague: Subleague, team: Team, day: int) -> Row:
    playoff = subleague.playoff_teams
    if team in playoff:
        needed = team - subleague.cutoff
        estimate = team.estimate_party_time(needed)
        badge = "H" if team == playoff.high else "L" if team == playoff.low else "*"
        trophy = "🏆" if needed > (99 - subleague.cutoff.games_played) or estimate < day else ""
    else:
        needed = playoff.cutoff - team
        estimate = team.estimate_party_time(needed)
        badge = "▼" if team in league.bottom_four else ""
        trophy = "🥳" if needed > (99 - team.games_played) or estimate < day else ""

    earliest = team.games_played + (99 - team.games_played - needed) // 2 + 1

    return Row(
        id=str(team.id),
        badge=badge,
        name=team.name,
        color=team.color,
        tiebreaker=team.tiebreaker,
        championships=team.championships,
        in_progress=bool(team.games_played < (day + 1) < 100),
        wins=team.wins,
        record=team.record,
        earliest=str(earliest) if earliest > team.games_played else "N/A",
        estimate=trophy or str(estimate) if estimate > 33 else None,
    )


def get_standings(game_data: GamesData, league: LeagueData) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    predictions: Prediction = defaultdict(list)
    for subleague in league.subleagues:

        for team in subleague.playoff_teams:
            predictions[subleague.name].append(format_row(league, subleague, team, game_data.sim.day))
        predictions[subleague.name].append(None)
        for team in subleague.remainder:
            predictions[subleague.name].append(format_row(league, subleague, team, game_data.sim.day))

    return predictions
