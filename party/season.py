from typing import TypedDict

from blaseball_mike import database, models
from rich.table import Table
from rich.text import Text

from party.models.subleague import Subleague

Prediction = TypedDict(
    "Prediction",
    {
        "league": str,
        "season": int,
        "day": int,
        "predictions": dict[str, Table],
    }
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


def get_game_data(sim_data: models.SimulationData, subleagues: list[Subleague]) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    standings = get_standings(sim_data.season)

    predictions: dict[str, list[str]] = {}
    for subleague in subleagues:
        subleague.update(standings)
        teams = Table.grid(expand=True, padding=(0, 1))
        teams.add_column("Flag", width=1)
        teams.add_column("Name")
        teams.add_column("Championships", style="#ffeb57")
        teams.add_column("Wins", max_width=3, justify="right")
        teams.add_column("Record", max_width=5)
        # teams.add_column("Distance", max_width=5)
        teams.add_column("Estimate", width=2)
        playoff = subleague.playoff_teams
        for team in playoff:
            needed = team - subleague.cutoff
            estimate = team.estimate_party_time(needed)
            badge = "H" if team == playoff.high else "L" if team == playoff.low else "*"
            star = "*" if team.games_played < (sim_data.day + 1) else " "
            championships = "●" * team.championships if team.championships < 4 else f"●*{team.championships}"
            trophy = "🏆" if needed > (99 - subleague.cutoff.games_played) or estimate < sim_data.day else ""
            teams.add_row(
                badge,
                Text.assemble((team.name, team.color), f"[{team.tiebreaker}]"),
                championships,
                f"{team.wins}{star}",
                team.record,
                trophy or str(estimate),
            )
        for team in subleague.remainder:
            needed = playoff.cutoff - team
            estimate = team.estimate_party_time(needed)
            star = "*" if team.games_played < (sim_data.day + 1) else " "
            championships = "●" * team.championships if team.championships < 4 else f"●*{team.championships}"
            party = "🥳" if needed > (99 - team.games_played) or estimate < sim_data.day else ""
            teams.add_row(
                "",
                Text.assemble((team.name, team.color), f"[{team.tiebreaker}]"),
                championships,
                f"{team.wins}{star}",
                team.record,
                party or str(estimate),
            )

        predictions[subleague.name] = teams

    game_data: Prediction = {
        "league": sim_data.league.name,
        "season": sim_data.season,
        "day": sim_data.day + 1,
        "predictions": predictions,
    }
    return game_data
