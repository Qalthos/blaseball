from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Tuple

from blaseball_mike import chronicler


@dataclass
class Record:
    wins: int = 0
    games: int = 0

    def __add__(self, other: "Record") -> "Record":
        return type(self)(self.wins + other.wins, self.games + other.games)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.wins, self.games)


def collect_records(season: int) -> Dict[str, Dict[str, Record]]:
    games_by_team: Dict[str, Dict[str, Record]] = defaultdict(lambda: defaultdict(Record))
    games = chronicler.get_games(season=season, finished=True)
    for game in games:
        home = game["data"]["homeTeam"]
        away = game["data"]["awayTeam"]
        is_home_win = game["data"]["homeScore"] > game["data"]["awayScore"]

        games_by_team[home][away] += Record(int(is_home_win), 1)
        games_by_team[away][home] += Record(int(not is_home_win), 1)

    return games_by_team
