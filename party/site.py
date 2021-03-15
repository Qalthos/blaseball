import json
from datetime import datetime
from typing import List

from blaseball_mike import models
from flask import Flask, render_template
from flask_caching import Cache

from party import season
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


@cache.memoize()
def get_league(league_id: str, season_number: int) -> League:
    # season_number is used to keep the memoization accurate
    return season.get_league(league_id)


@cache.memoize(timeout=300)
def get_standings(league_id: str, season_number: int, day_number: int) -> season.Prediction:
    subleagues = get_league(league_id, season_number)
    return season.get_game_data(season_number, day_number, subleagues)
