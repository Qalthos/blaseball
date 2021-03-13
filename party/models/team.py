from dataclasses import dataclass
from typing import Tuple

from blaseball_mike import models


@dataclass
class Team:
    _data: models.Team
    tiebreaker: int
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    runs: int = 0

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def name(self) -> str:
        return self._data.nickname

    @property
    def color(self) -> str:
        return self._data.main_color

    @property
    def championships(self) -> int:
        return self._data.championships

    @property
    def record(self) -> str:
        """Return the team record of wins and losses"""
        return f"{self.games_played - self.losses:>2}-{self.losses:>2}"

    def estimate_party_time(self, needed: int) -> int:
        """Return the estimated game the team will begin partying"""
        return int((99 * self.games_played) / (needed + self.games_played)) + 1

    def update(self, standings: models.Standings) -> None:
        self.games_played = standings.games_played[self.id]
        self.wins = standings.wins[self.id]
        self.losses = standings.losses[self.id]
        self.runs = standings.runs[self.id]

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
