from typing import Any

from blaseball_mike import database
from blaseball_mike import models
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
        teams = Text("Current playoff teams:")
        playoff = subleague.playoff_teams
        for team in playoff:
            badge = "H" if team == playoff.high else "L" if team == playoff.low else "*"
            teams.append(f"\n{badge} {team.name}", style=team.color)
            teams.append(f"{'●' * team.championships}", style="#ffeb57")
            teams.append(f"[{team.tiebreaker}] {team.wins} {team.record}")
            if team - subleague.cutoff > (99 - subleague.cutoff.games_played):
                teams.append(" 🏆")

        teams.append("\n")

        for team in subleague.remainder:
            teams.append(f"\n{team.name}", style=team.color)
            teams.append(f"[{team.tiebreaker}] {team.wins} {team.record}")
            needed = playoff.cutoff - team
            estimate = team.estimate_party_time(needed)
            if needed > (99 - team.games_played) or estimate < sim_data.day:
                teams.append(" 🥳🎉")
            else:
                teams.append(f" (-{needed})")
                if estimate < 99:
                    teams.append(f"\n  Party estimate on day {estimate}")

        predictions[subleague.name] = teams

    game_data = {
        "league": sim_data.league.name,
        "season": sim_data.season,
        "day": sim_data.day,
        "predictions": predictions,
    }
    return game_data
