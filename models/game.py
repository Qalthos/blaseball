from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from blaseball_mike.models import Player
from pydantic.color import Color

from models import FixedModel, Nothing
from models.postseason import Postseason


class SimState(FixedModel):
    pass


class SimData(FixedModel):
    id: str
    day: int
    league: UUID
    next_phase_time: datetime
    phase: int
    playoffs: list[UUID]
    rules: UUID
    season: int
    season_id: UUID
    terminology: UUID
    era_color: Color
    era_title: str
    sub_era_color: Color
    sub_era_title: str
    attr: list[str]
    agitations: int
    salutations: int
    tournament: int
    tournament_round: int
    gods_day_date: datetime
    preseason_date: datetime
    earlseason_date: datetime
    earlsiesta_date: datetime
    midseason_date: datetime
    latesiesta_date: datetime
    lateseason_date: datetime
    endseason_date: datetime
    earlpostseason_date: datetime
    latepostseason_date: datetime
    election_date: datetime
    menu: str
    state: SimState


class SeasonData(FixedModel):
    id: UUID
    league: UUID
    rules: UUID
    schedule: UUID
    season_number: int
    standings: UUID
    stats: UUID
    terminology: UUID


class Standings(FixedModel):
    id: UUID
    losses: dict[UUID, int]
    wins: dict[UUID, int]
    games_played: dict[UUID, int]
    runs: dict[UUID, int]


class Prize(FixedModel):
    item_id: UUID
    item_name: str
    winner: Optional[UUID]


class GamePostseason(FixedModel):
    bracket: int
    matchup: UUID
    playoff_id: UUID


class GameState(FixedModel):
    holiday_inning: Optional[bool]
    prize_match: Optional[Prize]
    postseason: Optional[GamePostseason]


class Game(FixedModel):
    id: UUID
    bases_occupied: list[int]
    base_runners: list[UUID]
    base_runner_names: list[str]
    outcomes: list[str]
    terminology: UUID
    last_update: str
    rules: UUID
    statsheet: UUID
    away_pitcher: Optional[UUID]
    away_pitcher_name: str
    away_batter: Optional[UUID]
    away_batter_name: str
    away_team: UUID
    away_team_name: str
    away_team_nickname: str
    away_team_color: Color
    away_team_emoji: str
    away_odds: float
    away_strikes: int
    away_score: float
    away_team_batter_count: int
    home_pitcher: Optional[UUID]
    home_pitcher_name: str
    home_batter: Optional[UUID]
    home_batter_name: str
    home_team: UUID
    home_team_name: str
    home_team_nickname: str
    home_team_color: Color
    home_team_emoji: str
    home_odds: float
    home_strikes: int
    home_score: float
    home_team_batter_count: int
    season: int
    is_postseason: bool
    day: int
    phase: int
    game_complete: bool
    finalized: bool
    game_start: bool
    half_inning_outs: int
    half_inning_score: float
    inning: int
    top_of_inning: bool
    at_bat_balls: int
    at_bat_strikes: int
    series_index: int
    series_length: int
    shame: bool
    weather: int
    baserunner_count: int
    home_bases: int
    away_bases: int
    repeat_count: int
    away_team_secondary_color: Color
    home_team_secondary_color: Color
    home_balls: int
    away_balls: int
    home_outs: int
    away_outs: int
    play_count: int
    tournament: int
    base_runner_mods: list[str]
    home_pitcher_mod: str
    home_batter_mod: str
    away_pitcher_mod: str
    away_batter_mod: str
    score_update: str
    score_ledger: str
    stadium_id: UUID
    secret_baserunner: Optional[UUID]
    top_inning_score: float
    bottom_inning_score: float
    new_inning_phase: int
    game_start_phase: int
    is_title_match: bool
    queued_events: list[str]
    state: GameState
    end_phase: int


class GamesData(FixedModel):
    sim: SimData
    season: SeasonData
    standings: Standings
    schedule: list[Game]
    tomorrow_schedule: list[Game]
    postseasons: list[Union[Nothing, Postseason]]

    def get_team_today(self, nickname: str) -> Game:
        for game in self.schedule:
            if nickname in (game.home_team_nickname, game.away_team_nickname):
                return game
        raise ValueError(f"{nickname} is not playing right now")
