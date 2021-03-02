from dataclasses import dataclass
from typing import List, TypedDict, Tuple


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
    wins: int
    losses: int
    tiebreaker: int

    @property
    def name(self) -> str:
        return self._data["nickname"]

    @property
    def emoji(self) -> str:
        return self._data["emoji"]

    @property
    def color(self) -> str:
        return self._data["mainColor"]

    def record(self, day: int = 0) -> str:
        """Return the team record of wins and losses

        If day is present, calculate wins from losses and day, in case of
        weather.
        """
        if day:
            return f"{day - self.losses}-{self.losses}"
        return f"{self.wins}-{self.losses}"

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
