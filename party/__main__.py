from blaseball_mike import models

from party import display, postseason, season


def main() -> None:
    sim_data = models.SimulationData.load()
    if sim_data.day < 99:
        league = season.get_league(sim_data.league.id)
        game_data = season.get_game_data(sim_data.season, sim_data.day, league)
        display.update_standings(
            f"{sim_data.league.name} Season {sim_data.season} Day {sim_data.day + 1}",
            game_data,
        )
    else:
        postseason_data = postseason.get_playoffs(sim_data)
        display.update_postseason(
            f"{postseason_data['name']} {postseason_data['round']}",
            postseason_data["games"],
        )


if __name__ == "__main__":
    display.display_loop(main)
