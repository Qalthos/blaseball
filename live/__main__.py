#!/usr/bin/env python
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional

from blaseball_mike.events import stream_events
from blaseball_mike.tables import Weather
from rich.columns import Columns
from rich.console import RenderGroup
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress
from rich.table import Table
from rich.text import Text

from models.game import Game, SimData
from models.league import LeagueData
from models.live import StreamData


def phase_time(sim: SimData) -> tuple[str, int, int]:
    if sim.phase == 0:
        phase = "Rest"
        start = sim.godsDayDate
        end = sim.preseasonDate
    elif sim.phase == 1:
        phase = "Earlseason"
        start = sim.preseasonDate
        end = sim.earlseasonDate
    elif sim.phase == 2:
        phase = "Earlseason"
        start = sim.earlseasonDate
        end = sim.earlsiestaDate
    elif sim.phase == 3:
        phase = "Earlsiesta"
        start = sim.earlsiestaDate
        end = sim.midseasonDate
    elif sim.phase == 4:
        phase = "Midseason"
        start = sim.midseasonDate
        end = sim.latesiestaDate
    elif sim.phase == 5:
        phase = "Latesiesta"
        start = sim.latesiestaDate
        end = sim.lateseasonDate
    elif sim.phase == 6:
        phase = "Lateseason"
        start = sim.lateseasonDate
        end = sim.endseasonDate
    elif sim.phase == 7:
        phase = "Endseason"
        start = sim.endseasonDate
        end = sim.earlpostseasonDate
    elif sim.phase == 8:
        phase = "Prepostseason"
        start = sim.endseasonDate
        end = sim.earlpostseasonDate
    elif sim.phase == 9:
        phase = "Earlpostseason"
        end = sim.earlpostseasonDate
        start = sim.latepostseasonDate
    elif sim.phase == 10:
        phase = "Postearlpostseason"
        start = sim.earlpostseasonDate
        end = sim.latepostseasonDate
    elif sim.phase == 11:
        phase = "Latepostseason"
        start = sim.latepostseasonDate
        end = sim.electionDate
    elif sim.phase == 12:
        phase = "Postpostseason"
        start = sim.latepostseasonDate
        end = sim.electionDate
    elif sim.phase == 13:
        phase = "Election"
        start = sim.electionDate
        end = sim.godsDayDate + timedelta(days=7)
    else:
        raise Exception(f"Not sure what phase {sim.phase} is")
    now = datetime.now(tz=timezone.utc)
    current = int((now - start).total_seconds())
    total = int((end - start).total_seconds())
    return phase, current, total


def games(games_data: list[Game], leagues: Optional[LeagueData]) -> Generator[Panel, None, None]:
    for game in sorted(games_data, key=lambda x: x.homeOdds * x.awayOdds):
        if game.shame:
            inning = "[#800878]SHAME"
        elif game.gameComplete:
            inning = "[red]FINAL"
        else:
            inning = "[green]LIVE"
        inning += f" - {game.inning + 1:X}"
        if not game.gameComplete:
            inning += "▲" if game.topOfInning else "▼"
        weather = Weather(game.weather).text

        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row(inning, weather)
        grid.add_row(game.awayTeamNickname, f"{game.awayScore:g}")
        grid.add_row(game.homeTeamNickname, f"{game.homeScore:g}")

        update = "\n"
        if game.gameComplete:
            update += "\n".join(game.outcomes)
        else:
            update += game.lastUpdate

        if not update.strip():
            yield Panel(grid, width=30)
        else:
            style = "none"
            if update.endswith("scores!") or update.endswith("home run!"):
                style = "yellow"
            yield Panel(RenderGroup(grid, update), width=30, border_style=style)


async def main() -> None:
    phase_progress = Progress(expand=True)
    phase = phase_progress.add_task("Phase")
    chest_progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.completed}/{task.total}",
        expand=True,
    )
    chest = chest_progress.add_task("Community Chest", total=3000)
    layout = Layout()
    layout.split(
        Layout(name="phase", size=1),
        Layout(name="games"),
        Layout(name="progress", size=1),
    )
    layout["phase"].update(phase_progress)
    layout["games"].update(Text())
    layout["progress"].update(chest_progress)

    leagues = None
    with Live(layout, auto_refresh=False) as live:
        async for event in stream_events():
            stream_data = StreamData.parse_obj(event)

            if stream_data.leagues:
                leagues = stream_data.leagues
                chest_stats = leagues.stats.communityChest
                chest_progress.update(chest, completed=float(chest_stats.runs))

            if stream_data.games:
                phase_name, completed, total = phase_time(stream_data.games.sim)
                phase_progress.update(
                    phase,
                    description=phase_name,
                    completed=completed,
                    total=total,
                )

                layout["games"].update(Columns(games(stream_data.games.schedule, leagues), equal=True, expand=True))

            live.refresh()


asyncio.run(main())
