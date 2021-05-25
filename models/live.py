from typing import Optional

from models import FixedModel
from models.game import GamesData
from models.league import LeagueData


class FightData(FixedModel):
    # Not sure if this is ever gonna get filled, but
    # cause problems when it does
    boss_fights: list[None]


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
    fights: Optional[FightData]
    temporal: Optional[TemporalData]
