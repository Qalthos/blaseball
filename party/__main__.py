import time

from blaseball_mike import models
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from party import postseason, season
from party.display import layout


def main() -> None:
    if sim_data.day < 99:
        game_data = season.get_game_data(sim_data, subleagues)
        layout["header"].update(Panel(Text(
            f"{game_data['league']} Season {game_data['season']} Day {game_data['day']}",
            justify="center",
        )))
        for subleague, data in game_data["predictions"].items():
            layout[subleague].update(Panel(
                data,
                title=subleague,
                padding=0,
            ))
    else:
        postseason_data = postseason.get_playoffs(sim_data)
        layout["header"].update(Panel(Text(
            f"{postseason_data['league']} {postseason_data['name']} Day {postseason_data['day']}",
            justify="center",
        )))
        for subleague, data in postseason_data["games"].items():
            layout[subleague].update(Panel(
                data,
                title=subleague,
                padding=0,
            ))


if __name__ == "__main__":
    sim_data = models.SimulationData.load()
    subleagues = season.get_subleagues(sim_data.league)
    main()
    with Live(layout) as live:
        while True:
            sim_data = models.SimulationData.load()
            main()

            try:
                time.sleep(300)
            except KeyboardInterrupt:
                break
