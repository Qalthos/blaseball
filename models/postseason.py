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
    games: list[UUID]
    matchups: list[UUID]
    name: str
    roundNumber: int
    special: bool
    winnerSeeds: list[int]
    winners: list[UUID]


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
