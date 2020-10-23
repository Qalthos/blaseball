from dataclasses import dataclass
from operator import attrgetter
from typing import List, Tuple, TypedDict

from blaseball_mike import database

from party.models import JSON
from party.models.division import Division
from party.models.team import Team


SubleagueData = TypedDict(
    "SubleagueData",
    {
        "id": str,
        "name": str,
        "divisions": List[str],
    },
)


@dataclass
class Subleague:
    _data: SubleagueData
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
