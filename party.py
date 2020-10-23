from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Dict, List, Tuple

from blaseball_mike import database

API = "https://blaseball.com/"
JSON = Dict[str, Any]


@dataclass
class Team:
    _data: JSON
    wins: int
    losses: int
    tiebreaker: int

    @property
    def name(self) -> str:
        return self._data["nickname"]

    @property
    def record(self) -> Tuple[int, int]:
        """A 2-tuple suitable for ordering teams by."""
        return (self.wins, -self.tiebreaker)

    def __str__(self) -> str:
        return f"{self.name} {self.wins}-{self.losses}"


@dataclass
class Division:
    _data: JSON
    teams: List[Team]

    @classmethod
    def load(cls, id_: str, all_teams: List[Team], standings: JSON, tiebreakers: List[str]) -> "Division":
        data = database.get_division(id_=id_)
        teams = [
            Team(
                _data=all_teams[team_id],
                wins=standings['wins'][team_id],
                losses=standings['losses'][team_id],
                tiebreaker=tiebreakers.index(team_id),
            )
            for team_id in data["teams"]
        ]
        return cls(_data=data, teams=sorted(teams, key=attrgetter("record"), reverse=True))

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def winner(self) -> Team:
        return self.teams[0]

    @property
    def remainder(self) -> List[Team]:
        return self.teams[1:]


@dataclass
class Subleague:
    _data: JSON
    divisions: List[Division]

    @classmethod
    def load(cls, id_: str, all_teams: List[Team], standings: JSON, tiebreakers: List[str]) -> "Subleague":
        data = database.get_subleague(id_=id_)
        divisions = [
            Division.load(division_id, all_teams, standings, tiebreakers)
            for division_id in data["divisions"]
        ]
        return cls(_data=data, divisions=divisions)

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def playoff(self) -> List[Team]:
        winners = [division.winner for division in self.divisions]
        remainders = []
        for division in self.divisions:
            remainders.extend(division.remainder)
        winners.extend(sorted(remainders, key=attrgetter("record"), reverse=True)[:2])
        return sorted(winners, key=attrgetter("record"), reverse=True)

    @property
    def playoff_cutoff(self) -> Tuple[int, int]:
        return self.playoff[-1].record

    @property
    def remainder(self) -> List[Team]:
        remainders = []
        for division in self.divisions:
            remainders.extend(division.remainder)
        return sorted(remainders, key=attrgetter("record"), reverse=True)[2:]


def main() -> None:
    sim_data = database.get_simulation_data()
    game_day = sim_data["day"] + 1
    games_left = 99 - game_day

    # Pick out all standings
    season = database.get_season(season_number=sim_data["season"] + 1)
    standings = database.get_standings(id_=season["standings"])

    # Get teams
    all_teams = database.get_all_teams()
    league = database.get_league(id_=sim_data["league"])
    # IDK why this is so weird
    tiebreakers = database.get_tiebreakers(id=league["tiebreakers"])[league["tiebreakers"]]
    print(f"{league['name']} Day {game_day}", end="\n\n")
    for subleague_id in league["subleagues"]:
        subleague = Subleague.load(
            id_=subleague_id,
            all_teams=all_teams,
            standings=standings,
            tiebreakers=tiebreakers["order"],
        )
        print(subleague.name)
        print("Current playoff teams:")
        for team in subleague.playoff:
            if team.wins - subleague.playoff_cutoff[0] > games_left:
                print(f"{team} 🏆")
            else:
                print(team)
        print()
        required_losses = games_left - subleague.playoff_cutoff[0]
        for team in subleague.remainder:
            party_countdown = required_losses + team.wins
            if party_countdown <= 0:
                print(f"{team} 🥳🎉")
            else:
                print(f"{team} {party_countdown} losses until party time")
                points_per_game = team.wins / game_day
                delta_to_playoffs = subleague.playoff_cutoff[0] - team.wins
                if delta_to_playoffs > games_left * points_per_game:
                    print(f"  Estimated to occur on day {(subleague.playoff_cutoff[0] - 99) // (points_per_game - 1) + 1:.0f}")

        print()


if __name__ == "__main__":
    main()
