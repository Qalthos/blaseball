from dataclasses import dataclass
from typing import List, Tuple, TypedDict

from blaseball_mike import models

TeamData = TypedDict(
    "TeamData",
    {
        "id": str,

        # Players
        "lineup": List[str],
        "rotation": List[str],
        "bullpen": List[str],
        "bench": List[str],

        # Team metadata
        "fullName": str,
        "location": str,
        "mainColor": str,
        "nickname": str,
        "secondaryColor": str,
        "shorthand": str,
        "emoji": str,
        "slogan": str,

        # Shame stats
        "shameRuns": int,
        "totalShames": int,
        "totalShamings": int,
        "seasonShames": int,
        "seasonShamings": int,

        "championships": int,
        "rotationSlot": int,

        # Modifiers
        "weekAttr": List[str],
        "gameAttr": List[str],
        "seasAttr": List[str],
        "permAttr": List[str],

        "teamSpirit": int,
    },
)


@dataclass
class Team:
    _data: TeamData
    tiebreaker: int
    games_played: int = 0
    wins: int = 0
    losses: int = 0

    @property
    def name(self) -> str:
        return self._data["nickname"]

    @property
    def color(self) -> str:
        return self._data["mainColor"]

    @property
    def championships(self) -> int:
        return self._data["championships"]

    @property
    def record(self) -> str:
        """Return the team record of wins and losses"""
        return f"{self.games_played - self.losses}-{self.losses}"

    def estimate_party_time(self, needed: int) -> int:
        """Return the estimated game the team will begin partying"""
        return int((99 * self.games_played) / (needed + self.games_played)) + 1

    def update(self, standings: models.Standings) -> None:
        self.games_played = standings.games_played[self._data["id"]]
        self.wins = standings.wins[self._data["id"]]
        self.losses = standings.losses[self._data["id"]]

    @property
    def sort(self) -> Tuple[int, int]:
        """A 2-tuple suitable for ordering teams by."""
        return (self.wins, -self.tiebreaker)

    def __str__(self) -> str:
        return f"{self.name} ({self.record})"

    def __sub__(self, other: "Team") -> int:
        """Calculate number of wins other must earn in order to pass self."""
        difference = self.wins - other.wins
        if other.tiebreaker > self.tiebreaker:
            difference += 1
        return difference
