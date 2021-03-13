from dataclasses import dataclass
from operator import attrgetter
from typing import List

from blaseball_mike import models

from party.models.team import Team


@dataclass
class Division:
    name: str
    teams: List[Team]

    @classmethod
    def load(cls, division: models.Division, tiebreakers: List[str]) -> "Division":
        teams = [
            Team(
                _data=team,
                tiebreaker=tiebreakers.index(team.id) + 1,
            )
            for team in division.teams.values()
        ]
        return cls(
            name=division.name,
            teams=sorted(teams, key=attrgetter("sort"), reverse=True)
        )

    @property
    def winner(self) -> Team:
        return self.teams[0]

    @property
    def remainder(self) -> List[Team]:
        return self.teams[1:]

    def update(self, standings: models.Standings) -> None:
        for team in self.teams:
            team.update(standings)

        self.teams.sort(key=attrgetter("sort"), reverse=True)
