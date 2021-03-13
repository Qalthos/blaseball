from typing import TypedDict

from blaseball_mike import database, models
from rich.table import Table
from rich.text import Text

from party.models.subleague import Subleague
from party.models.team import Team

Prediction = TypedDict(
    "Prediction",
    {
        "league": str,
        "season": int,
        "day": int,
        "predictions": dict[str, Table],
    },
)


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


def format_row(subleague: Subleague, team: Team, day: int) -> tuple[str, Text, str, str, str, str]:
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
    return (
        badge,
        Text.assemble((team.name, team.color), f"[{team.tiebreaker}]"),
        championships,
        f"{star}{team.wins}",
        team.record,
        trophy or str(estimate),
    )
    pass


def get_game_data(sim_data: models.SimulationData, subleagues: list[Subleague]) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    standings = get_standings(sim_data.season)

    predictions: dict[str, list[str]] = {}
    for subleague in subleagues:
        subleague.update(standings)

        teams = Table.grid(expand=True)
        teams.add_column("Flag", width=1)
        teams.add_column("Name")
        teams.add_column("Championships", style="#ffeb57")
        teams.add_column("Wins", width=4, justify="right")
        teams.add_column("Record", width=6, justify="right")
        teams.add_column("Estimate", width=3, justify="right")

        for team in subleague.playoff_teams:
            teams.add_row(*format_row(subleague, team, sim_data.day))
        teams.add_row()
        for team in subleague.remainder:
            teams.add_row(*format_row(subleague, team, sim_data.day))

        predictions[subleague.name] = teams

    game_data: Prediction = {
        "league": sim_data.league.name,
        "season": sim_data.season,
        "day": sim_data.day + 1,
        "predictions": predictions,
    }
    return game_data
