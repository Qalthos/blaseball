from collections import defaultdict
from typing import Dict, List, NamedTuple

from models.game import GamesData, Standings
from models.league import Division, LeagueData, Subleague, Tiebreakers
from models.team import Team


class Row(NamedTuple):
    badge: str
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
ATeam = tuple[Team, Subleague, Division]


def format_row(ateam: ATeam, other_teams: list[ATeam], day: int, standings: Standings, tiebreak: Tiebreakers) -> Row:
    team, subleague, division = ateam
    subleague_teams = [t for t in other_teams if t[1] == ateam[1]]
    division_teams = [t for t in subleague_teams if t[2] == ateam[2]]
    nondivision_teams = [t for t in subleague_teams if t not in division_teams]

    # TODO: Uhhhhhhh...
    overbracket = [division_teams[0]]
    if nondivision_teams:
        overbracket.append(nondivision_teams[0])

    for t in subleague_teams:
        if t not in overbracket:
            overbracket.append(t)
        if len(overbracket) == 4:
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

    games_played = standings.games_played[team.id]
    losses = standings.losses[team.id]
    return Row(
        id=str(team.id),
        name=team.nickname,
        color=team.main_color.as_hex(),
        championships=team.championships,
        underchampionships=team.underchampionships,
        in_progress=bool(games_played < (day + 1) < 100),
        wins=standings.wins[team.id],
        losses=losses,
        nonlosses=games_played - losses,
        badge="",
        tiebreaker=tiebreak.order.index(team.id) + 1,
        over=over,
        party=party,
        subleague=subleague.name,
        division=division.name,
    )


def estimate(team: Team, to_beat: Team, standings: Standings, tiebreak: Tiebreakers) -> int:
    difference = standings.wins[team.id] - standings.wins[to_beat.id]
    if tiebreak.order.index(to_beat.id) > tiebreak.order.index(team.id):
        difference += 1

    played = standings.games_played[team.id]
    try:
        return int((99 * played) / (difference + played)) + 1
    except ZeroDivisionError:
        # TODO: Uhhhh
        return -1


def league_teams(league: LeagueData) -> list[ATeam]:
    return [
        (t, s, d)
        for s in league.subleagues
        for d in league.divisions if d.id in s.divisions
        for t in league.teams if t.id in d.teams
    ]


def sort_teams(teams: list[ATeam], standings: Standings, tiebreak: Tiebreakers) -> list[ATeam]:
    return sorted(
        teams,
        key=lambda t: (
            standings.wins[t[0].id],
            -tiebreak.order.index(t[0].id),
        ),
        reverse=True,
    )


def get_standings(game_data: GamesData, league_data: LeagueData) -> Prediction:
    """Get Blaseball data and return party time predictions"""

    league = league_data.leagues[0]
    tiebreaker = next((
        tb for tb in league_data.tiebreakers
        if tb.id == league.tiebreakers
    ))
    predictions: Prediction = {
        subleague.name: [] for subleague in league_data.subleagues
    }
    teams = league_teams(league_data)
    teams = sort_teams(teams, game_data.standings, tiebreaker)
    for ateam in teams:
        subleague = ateam[1]
        predictions[subleague.name].append(format_row(ateam, teams, game_data.sim.day, game_data.standings, tiebreaker))

    return predictions
