from typing import Any

from blaseball_mike import database
from blaseball_mike import models
from rich.layout import Layout
from rich.table import Table
from rich.text import Text

from party.models.subleague import Subleague


def get_game_data(sim_data: models.SimulationData) -> dict[str, Any]:
    """Get Blaseball data and return party time predictions"""

    # Pick out all standings
    season = database.get_season(season_number=sim_data.season)
    standings = database.get_standings(id_=season["standings"])

    # Get teams
    all_teams = database.get_all_teams()
    tiebreakers = next(iter(sim_data.league.tiebreakers.values()))

    predictions: dict[str, list[str]] = {}
    for subleague_id in sim_data.league.subleagues:
        subleague = Subleague.load(
            id_=subleague_id,
            all_teams=all_teams,
            standings=standings,
            tiebreakers=list(tiebreakers.order),
        )
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
            badge = "H" if team == playoff.high else "L" if team == playoff.low else "*"
            star = "*" if team.games_played < (sim_data.day + 1) else " "
            championships = "●" * team.championships if team.championships < 4 else f"●*{team.championships}"
            trophy = " 🏆" if team - subleague.cutoff > (99 - subleague.cutoff.games_played) else ""
            teams.add_row(
                badge,
                Text.assemble((team.name, team.color), f"[{team.tiebreaker}]"),
                championships,
                f"{team.wins}{star}",
                team.record,
                # str(team.estimate_party_time(playoff.cutoff - team)),
                trophy,
            )
        for team in subleague.remainder:
            needed = playoff.cutoff - team
            estimate = team.estimate_party_time(needed)
            party = "🥳" if needed > (99 - team.games_played) or estimate < sim_data.day else ""
            star = "*" if team.games_played < (sim_data.day + 1) else " "
            championships = "●" * team.championships if team.championships < 4 else f"●*{team.championships}"
            teams.add_row(
                party,
                Text.assemble((team.name, team.color), f"[{team.tiebreaker}]"),
                championships,
                f"{team.wins}{star}",
                team.record,
                # f"-{needed}",
                str(estimate),
            )

        predictions[subleague.name] = teams

    game_data = {
        "league": sim_data.league.name,
        "season": sim_data.season,
        "day": sim_data.day + 1,
        "predictions": predictions,
    }
    return game_data
