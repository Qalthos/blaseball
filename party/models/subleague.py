from dataclasses import dataclass
from operator import attrgetter
from typing import List, TypedDict, Iterable, Iterator

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
class PlayoffTeams(Iterable[Team]):
    high: Team
    low: Team
    others: list[Team]

    @classmethod
    def load(self, high: Division, low: Division) -> "PlayoffTeams":
        at_large = sorted(high.remainder + low.remainder, key=attrgetter("sort"), reverse=True)
        return PlayoffTeams(high=high.winner, low=low.winner, others=at_large[:2])

    def __iter__(self) -> Iterator[Team]:
        winners = [self.high, self.low, *self.others]
        return iter(sorted(winners, key=attrgetter("sort"), reverse=True))


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
    def playoff_teams(self) -> PlayoffTeams:
        return PlayoffTeams.load(*self.divisions)

    @property
    def remainder(self) -> List[Team]:
        remainders = []
        for division in self.divisions:
            remainders.extend(division.remainder)
        return sorted(remainders, key=attrgetter("sort"), reverse=True)[2:]
