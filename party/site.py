from blaseball_mike import models
from flask import Flask, render_template
from flask_caching import Cache

from party import season

app = Flask(__name__)
cache = Cache(app)


@app.route("/")
@cache.cached(timeout=900)
def standings() -> str:
    sim_data = models.SimulationData.load()
    subleagues = season.get_subleagues(sim_data.league)
    game_data = season.get_game_data(sim_data, subleagues)

    return render_template("standings.j2", sim=sim_data, standings=game_data)
