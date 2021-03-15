from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

from blaseball_mike import models

from party.models.league import League
from party.models.subleague import Subleague
from party.models.team import Team


class Row(NamedTuple):
    badge: str
    name: str
    color: str
    tiebreaker: int
    championships: int
    in_progress: bool
    wins: int
    record: str
    earliest: int
    estimate: Optional[str]


Prediction = Dict[str, List[Optional[Row]]]


def get_standings(season: int) -> models.Standings:
    return models.Season.load(season_number=season).standings


def get_league(league_id: str) -> League:
    league = models.League.load_by_id(id_=league_id)
    tiebreakers = next(iter(league.tiebreakers.values()))
    return League.load(league, tiebreakers=list(tiebreakers.order))


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

    return Row(
        badge=badge,
        name=team.name,
        color=team.color,
        tiebreaker=team.tiebreaker,
        championships=team.championships,
        in_progress=bool(team.games_played < (day + 1) < 100),
        wins=team.wins,
        record=team.record,
        earliest=needed + (99 - day + 1) // 2,
        estimate=trophy or str(estimate) if estimate > 33 else None,
    )


def get_game_data(season: int, day: int, league: League) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    standings = get_standings(season)
    league.update(standings)

    predictions: Prediction = defaultdict(list)
    for subleague in league.subleagues:

        for team in subleague.playoff_teams:
            predictions[subleague.name].append(format_row(league, subleague, team, day))
        predictions[subleague.name].append(None)
        for team in subleague.remainder:
            predictions[subleague.name].append(format_row(league, subleague, team, day))

    return predictions
