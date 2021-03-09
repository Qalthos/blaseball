import time

from blaseball_mike import models
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from party.display import layout
from party import season, postseason


def main() -> None:
    if sim_data.day < 100:
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
        game_data = postseason.get_playoffs(sim_data)
        layout["header"].update(Panel(Text(
            f"{game_data['name']} Day {game_data['day']}",
            justify="center",
        )))


if __name__ == "__main__":
    sim_data = models.SimulationData.load()
    subleagues = season.get_subleagues(sim_data.league)
    main()
    with Live(layout) as live:
        while True:
            sim_data = models.SimulationData.load()
            main()

            try:
                time.sleep(600)
            except KeyboardInterrupt:
                break
