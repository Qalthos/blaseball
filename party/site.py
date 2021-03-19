import json
from datetime import datetime, timezone

from blaseball_mike import models
from flask import Flask, render_template, request
from flask_caching import Cache

from party import season, teams
from party.models.league import League

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


@app.route("/")
def show_standings() -> str:
    season_number = request.args.get("season", default=None, type=int)
    standings_json = show_standings_json()
    if standings_json and season_number is None:
        bundle = json.loads(standings_json)
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])
    else:
        sim = get_sim_data()
        if season_number is None:
            season_number = sim.season
            day_number = sim.day
        else:
            day_number = 99
        standings = get_standings(
            sim.league.id,
            season_number,
            day_number,
        )
        bundle = {
            "league": sim.league.name,
            "season": season_number,
            "standings": standings,
            "updated": datetime.now(timezone.utc),
        }

    return render_template("standings.j2", **bundle)


@app.route("/standings.json")
def show_standings_json() -> str:
    try:
        with open("/tmp/standings.json") as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""


@app.route("/teams/<string:team_id>")
def show_team_stats(team_id: str):
    season_number = request.args.get("season", default=None, type=int)
    teams_json = show_teams_json()
    if teams_json and season_number is None:
        bundle = json.loads(teams_json)
        bundle["team_id"] = team_id
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])
    else:
        if season_number is None:
            season_number = get_sim_data.season
        all_teams, team_data = get_team_data(season_number)
        bundle = {
            "team_id": team_id,
            "team_data": team_data,
            "teams": all_teams,
            "updated": datetime.now(timezone.utc),
        }

    return render_template("team.j2", season=season_number, **bundle)


@app.route("/teams.json")
def show_teams_json():
    try:
        with open("/tmp/teams.json") as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""


@cache.cached(timeout=60)
def get_sim_data():
    return models.SimulationData.load()


@cache.memoize()
def get_league(league_id: str, season_number: int) -> League:
    # season_number is used to keep the memoization accurate
    return season.get_league(league_id)


@cache.memoize(timeout=300)
def get_standings(league_id: str, season_number: int, day_number: int):
    league = get_league(league_id, season_number)
    return season.get_game_data(season_number, day_number, league)


@cache.memoize(timeout=900)
def get_team_data(season_number: int):
    return teams.collect_records(season_number)
