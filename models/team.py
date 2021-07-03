from typing import Optional
from uuid import UUID

from blaseball_mike import tables
from pydantic.color import Color

from models import FixedModel


class ItemStat(FixedModel):
    type: tables.AdjustmentType
    stat: Optional[int]
    value: Optional[float]
    mod: Optional[str]


class ItemPart(FixedModel):
    name: str
    adjustments: list[ItemStat]


class Item(FixedModel):
    id: UUID
    name: str
    forger: Optional[UUID]
    forger_name: Optional[str]
    pre_prefix: Optional[ItemPart]
    prefixes: Optional[list[ItemPart]]
    post_prefix: Optional[ItemPart]
    root: ItemPart
    suffix: Optional[ItemPart]
    durability: int
    health: int
    baserunning_rating: float
    pitching_rating: float
    hitting_rating: float
    defense_rating: float


class Elsewhere(FixedModel):
    day: int
    season: int


class PlayerState(FixedModel):
    elsewhere: Optional[Elsewhere]
    item_mod_sources: Optional[dict[str, list[str]]]
    unscattered_name: Optional[str]


class Player(FixedModel):
    id: UUID
    anticapitalism: float
    base_thirst: float
    buoyancy: float
    chasiness: float
    coldness: float
    continuation: float
    divinity: float
    ground_friction: float
    indulgence: float
    laserlikeness: float
    martyrdom: float
    moxie: float
    musclitude: float
    name: str
    omniscience: float
    overpowerment: float
    patheticism: float
    ruthlessness: float
    shakespearianism: float
    suppression: float
    tenaciousness: float
    thwackability: float
    tragicness: float
    unthwackability: float
    watchfulness: float
    pressurization: float
    total_fingers: int
    soul: int
    deceased: bool
    peanut_allergy: bool
    cinnamon: float
    fate: int
    ritual: str
    coffee: int
    blood: int
    perm_attr: list[str]
    seas_attr: list[str]
    week_attr: list[str]
    game_attr: list[str]
    hit_streak: int
    consecutive_hits: int
    baserunning_rating: float
    pitching_rating: float
    hitting_rating: float
    defense_rating: float
    league_team_id: Optional[UUID]
    tournament_team_id: Optional[UUID]
    eDensity: float
    state: PlayerState
    evolution: int
    items: list[Item]
    item_attr: list[str]


class FaxMachine(FixedModel):
    runs_needed: int


class StadiumState(FixedModel):
    air_balloons: Optional[int]
    flood_balloons: Optional[int]
    fax_machine: Optional[FaxMachine]
    solar_panels: Optional[bool]
    event_horizon: Optional[bool]


class Stadium(FixedModel):
    id: UUID
    team_id: UUID
    name: str
    nickname: str
    model: int
    main_color: Color
    secondary_color: Color
    tertiary_color: Color
    ominousness: float
    forwardness: float
    obtuseness: float
    grandiosity: float
    fortification: float
    elongation: float
    inconvenience: float
    viscosity: float
    hype: float
    mysticism: float
    luxuriousness: float
    filthiness: float
    weather: dict[str, int]
    reno_hand: list[str]
    reno_discard: list[str]
    reno_log: dict[str, int]
    reno_cost: int
    mods: list[str]
    birds: int
    state: StadiumState


class StolenPlayer(FixedModel):
    id: UUID
    victim_index: int
    victim_team_id: UUID
    victim_location: int


class TeamState(FixedModel):
    donated_shame: Optional[float]
    overflow_runs: Optional[float]
    redacted: Optional[bool]
    stolen_players: Optional[list[StolenPlayer]]
    perm_mod_sources: Optional[dict[str, list[str]]]
    game_mod_sources: Optional[dict[str, list[str]]]


class Team(FixedModel):
    id: UUID
    lineup: list[UUID]
    rotation: list[UUID]
    shadows: list[UUID]
    full_name: str
    nickname: str
    location: str
    main_color: Color
    secondary_color: Color
    shorthand: str
    emoji: str
    slogan: str
    shame_runs: int
    total_shames: int
    total_shamings: int
    season_shames: int
    season_shamings: int
    championships: int
    underchampionships: int
    deceased: bool
    game_attr: list[str]
    week_attr: list[str]
    seas_attr: list[str]
    perm_attr: list[str]
    rotation_slot: int
    team_spirit: int
    card: tables.Tarot
    tournament_wins: int
    stadium: Optional[UUID]
    imPosition: tuple[float, float]
    eDensity: float
    evolution: int
    win_streak: int
    level: Optional[str]
    state: TeamState
