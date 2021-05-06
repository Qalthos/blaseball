from dataclasses import dataclass, field
from typing import Any, NamedTuple

from blaseball_mike import chronicler, database, tables

TEAMS = {
    team_id: team["nickname"]
    for team_id, team in database.get_all_teams().items()
}
STADIA = {
    stadium["data"]["teamId"]: stadium["data"]["nickname"]
    for stadium in chronicler.get_stadiums()
}


class Record(NamedTuple):
    wins: int = 0
    games: int = 0

    def add(self, other: "Record") -> "Record":
        return type(self)(self.wins + other.wins, self.games + other.games)


@dataclass
class OtherTeamRecord:
    name: str
    pitchers: dict[str, Record] = field(default_factory=dict)
    overall: Record = Record()

    def record_game(self, pitcher: str, outcome: Record) -> None:
        self.overall = self.overall.add(outcome)
        self.pitchers[pitcher] = self.pitchers.get(pitcher, Record()).add(outcome)

    def to_json(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            pitchers=self.pitchers,
            overall=self.overall,
        )


@dataclass
class TeamRecord:
    name: str
    others: dict[str, OtherTeamRecord] = field(default_factory=dict)
    pitchers: dict[str, Record] = field(default_factory=dict)
    weather: dict[str, Record] = field(default_factory=dict)
    stadia: dict[str, Record] = field(default_factory=dict)
    overall: Record = Record()

    def record_game(self, pitcher: str, weather: str, stadium: str, team_id: str, team_pitcher: str, outcome: Record) -> None:
        self.overall = self.overall.add(outcome)
        self.pitchers[pitcher] = self.pitchers.get(pitcher, Record()).add(outcome)
        self.weather[weather] = self.weather.get(weather, Record()).add(outcome)
        self.stadia[stadium] = self.stadia.get(stadium, Record()).add(outcome)
        if team_id not in self.others:
            self.others[team_id] = OtherTeamRecord(name=TEAMS[team_id])
        self.others[team_id].record_game(pitcher=team_pitcher, outcome=outcome)

    def to_json(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            overall=self.overall,
            pitchers=self.pitchers,
            weather=self.weather,
            stadia=self.stadia,
            others={
                team: team_record.to_json()
                for team, team_record in self.others.items()
            },
        )


@dataclass
class GamesByTeam:
    teams: dict[str, TeamRecord] = field(default_factory=dict)

    def record_game(self, team_id: str, pitcher: str, weather: str, stadium_team_id: str, other_team_id: str, team_pitcher: str, outcome: Record) -> None:
        if team_id not in self.teams:
            self.teams[team_id] = TeamRecord(name=TEAMS[team_id])
        self.teams[team_id].record_game(
            pitcher=pitcher,
            weather=weather,
            stadium=STADIA[stadium_team_id],
            team_id=other_team_id,
            team_pitcher=team_pitcher,
            outcome=outcome,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            team_id: team.to_json()
            for team_id, team in self.teams.items()
        }


def collect_records(season: int) -> dict[str, Any]:

    games_by_team = GamesByTeam()
    games = chronicler.get_games(season=season, finished=True)
    for game in games:
        data = game["data"]
        home = data["homeTeam"]
        away = data["awayTeam"]
        is_home_win = data["homeScore"] > data["awayScore"]
        weather = tables.Weather(data["weather"]).name

        games_by_team.record_game(
            team_id=home,
            other_team_id=away,
            stadium_team_id=home,
            pitcher=data["homePitcherName"],
            team_pitcher=data["awayPitcherName"],
            weather=weather,
            outcome=Record(int(is_home_win), 1),
        )
        games_by_team.record_game(
            team_id=away,
            other_team_id=home,
            stadium_team_id=home,
            pitcher=data["awayPitcherName"],
            team_pitcher=data["homePitcherName"],
            weather=weather,
            outcome=Record(int(not is_home_win), 1),
        )

    return games_by_team.to_json()
