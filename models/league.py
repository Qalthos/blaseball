from uuid import UUID

from models import FixedModel
from models.team import Stadium, Team


class League(FixedModel):
    id: UUID
    subleagues: list[UUID]
    name: str
    tiebreakers: UUID


class Subleague(FixedModel):
    id: UUID
    divisions: list[UUID]
    name: str


class Division(FixedModel):
    id: UUID
    teams: list[UUID]
    name: str


class Tiebreakers(FixedModel):
    id: UUID
    order: list[UUID]


class CommunityChest(FixedModel):
    chests_unlocked: int
    progress: float
    runs: float


class SunSun(FixedModel):
    current: float
    maximum: int


class LeagueStats(FixedModel):
    community_chest: CommunityChest
    sunsun: SunSun


class LeagueData(FixedModel):
    leagues: list[League]
    stadiums: list[Stadium]
    subleagues: list[Subleague]
    divisions: list[Division]
    teams: list[Team]
    tiebreakers: list[Tiebreakers]
    stats: LeagueStats

    def get_team_subleague(self, team_id: UUID) -> Subleague:
        for subleague in self.subleagues:
            for division in self.divisions:
                if division.id not in subleague.divisions:
                    continue
                if team_id in division.teams:
                    return subleague
        raise ValueError(f"Team {team_id!s} not found")

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
