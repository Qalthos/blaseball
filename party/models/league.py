from dataclasses import dataclass
from typing import List

from blaseball_mike import models

from party.models.subleague import Subleague
from party.models.team import Team


@dataclass
class League:
    name: str
    subleagues: List[Subleague]

    @classmethod
    def load(cls, league: models.League, tiebreakers: List[str]) -> "League":
        league = models.League.load_by_id(id_=league.id)
        subleagues = [
            Subleague.load(subleague, tiebreakers)
            for subleague in league.subleagues.values()
        ]
        return cls(name=league.name, subleagues=subleagues)

    @property
    def bottom_four(self) -> List[Team]:
        pass
