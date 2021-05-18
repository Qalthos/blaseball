from datetime import datetime
from typing import Optional
from uuid import UUID

from models import FixedModel


class SimData(FixedModel):
    id: str
    day: int
    league: UUID
    nextPhaseTime: datetime
    phase: int
    playOffRound: int
    playoffs: UUID
    rules: UUID
    season: int
    seasonId: UUID
    terminology: UUID
    eraColor: str
    eraTitle: str
    subEraColor: str
    subEraTitle: str
    attr: list[str]
    agitations: int
    salutations: int
    tournament: int
    tournamentRound: int
    godsDayDate: datetime
    preseasonDate: datetime
    earlseasonDate: datetime
    earlsiestaDate: datetime
    midseasonDate: datetime
    latesiestaDate: datetime
    lateseasonDate: datetime
    endseasonDate: datetime
    earlpostseasonDate: datetime
    latepostseasonDate: datetime
    electionDate: datetime
    menu: str


class SeasonData(FixedModel):
    id: UUID
    league: UUID
    rules: UUID
    schedule: UUID
    seasonNumber: int
    standings: UUID
    stats: UUID
    terminology: UUID


class Standings(FixedModel):
    id: UUID
    losses: dict[UUID, int]
    wins: dict[UUID, int]
    gamesPlayed: dict[UUID, int]
    runs: dict[UUID, int]


class Item(FixedModel):
    itemId: UUID
    itemName: str
    winner: Optional[UUID]


class GameState(FixedModel):
    holidayInning: Optional[bool]
    prizeMatch: Optional[Item]


class Game(FixedModel):
    id: UUID
    basesOccupied: list[int]
    baseRunners: list[UUID]
    baseRunnerNames: list[str]
    outcomes: list[str]
    terminology: UUID
    lastUpdate: str
    rules: UUID
    statsheet: UUID
    awayPitcher: Optional[UUID]
    awayPitcherName: str
    awayBatter: Optional[UUID]
    awayBatterName: str
    awayTeam: UUID
    awayTeamName: str
    awayTeamNickname: str
    awayTeamColor: str
    awayTeamEmoji: str
    awayOdds: float
    awayStrikes: int
    awayScore: float
    awayTeamBatterCount: int
    homePitcher: Optional[UUID]
    homePitcherName: str
    homeBatter: Optional[UUID]
    homeBatterName: str
    homeTeam: UUID
    homeTeamName: str
    homeTeamNickname: str
    homeTeamColor: str
    homeTeamEmoji: str
    homeOdds: float
    homeStrikes: int
    homeScore: float
    homeTeamBatterCount: int
    season: int
    isPostseason: bool
    day: int
    phase: int
    gameComplete: bool
    finalized: bool
    gameStart: bool
    halfInningOuts: int
    halfInningScore: float
    inning: int
    topOfInning: bool
    atBatBalls: int
    atBatStrikes: int
    seriesIndex: int
    seriesLength: int
    shame: bool
    weather: int
    baserunnerCount: int
    homeBases: int
    awayBases: int
    repeatCount: int
    awayTeamSecondaryColor: str
    homeTeamSecondaryColor: str
    homeBalls: int
    awayBalls: int
    homeOuts: int
    awayOuts: int
    playCount: int
    tournament: int
    baseRunnerMods: list[str]
    homePitcherMod: str
    homeBatterMod: str
    awayPitcherMod: str
    awayBatterMod: str
    scoreUpdate: str
    scoreLedger: str
    stadiumId: UUID
    secretBaserunner: Optional[UUID]
    topInningScore: float
    bottomInningScore: float
    newInningPhase: int
    gameStartPhase: int
    isTitleMatch: bool
    queuedEvents: list[str]
    state: GameState


class GamesData(FixedModel):
    sim: SimData
    season: SeasonData
    standings: Standings
    schedule: list[Game]
    tomorrowSchedule: list[Game]
    postseason: dict
