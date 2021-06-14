from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

from blaseball_mike import models

from party.models.league import League
from party.models.subleague import Subleague
from party.models.team import Team


class Row(NamedTuple):
    # Team metadata
    id: str
    name: str
    color: str
    division: str

    # Season data
    championships: int
    wins: int
    tiebreaker: int
    losses: int
    games_played: int
    in_progress: bool

    # Outcome predictions
    playoff: int  # 1 for Overbracket, -1 for Underbracket, 0 otherwise
    wills: bool
    earliest: str
    estimate: Optional[str]


Prediction = Dict[str, List[Optional[Row]]]


def get_standings(season: int) -> models.Standings:
    return models.Season.load(season_number=season).standings


def get_league(league_id: str) -> League:
    league = models.League.load_by_id(id_=league_id)
    tiebreakers = next(iter(league.tiebreakers.values()))
    return League.load(league, tiebreakers=list(tiebreakers.order))


def format_row(league: League, subleague: Subleague, team: Team, day: int) -> Row:
    overbracket, underbracket = subleague.playoff_teams
    playoff_state = 0
    if team in overbracket:
        playoff_state = 1
        needed = team - subleague.cutoff
        estimate = team.estimate_party_time(needed)
        trophy = "🏆" if needed > (99 - subleague.cutoff.games_played) or estimate < day else ""
    elif team in underbracket:
        playoff_state = -1
        needed = team - subleague.cutoff
        estimate = team.estimate_party_time(needed)
        trophy = "🏆" if needed > (99 - subleague.cutoff.games_played) or estimate < day else ""
    else:
        needed = overbracket.cutoff - team
        estimate = team.estimate_party_time(needed)
        trophy = "🥳" if needed > (99 - team.games_played) or estimate < day else ""

    earliest = team.games_played + (99 - team.games_played - needed) // 2 + 1

    return Row(
        id=team.id,
        name=team.name,
        color=team.color,
        division=subleague.get_division(team),
        championships=team.championships,
        wins=team.wins,
        tiebreaker=team.tiebreaker,
        losses=team.losses,
        games_played=team.games_played,
        in_progress=bool(team.games_played < (day + 1) < 100),
        playoff=playoff_state,
        wills=bool(team in league.bottom_four),
        earliest=str(earliest) if earliest > team.games_played else "N/A",
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
