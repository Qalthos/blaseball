from blaseball_mike import models
from flask import Flask, render_template
from flask_caching import Cache

from party import season

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})


@app.route("/")
def standings() -> str:
    sim_data = get_sim_data()
    subleagues = get_league(sim_data.league.id, season)
    standings = get_standings(sim_data.season, sim_data.day, subleagues)

    return render_template("standings.j2", sim=sim_data, standings=standings)


@cache.cached(timeout=300)
def get_sim_data() -> models.SimulationData:
    return models.SimulationData.load()


@cache.memoize
def get_league(league_id: str, season_number: int):
    # season_number is used to keep the memoization accurate
    ignore = season_number  # dead: disable
    return season.get_subleagues(league_id)


@cache.cached(timeout=900)
def get_standings(season_number: int, day_number: int, subleagues):
    return season.get_game_data(season_number, day_number, subleagues)
