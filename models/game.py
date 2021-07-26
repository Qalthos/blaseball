from datetime import datetime
from typing import Literal, Optional, Union
from uuid import UUID

from blaseball_mike.models import Player
from pydantic.color import Color

from models import FixedModel, Nothing
from models.postseason import Postseason


class SimState(FixedModel):
    phase_on_hold: Optional[int]
    scheduled_game_event: Optional[datetime]


class SimData(FixedModel):
    id: Literal["thisidisstaticyo"]
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


class EgoPlayerData(FixedModel):
    id: UUID
    team: Optional[UUID]
    location: Optional[int]
    hall_player: bool


class GameState(FixedModel):
    holiday_inning: Optional[bool]
    prize_match: Optional[Prize]
    postseason: Optional[GamePostseason]
    ego_player_data: Optional[list[EgoPlayerData]]
    game_cancelled: Optional[bool]


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
    day: int
    # Phases
    phase: int
    game_start_phase: int
    new_inning_phase: int
    new_half_inning_phase: int
    end_phase: int
    # Flags
    is_postseason: bool
    is_title_match: bool
    game_start: bool
    game_complete: bool
    finalized: bool
    top_of_inning: bool
    half_inning_outs: int
    half_inning_score: float
    inning: int
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
    queued_events: list[str]
    state: GameState

    @property
    def secret_baserunner_name(self) -> Optional[str]:
        if self.secret_baserunner:
            return Player.load_one(str(self.secret_baserunner)).name
        return None


class GamesData(FixedModel):
    sim: SimData
    season: SeasonData
    standings: Standings
    schedule: list[Game]
    tomorrow_schedule: list[Game]
    postseasons: list[Union[Nothing, Postseason]]
