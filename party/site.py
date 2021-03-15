from typing import List

from blaseball_mike import models
from flask import Flask, render_template
from flask_caching import Cache

from party import season
from party.models.subleague import Subleague

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


@app.route("/")
@cache.cached(timeout=900)
def show_standings() -> str:
    sim_data = models.SimulationData.load()
    subleagues = get_league(sim_data.league.id, season)
    standings = season.get_game_data(sim_data.season, sim_data.day, subleagues)

    return render_template("standings.j2", sim=sim_data, standings=standings)


@cache.memoize()
def get_league(league_id: str, season_number: int) -> List[Subleague]:
    # season_number is used to keep the memoization accurate
    return season.get_subleagues(league_id)
