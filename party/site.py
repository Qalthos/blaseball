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
    sim_data = models.SimulationData.load()
    standings = get_standings(sim_data.league.id, sim_data.season, sim_data.day)

    return render_template("standings.j2", sim=sim_data, standings=standings)


@cache.memoize()
def get_league(league_id: str, season_number: int) -> League:
    # season_number is used to keep the memoization accurate
    return season.get_league(league_id)


@cache.memoize(timeout=300)
def get_standings(league_id: str, season_number: int, day_number: int) -> season.Prediction:
    subleagues = get_league(league_id, season_number)
    return season.get_game_data(season_number, day_number, subleagues)
