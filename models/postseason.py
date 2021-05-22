from typing import Optional
from uuid import UUID

from models import FixedModel


class Playoffs(FixedModel):
    id: UUID
    name: str
    numberOfRounds: int
    playoffDay: int
    rounds: list[UUID]
    season: int
    tomorrowRound: int
    winner: Optional[UUID]
    tournament: int


class PlayoffRound(FixedModel):
    id: UUID
    gameIndex: int
    # UUIDs, but with 'none' instead of nulls?
    games: list[list[Optional[str]]]
    matchups: list[UUID]
    name: str
    roundNumber: int
    special: bool
    winnerSeeds: list[int]
    # UUIDs, but with 'none' instead of nulls?
    winners: list[Optional[str]]


class PlayoffMatchup(FixedModel):
    id: UUID
    name: Optional[str]
    awaySeed: Optional[int]
    awayTeam: Optional[UUID]
    awayWins: int
    homeSeed: Optional[int]
    homeTeam: Optional[UUID]
    homeWins: int
    gamesPlayed: int
    gamesNeeded: int


class Postseason(FixedModel):
    playoffs: Playoffs
    allRounds: list[PlayoffRound]
    allMatchups: list[PlayoffMatchup]
    round: PlayoffRound
    matchups: list[PlayoffMatchup]
    tomorrowRound: PlayoffRound
    tomorrowMatchups: list[PlayoffMatchup]

    def get_matchup(self, matchup_id: UUID) -> PlayoffMatchup:
        for matchup in self.allMatchups:
            if matchup.id == matchup_id:
                return matchup
        raise ValueError("No matchup with id {matchup_id!s} found.")
