from dataclasses import dataclass
from operator import attrgetter
from typing import Iterable, Iterator, List

from blaseball_mike import models

from party.models.division import Division
from party.models.team import Team


@dataclass
class PlayoffTeams(Iterable[Team]):
    high: Team
    low: Team
    others: List[Team]

    @classmethod
    def load(cls, high: Division, low: Division) -> tuple["PlayoffTeams", "PlayoffTeams"]:
        at_large = sorted(high.remainder + low.remainder, key=attrgetter("sort"), reverse=True)
        overbracket = PlayoffTeams(high=high.winner, low=low.winner, others=at_large[:2])
        at_large = sorted(high.remainder + low.remainder, key=attrgetter("sort"))
        underbracket = PlayoffTeams(high=high.unwinner, low=low.unwinner, others=at_large[:2])
        return overbracket, underbracket

    @property
    def cutoff(self):
        return min(self.others, key=attrgetter("sort"))

    def __iter__(self) -> Iterator[Team]:
        winners = [self.high, self.low, *self.others]
        return iter(sorted(winners, key=attrgetter("sort"), reverse=True))


@dataclass
class Subleague:
    name: str
    divisions: List[Division]

    @classmethod
    def load(cls, subleague: models.Subleague, tiebreakers: List[str]) -> "Subleague":
        divisions = [
            Division.load(division, tiebreakers)
            for division in subleague.divisions.values()
        ]
        return cls(name=subleague.name, divisions=divisions)

    @property
    def teams(self):
        for division in self.divisions:
            yield from division.teams

    @property
    def playoff_teams(self) -> tuple[PlayoffTeams, PlayoffTeams]:
        return PlayoffTeams.load(*self.divisions)

    @property
    def remainder(self) -> List[Team]:
        remainders = []
        for division in self.divisions:
            remainders.extend(division.remainder)
        return sorted(remainders, key=attrgetter("sort"), reverse=True)[2:-2]

    @property
    def cutoff(self) -> tuple[Team, Team]:
        return self.remainder[0], self.remainder[-1]

    def update(self, standings: models.Standings) -> None:
        for division in self.divisions:
            division.update(standings)

    def get_division(self, team: Team) -> str:
        for division in self.divisions:
            if team in division.teams:
                return division.name
        raise ValueError(f"Team {team.name} is not in any division in this subleague")
