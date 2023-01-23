from typing import Dict, List, NamedTuple, Optional

from party.models.sim import Division, Sim, SubLeague
from party.models.team import Team

GAMES = 90


class Row(NamedTuple):
    name: str
    color: str
    wins: int
    record: str
    earliest: str
    estimate: Optional[str]
    id: str


Prediction = Dict[str, List[Optional[Row]]]


class DivisionRanking:
    name: str
    id: str
    _teams: list[Team]

    def __init__(self, division: Division):
        self.name = division.name
        self.id = division.id
        self._teams = []

    def __contains__(self, item: Team) -> bool:
        return self.id == item.division.id

    @property
    def teams(self) -> list[Team]:
        # TODO: is index 0 or season number?
        return sort_teams(self._teams)

    @property
    def playoff_team(self) -> Team:
        return self.teams[0]

    def add_team(self, team: Team) -> None:
        self._teams.append(team)


class SubleagueRanking:
    id: str
    _divisions: list[DivisionRanking]

    def __init__(self, subleague: SubLeague) -> None:
        self.id = subleague.id
        self._divisions = [DivisionRanking(d) for d in subleague.divisions]

    def __contains__(self, item: Team) -> bool:
        for division in self._divisions:
            if item in division:
                return True
        return False

    @property
    def teams(self) -> list[Team]:
        teams = sum([d._teams for d in self._divisions], [])
        return sort_teams(teams)

    @property
    def playoff_teams(self) -> list[Team]:
        playoff: list[Team] = []
        others: list[Team] = []
        for division in self._divisions:
            playoff.append(division.playoff_team)
            others.extend(d for d in division._teams if d not in playoff)
        playoff.extend(sort_teams(others)[: len(self._divisions)])
        return playoff

    def add_team(self, team: Team) -> None:
        for division in self._divisions:
            if team in division:
                division.add_team(team)
                break
        else:
            raise Exception("This team doesn't belong here")


def estimate_party_time(team: Team, needed: int) -> int:
    """Return the estimated game the team will begin partying"""
    played = team.standings[0].wins + team.standings[0].losses
    try:
        return int((90 * played) / (needed + played)) + 1
    except ZeroDivisionError:
        return 30


def sort_teams(teams: list[Team]) -> list[Team]:
    return sorted(teams, key=lambda t: t.standings[0].wins, reverse=True)


def format_row(subleague: SubleagueRanking, team: Team, day: int) -> Row:
    playoff = subleague.playoff_teams
    cutoff = playoff[-1]
    if team in playoff:
        needed = team.standings[0].wins - cutoff.standings[0].wins
        estimate = estimate_party_time(team, needed)
        trophy = "🏆" if needed > (GAMES - day) or estimate < day else ""
    else:
        needed = cutoff.standings[0].wins - team.standings[0].wins
        estimate = estimate_party_time(team, needed)
        trophy = "🥳" if needed > (GAMES - day) or estimate < day else ""

    earliest = day + ((GAMES - day - needed) // 2) + 1

    return Row(
        id=team.id,
        name=team.name,
        color=team.primaryColor,
        wins=team.standings[0].wins,
        record=f"{team.standings[0].wins}-{team.standings[0].losses}",
        earliest=str(earliest) if earliest > day else "N/A",
        estimate=trophy or str(estimate) if estimate > 33 else None,
    )


def make_predictions(sim: Sim, teams: list[Team]) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    leagues: list[SubleagueRanking] = []
    for subleague in sim.simData.currentLeagueData.subLeagues:
        leagues.append(SubleagueRanking(subleague))

    for team in teams:
        for subleague in leagues:
            if team in subleague:
                subleague.add_team(team)

    predictions: Prediction = {sl.id: [] for sl in leagues}
    for subleague in leagues:
        for team in subleague.teams:
            predictions[subleague.id].append(
                format_row(subleague, team, sim.simData.currentDay)
            )

    return predictions
