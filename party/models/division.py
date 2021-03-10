from dataclasses import dataclass
from operator import attrgetter
from typing import List, TypedDict

from blaseball_mike import database, models

from party.models.team import Team

DivisionData = TypedDict(
    "DivisionData",
    {
        "id": str,
        "teams": List[str],
        "name": str,
    },
)


@dataclass
class Division:
    _data: DivisionData
    teams: List[Team]

    @classmethod
    def load(cls, id_: str, all_teams: List[Team], tiebreakers: List[str]) -> "Division":
        data = database.get_division(id_=id_)
        teams = [
            Team(
                _data=all_teams[team_id],
                tiebreaker=tiebreakers.index(team_id) + 1,
            )
            for team_id in data["teams"]
        ]
        return cls(_data=data, teams=sorted(teams, key=attrgetter("sort"), reverse=True))

    @property
    def name(self) -> str:
        return self._data["name"]

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
