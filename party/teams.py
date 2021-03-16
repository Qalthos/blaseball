from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Tuple

from blaseball_mike import chronicler, database


@dataclass
class Record:
    wins: int = 0
    games: int = 0

    def __add__(self, other: "Record") -> "Record":
        return type(self)(self.wins + other.wins, self.games + other.games)

    def to_json(self) -> Tuple[int, int]:
        return (self.wins, self.games)


@dataclass
class TeamRecord:
    overall: Record = Record()
    pitchers: Dict[str, Record] = field(default_factory=dict)

    def record_game(self, pitcher: str, outcome: Record) -> None:
        self.overall += outcome
        self.pitchers[pitcher] = self.pitchers.get(pitcher, Record()) + outcome

    def to_json(self):
        return dict(
            overall=self.overall,
            pitchers=self.pitchers,
        )


def collect_records(season: int):
    teams = database.get_all_teams()

    games_by_team: Dict[str, Dict[str, TeamRecord]] = defaultdict(lambda: defaultdict(TeamRecord))
    games = chronicler.get_games(season=season, finished=True)
    for game in games:
        data = game["data"]
        home = data["homeTeam"]
        away = data["awayTeam"]
        is_home_win = data["homeScore"] > data["awayScore"]

        games_by_team[home][away].record_game(
            data["awayPitcherName"],
            Record(int(is_home_win), 1)
        )
        games_by_team[away][home].record_game(
            data["homePitcherName"],
            Record(int(not is_home_win), 1)
        )

    return teams, games_by_team
