from collections import defaultdict
from typing import TypedDict

from blaseball_mike import models
from rich.table import Table
from rich.text import Text

Prediction = TypedDict(
    "Prediction",
    {
        "league": str,
        "name": str,
        "round": str,
        "games": dict[str, Table],
    },
)


def subleague_for_team(subleagues: list[models.Subleague], team: models.Team) -> str:
    for subleague in subleagues:
        if team in subleague.teams.values():
            return subleague.name
    raise KeyError("Can't find subleague for team")


def get_playoffs(sim_data: models.SimulationData) -> Prediction:
    playoff = models.Playoff.load_by_season(sim_data.season)
    subleagues = sim_data.league.subleagues.values()

    tables = {}
    for subleague in subleagues:
        games = Table.grid(expand=True)
        games.add_column("Seed", width=1)
        games.add_column("Name")
        games.add_column("Wins", width=1)
        tables[subleague.name] = games

    teams: dict[str, dict[str, list]]
    current_round: models.PlayoffRound
    for playoff_round in playoff.rounds:
        if not playoff_round.games:
            break
        current_round = playoff_round
        teams = {subleague.name: defaultdict(list) for subleague in subleagues}
        for matchup in current_round.matchups:
            if matchup.away_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.away_team)
                except KeyError:
                    continue
                teams[subleague][matchup.id].append((
                    str(matchup.away_seed + 1),
                    Text(matchup.away_team.nickname, style=matchup.away_team.main_color),
                    str(matchup.away_wins),
                ))
            if matchup.home_team:
                try:
                    subleague = subleague_for_team(subleagues, matchup.home_team)
                except KeyError:
                    continue
                teams[subleague][matchup.id].append((
                    str(matchup.home_seed + 1),
                    Text(matchup.home_team.nickname, style=matchup.home_team.main_color),
                    str(matchup.home_wins)
                ))

    for subleague, table in tables.items():
        matches = sorted(teams[subleague].values())
        for match in matches:
            for team in match:
                table.add_row(*team)
            table.add_row()

    game_data: Prediction = {
        "league": sim_data.league.name,
        "name": playoff.name,
        "round": current_round.name,
        "games": tables,
    }
    return game_data
