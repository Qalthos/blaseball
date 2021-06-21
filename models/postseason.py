from typing import Optional
from uuid import UUID

from pydantic import validator

from models import FixedModel


class Playoffs(FixedModel):
    id: UUID
    name: str
    number_of_rounds: int
    playoff_day: int
    rounds: list[UUID]
    season: int
    bracket: int
    round: int
    tomorrow_round: int
    winner: Optional[UUID]
    tournament: int


class PlayoffRound(FixedModel):
    id: UUID
    game_index: int
    games: list[list[Optional[UUID]]]
    matchups: list[UUID]
    name: str
    round_number: int
    special: bool
    winner_seeds: list[int]
    winners: list[Optional[UUID]]

    @validator("winners", pre=True)
    def coerce_none(cls, items):
        for index, item in enumerate(items):
            if item == "none":
                items[index] = None
        return items

    @validator("games", pre=True)
    def coerce_list_none(cls, items):
        for index, game_list in enumerate(items):
            items[index] = cls.coerce_none(game_list)
        return items


class PlayoffMatchup(FixedModel):
    id: UUID
    name: Optional[str]
    away_seed: Optional[int]
    away_team: Optional[UUID]
    away_wins: int
    home_seed: Optional[int]
    home_team: Optional[UUID]
    home_wins: int
    games_played: int
    games_needed: int


class Postseason(FixedModel):
    playoffs: Playoffs
    all_rounds: list[PlayoffRound]
    all_matchups: list[PlayoffMatchup]
    round: PlayoffRound
    matchups: list[PlayoffMatchup]
    tomorrow_round: PlayoffRound
    tomorrow_matchups: list[PlayoffMatchup]

    def get_matchup(self, matchup_id: UUID) -> PlayoffMatchup:
        if self.all_matchups is None:
            raise ValueError("No matchups")
        for matchup in self.all_matchups:
            if matchup.id == matchup_id:
                return matchup
        raise ValueError("No matchup with id {matchup_id!s} found.")
