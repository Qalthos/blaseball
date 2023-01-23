from typing import Dict, List, NamedTuple

from blaseball_mike.models import Division, Team, Subleague
from blaseball_mike.stream_model import StreamGames, StreamLeagues


class Row(NamedTuple):
    name: str
    color: str
    tiebreaker: int
    championships: int
    underchampionships: int
    in_progress: bool
    wins: int
    losses: int
    nonlosses: int
    over: int
    party: int
    subleague: str
    division: str
    id: str


Prediction = Dict[str, List[Row]]
Tiebreak = dict[str, Team]
ATeam = tuple[Team, Subleague, Division]


def format_row(ateam: ATeam, other_teams: list[ATeam], standings, tiebreak: Tiebreak) -> Row:
    team, subleague, division = ateam
    subleague_teams = [t for t in other_teams if t[1] == ateam[1]]
    division_teams = [t for t in subleague_teams if t[2] == ateam[2]]
    nondivision_teams = [t for t in subleague_teams if t not in division_teams]

    overbracket = [division_teams[0], nondivision_teams[0]]

    for t in subleague_teams:
        if t not in overbracket:
            overbracket.append(t)
        if len(overbracket) == 5:
            break
    overbracket = sort_teams(overbracket, standings, tiebreak)

    middling = [t for t in subleague_teams if t not in overbracket]

    if middling:
        overbracket_cutoff = middling[0][0]
    else:
        overbracket_cutoff = overbracket[-1][0]
    if ateam == division_teams[0] == overbracket[-1]:
        for t in middling:
            if t in division_teams:
                overbracket_cutoff = t[0]
                break

    party_cutoff = overbracket[-1][0]
    if party_cutoff == nondivision_teams[0][0]:
        # Beating this team does nothing, they get in regardless
        party_cutoff = overbracket[-2][0]

    over = estimate(team, overbracket_cutoff, standings, tiebreak)
    party = estimate(party_cutoff, team, standings, tiebreak)

    games_played = standings.games_played.get(team.id, 0)
    losses = standings.losses.get(team.id, 0)
    return Row(
        id=str(team.id),
        name=team.nickname,
        color=team.main_color,
        championships=team.championships,
        underchampionships=team.underchampionships,
        #  Uhhhh
        in_progress=False,
        wins=standings.wins.get(team.id, 0),
        losses=losses,
        nonlosses=games_played - losses,
        tiebreaker=list(tiebreak.order.keys()).index(team.id) + 1,
        over=over,
        party=party,
        subleague=subleague.name,
        division=division.name,
    )


def estimate(team: Team, to_beat: Team, standings, tiebreak: Tiebreak) -> int:
    difference = standings.wins.get(team.id, 0) - standings.wins.get(to_beat.id, 0)
    if list(tiebreak.order.keys()).index(to_beat.id) > list(tiebreak.order.keys()).index(team.id):
        difference += 1

    played = standings.games_played.get(team.id, 0)
    try:
        return int((99 * played) / (difference + played)) + 1
    except ZeroDivisionError:
        # TODO: Uhhhh
        return -1


def league_teams(league: StreamLeagues) -> list[ATeam]:
    return [
        (t, s, d)
        for s in league.subleagues.values()
        for d in league.divisions.values() if d.id in s.divisions
        for t in league.teams.values() if t.id in d.teams
    ]


def sort_teams(teams: list[ATeam], standings, tiebreak) -> list[ATeam]:
    return sorted(
        teams,
        key=lambda t: (
            standings.wins.get(t[0].id, 0),
            -list(tiebreak.order.keys()).index(t[0].id),
        ),
        reverse=True,
    )


def get_standings(game_data: StreamGames, league_data: StreamLeagues) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    league = list(league_data.leagues.values())[0]
    tiebreaker = list(league.tiebreakers.values())[0]
    predictions: Prediction = {
        subleague.name: [] for subleague in league_data.subleagues.values()
    }
    teams = league_teams(league_data)
    teams = sort_teams(teams, game_data.standings, tiebreaker)
    for ateam in teams:
        subleague = ateam[1]
        predictions[subleague.name].append(
            format_row(ateam, teams, game_data.standings, tiebreaker)
        )

    return predictions
