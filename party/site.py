import json
from datetime import datetime

from blaseball_mike import models
from flask import Flask, render_template
from flask_caching import Cache

from party import season, teams
from party.models.league import League

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


@app.route("/")
@cache.cached(timeout=60)
def show_standings() -> str:
    standings_json = show_standings_json()
    if standings_json:
        bundle = json.loads(standings_json)
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])
        return render_template("standings.j2", **bundle)
    else:
        sim_data = models.SimulationData.load()
        standings = get_standings(
            sim_data.league.id,
            sim_data.season,
            sim_data.day,
        )

        return render_template(
            "standings.j2",
            league=sim_data.league.name,
            season=sim_data.season,
            standings=standings,
            updated=datetime.now(),
        )


@app.route("/standings.json")
def show_standings_json() -> str:
    try:
        with open("/tmp/standings.json") as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""


@app.route("/teams/<string:team_id>")
@cache.memoize(timeout=60)
def show_team_stats(team_id: str):
    teams_json = show_teams_json()
    if teams_json:
        bundle = json.loads(teams_json)
        team_data = bundle[team_id]
    else:
        team_data = get_team_data(season)[team_id]

    sim = models.SimulationData.load()
    all_teams = sim.league.teams
    return render_template(
        "team.j2",
        team_id=team_id,
        team_data=team_data,
        teams=all_teams
    )


@app.route("/teams.json")
def show_teams_json():
    try:
        with open("/tmp/teams.json") as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""


@cache.memoize()
def get_league(league_id: str, season_number: int) -> League:
    # season_number is used to keep the memoization accurate
    return season.get_league(league_id)


@cache.memoize(timeout=300)
def get_standings(league_id: str, season_number: int, day_number: int):
    league = get_league(league_id, season_number)
    return season.get_game_data(season_number, day_number, league)


@cache.memoize(timeout=900)
def get_team_data(season: int):
    return teams.collect_records(season)
