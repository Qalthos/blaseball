from typing import Optional, Union

from models import FixedModel, Nothing
from models.game import Game, GamesData
from models.league import LeagueData


class FightData(FixedModel):
    boss_fights: list[Game]


class TemporalValues(FixedModel):
    id: str
    alpha: int
    beta: int
    gamma: int
    delta: bool
    epsilon: bool
    zeta: str
    eta: int
    theta: str
    iota: int


class TemporalData(FixedModel):
    doc: TemporalValues


class StreamData(FixedModel):
    games: Optional[GamesData]
    leagues: Optional[LeagueData]
    fights: Union[FightData, Nothing]
    temporal: Union[TemporalData, Nothing, None]
