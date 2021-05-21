from typing import Optional
from uuid import UUID

from models import FixedModel


class League(FixedModel):
    id: UUID
    subleagues: list[UUID]
    name: str
    tiebreakers: UUID


class FaxMachine(FixedModel):
    runsNeeded: int


class StadiumState(FixedModel):
    faxMachine: Optional[FaxMachine]
    solarPanels: Optional[bool]


class Stadium(FixedModel):
    id: UUID
    teamId: UUID
    name: str
    nickname: str
    model: int
    mainColor: str
    secondaryColor: str
    tertiaryColor: str
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
    renoHand: list[str]
    renoDiscard: list[str]
    renoLog: dict[str, int]
    renoCost: int
    mods: list[str]
    birds: int
    state: StadiumState


class Subleague(FixedModel):
    id: UUID
    divisions: list[UUID]
    name: str


class Division(FixedModel):
    id: UUID
    teams: list[UUID]
    name: str


class TeamState(FixedModel):
    donatedShame: Optional[float]
    overflowRuns: Optional[float]
    permModSources: Optional[dict[str, list[str]]]
    gameModSources: Optional[dict[str, list[str]]]


class Team(FixedModel):
    id: UUID
    lineup: list[UUID]
    rotation: list[UUID]
    bullpen: list[UUID]
    bench: list[UUID]
    fullName: str
    nickname: str
    location: str
    mainColor: str
    secondaryColor: str
    shorthand: str
    emoji: str
    slogan: str
    shameRuns: int
    totalShames: int
    totalShamings: int
    seasonShames: int
    seasonShamings: int
    championships: int
    gameAttr: list[str]
    weekAttr: list[str]
    seasAttr: list[str]
    permAttr: list[str]
    rotationSlot: int
    teamSpirit: int
    card: int
    tournamentWins: int
    stadium: Optional[UUID]
    eDensity: float
    evolution: int
    winStreak: int
    level: Optional[str]
    state: TeamState


class Tiebreakers(FixedModel):
    id: UUID
    order: list[UUID]


class CommunityChest(FixedModel):
    chestsUnlocked: int
    progress: float
    runs: float


class LeagueStats(FixedModel):
    communityChest: CommunityChest


class LeagueData(FixedModel):
    leagues: list[League]
    stadiums: list[Stadium]
    subleagues: list[Subleague]
    divisions: list[Division]
    teams: list[Team]
    tiebreakers: list[Tiebreakers]
    stats: LeagueStats

    def get_stadium(self, stadium_id: UUID) -> Stadium:
        for stadium in self.stadiums:
            if stadium.id == stadium_id:
                return stadium
        raise ValueError(f"Stadium {stadium_id!s} not found")

    def get_team(self, team_id: UUID) -> Team:
        for team in self.teams:
            if team.id == team_id:
                return team
        raise ValueError(f"Team {team_id!s} not found")
