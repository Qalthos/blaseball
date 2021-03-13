from collections import defaultdict, namedtuple

from blaseball_mike import database, models

from party.models.subleague import Subleague
from party.models.team import Team

Row = namedtuple(
    "Row",
    [
        "badge",
        "name",
        "color",
        "tiebreaker",
        "championships",
        "wins",
        "record",
        "estimate"
    ]
)
Prediction = dict[str, list[Row]]


def get_standings(season: int) -> models.Standings:
    return models.Season.load(season_number=season).standings


def get_subleagues(league: models.League) -> list[Subleague]:
    all_teams = database.get_all_teams()
    tiebreakers = next(iter(league.tiebreakers.values()))

    subleagues = []
    for subleague_id in league.subleagues:
        subleagues.append(Subleague.load(
            id_=subleague_id,
            all_teams=all_teams,
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
    pass


def get_game_data(sim_data: models.SimulationData, subleagues: list[Subleague]) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    standings = get_standings(sim_data.season)

    predictions: Prediction = defaultdict(list)
    for subleague in subleagues:
        subleague.update(standings)

        for team in subleague.playoff_teams:
            predictions[subleague.name].append(format_row(subleague, team, sim_data.day))
        predictions[subleague.name].append(Row("", "", "", "", "", "", "", ""))
        for team in subleague.remainder:
            predictions[subleague.name].append(format_row(subleague, team, sim_data.day))

    return predictions
