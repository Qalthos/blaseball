import json
from datetime import datetime
from typing import Optional

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
        bundle["season_param"] = season_number
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])

    return render_template("standings.j2", **bundle)


@app.route("/standings.json")
def show_standings_json(season_no: Optional[int] = None) -> str:
    return load_json("standings", season_no)


@app.route("/teams/<string:team_id>")
def show_team_stats(team_id: str) -> str:
    season_number = request.args.get("season", default=None, type=int)
    teams_json = show_teams_json(season_number)
    if teams_json:
        bundle = json.loads(teams_json)
        bundle["team_id"] = team_id
        bundle["season_param"] = season_number
        bundle["updated"] = datetime.fromisoformat(bundle["updated"])

    return render_template("team.j2", **bundle)


@app.route("/teams.json")
def show_teams_json(season_no: Optional[int] = None):
    return load_json("teams", season_no)


def load_json(table: str, season_no: Optional[int] = None) -> str:
    dest = f"/srv/blaseball/{table}.json"
    if season_no is not None:
        dest = f"/srv/blaseball/{table}.{season_no}.json"

    try:
        with open(dest) as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""
