from dataclasses import dataclass
from operator import attrgetter
from typing import List, Optional

from blaseball_mike import models

from party.models.subleague import Subleague
from party.models.team import Team


@dataclass
class League:
    name: str
    subleagues: List[Subleague]
    _teams: Optional[List[Team]] = None

    @classmethod
    def load(cls, league: models.League, tiebreakers: List[str]) -> "League":
        league = models.League.load_by_id(id_=league.id)
        subleagues = [
            Subleague.load(subleague, tiebreakers)
            for subleague in league.subleagues.values()
        ]
        return cls(name=league.name, subleagues=subleagues)

    @property
    def teams(self):
        if self._teams is None:
            self._teams = []
            for subleague in self.subleagues:
                self.teams.extend(subleague.teams)
            self._teams.sort(key=attrgetter("sort"))
        return self._teams

    @property
    def bottom_four(self) -> List[Team]:
        return self.teams[:4]

    def update(self, standings: models.Standings) -> None:
        for subleague in self.subleagues:
            subleague.update(standings)
        # Invalidate team order
        self._teams = None
