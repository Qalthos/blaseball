import json
from datetime import datetime

from flask import Flask, render_template, request
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


@app.route("/")
def show_standings() -> str:
    season_number = request.args.get("season", default=None, type=int)
    standings_json = show_standings_json(season_number)
    if standings_json:
        bundle = json.loads(standings_json)
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])

    return render_template("standings.j2", **bundle)


@app.route("/standings.json")
def show_standings_json(season_no: int = None) -> str:
    dest = "/srv/blaseball/standings.json"
    if season_no is not None:
        dest = "/srv/blaseball/standings.{season_no}.json"
    return load_json(dest)


@app.route("/teams/<string:team_id>")
def show_team_stats(team_id: str):
    season_number = request.args.get("season", default=None, type=int)
    teams_json = show_teams_json(season_number)
    if teams_json:
        bundle = json.loads(teams_json)
        bundle["team_id"] = team_id
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])

    return render_template("team.j2", season=season_number, **bundle)


@app.route("/teams.json")
def show_teams_json(season_no: int = None):
    dest = "/srv/blaseball/teams.json"
    if season_no is not None:
        dest = "/srv/blaseball/teams.{season_no}.json"
    return load_json(dest)


def load_json(dest: str) -> str:
    try:
        with open(dest) as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""
