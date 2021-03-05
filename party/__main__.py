import time
from typing import Any

from blaseball_mike import database
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from party.models.subleague import Subleague
from party.display import layout


def get_game_data() -> dict[str, Any]:
    """Get Blaseball data and return party time predictions"""

    sim_data = database.get_simulation_data()
    season_number = sim_data["season"] + 1

    # Pick out all standings
    season = database.get_season(season_number=season_number)
    standings = database.get_standings(id_=season["standings"])

    # Get teams
    all_teams = database.get_all_teams()
    league = database.get_league(id_=sim_data["league"])
    # IDK why this is so weird
    tiebreakers = database.get_tiebreakers(
        id=league["tiebreakers"]
    )[league["tiebreakers"]]

    predictions: dict[str, list[str]] = {}
    for subleague_id in league["subleagues"]:
        subleague = Subleague.load(
            id_=subleague_id,
            all_teams=all_teams,
            standings=standings,
            tiebreakers=tiebreakers["order"],
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
            if needed > (99 - team.games_played) or estimate < sim_data["day"]:
                teams.append(" 🥳🎉")
            else:
                teams.append(f" (-{needed})")
                if estimate < 99:
                    teams.append(f"\n  Party estimate on day {estimate}")

        predictions[subleague.name] = teams

    game_data = {
        "league": league["name"],
        "season": season_number,
        "day": sim_data["day"] + 1,
        "predictions": predictions,
    }
    return game_data


def main() -> None:
    game_data = get_game_data()
    layout["header"].update(Panel(Text(
        f"{game_data['league']} Season {game_data['season']} Day {game_data['day']}",
        justify="center",
    )))
    for subleague, data in game_data["predictions"].items():
        layout[subleague].update(Panel(
            data,
            title=subleague,
        ))


if __name__ == "__main__":
    with Live(layout) as live:
        while True:
            main()

            try:
                time.sleep(600)
            except KeyboardInterrupt:
                break
