from collections import defaultdict
from typing import Dict, List, NamedTuple

from blaseball_mike import models

from party.models.subleague import Subleague
from party.models.team import Team


class Row(NamedTuple):
    badge: str
    name: str
    color: str
    tiebreaker: str
    championships: str
    wins: str
    record: str
    estimate: str


Prediction = Dict[str, List[Row]]


def get_standings(season: int) -> models.Standings:
    return models.Season.load(season_number=season).standings


def get_subleagues(league_id: str) -> List[Subleague]:
    league = models.League.load_by_id(id_=league_id)
    tiebreakers = next(iter(league.tiebreakers.values()))

    subleagues = []
    for subleague_id in league.subleagues:
        subleagues.append(Subleague.load(
            id_=subleague_id,
            tiebreakers=list(tiebreakers.order),
        ))
    return subleagues


def format_row(subleague: Subleague, team: Team, day: int) -> Row:
    playoff = subleague.playoff_teams
    if team in playoff:
        needed = team - subleague.cutoff
        estimate = team.estimate_party_time(needed)
        badge = "H" if team == playoff.high else "L" if team == playoff.low else "*"
        trophy = "🏆" if needed > (99 - subleague.cutoff.games_played) or estimate < day else ""
    else:
        needed = playoff.cutoff - team
        estimate = team.estimate_party_time(needed)
        badge = ""
        trophy = "🥳" if needed > (99 - team.games_played) or estimate < day else ""

    star = "*" if team.games_played < (day + 1) < 100 else " "
    championships = "●" * team.championships if team.championships < 4 else f"●*{team.championships}"
    return Row(
        badge,
        team.name,
        team.color,
        f"[{team.tiebreaker}]",
        championships,
        f"{star}{team.wins}",
        team.record,
        trophy or str(estimate),
    )


def get_game_data(season: int, day: int, subleagues: List[Subleague]) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    standings = get_standings(season)

    predictions: Prediction = defaultdict(list)
    for subleague in subleagues:
        subleague.update(standings)

        for team in subleague.playoff_teams:
            predictions[subleague.name].append(format_row(subleague, team, day))
        predictions[subleague.name].append(Row("", "", "", "", "", "", "", ""))
        for team in subleague.remainder:
            predictions[subleague.name].append(format_row(subleague, team, day))

    return predictions
