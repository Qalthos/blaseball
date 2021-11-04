#!/usr/bin/env python
import asyncio
from datetime import datetime, timezone
from typing import Generator

from blaseball_mike.events import stream_events
from blaseball_mike.models import Game
from blaseball_mike.stream_model import Sim, StreamData
from dateutil.parser import parse
from rich.columns import Columns
from rich.console import RenderGroup
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress
from rich.table import Table
from rich.text import Text

TEAM_URL = "https://www.blaseball.com/team"
PLAYER_URL = "https://www.blaseball.com/player"
LINK = "[link={url}/{id!s}]{name}"
TEAM = "Mechanics"


def inning(game: Game) -> Text:
    if not game.game_start:
        style = "#9a9531"
        inning = "UPCOMING"
    else:
        if game.shame:
            style = "#800878"
            inning = "SHAME"
        elif game.game_complete:
            style = "red"
            inning = "FINAL"
        else:
            style = "green"
            inning = "LIVE"

        inning += f" - {game.inning:X}"
        if not game.game_complete:
            inning += "▲" if game.top_of_inning else "▼"

    return Text.assemble(
        (inning, style),
        "",
    )


def highlight(game: Game) -> str:
    style = "none"
    if "Run" in game.score_update:
        style = "yellow"
    elif "Unrun" in game.score_update:
        style = "red"
    elif game.last_update.endswith("is Partying!"):
        style = "#ff66f9"
    elif game.last_update.startswith("CONSUMERS ATTACK"):
        style = "#a16dc3"

    return style


def update(game: Game) -> str:
    update = "\n"
    if game.game_complete:
        update += "\n".join(game.outcomes)
    elif game.last_update:
        update += game.last_update
    if game.score_ledger:
        update += f"\n[#c4c4c4]{game.score_ledger}[/]"
    if game.score_update:
        color = ""
        if "run" in game.score_update:
            color = "[yellow]"
        elif "unrun" in game.score_update:
            color = "[red]"
        update += f" {color}{game.score_update}"
    return update.rstrip()


def phase_time(sim: Sim) -> tuple[str, int, int]:
    end = sim.next_phase_time
    if sim.phase == 0:
        phase = "Rest"
        start = sim.gods_day_date
    elif sim.phase == 1:
        phase = "Earlseason"
        start = sim.preseason_date
    elif sim.phase == 2:
        phase = "Earlseason"
        start = sim.earlseason_date
    elif sim.phase == 3:
        phase = "Earlsiesta"
        start = sim.earlsiesta_date
    elif sim.phase == 4:
        phase = "Midseason"
        start = sim.midseason_date
    elif sim.phase == 5:
        phase = "Latesiesta"
        start = sim.latesiesta_date
    elif sim.phase == 6:
        phase = "Lateseason"
        start = sim.lateseason_date
    elif sim.phase == 7:
        phase = "Endseason"
        start = sim.endseason_date
    elif sim.phase == 8:
        phase = "Prepostseason"
        start = sim.endseason_date
    elif sim.phase == 9:
        phase = "Earlpostseason"
        start = sim.earlpostseason_date
    elif sim.phase == 10:
        phase = "Postearlpostseason"
        start = sim.earlpostseason_date
    elif sim.phase == 11:
        phase = "Latepostseason"
        start = sim.latepostseason_date
    elif sim.phase == 12:
        phase = "Postpostseason"
        start = sim.latepostseason_date
    elif sim.phase == 13:
        phase = "Election"
        start = sim.election_date
        end = sim.next_season_start
    else:
        raise Exception(f"Not sure what phase {sim.phase} is")
    now = datetime.now(tz=timezone.utc)
    current = int((now - parse(start)).total_seconds())
    total = int((end - parse(start)).total_seconds())
    return phase, current, total


def get_team_game(nickname: str, schedule: list[Game]) -> Game:
    for game in schedule:
        if nickname in (game.home_team_nickname, game.away_team_nickname):
            return game
    raise ValueError(f"{nickname} is not playing at that time")


def big_game(game: Game) -> Panel:
    if game.is_postseason:
        series = f"First to ±{game.series_length}"
    else:
        series = f"{game.series_index} of {game.series_length}"

    info = Table.grid(expand=True)
    info.add_column()
    info.add_column()
    info.add_column(justify="right")

    info.add_row(inning(game), game.weather.name, series)
    info.add_row(
        LINK.format(url=TEAM_URL, id=game.away_team, name=game.away_team_name),
        LINK.format(url=PLAYER_URL, id=game.away_pitcher, name=game.away_pitcher_name),
        f"{game.away_score:g}"
    )
    info.add_row(
        LINK.format(url=TEAM_URL, id=game.home_team, name=game.home_team_name),
        LINK.format(url=PLAYER_URL, id=game.home_pitcher, name=game.home_pitcher_name),
        f"{game.home_score:g}"
    )

    if game.top_of_inning:
        total_balls = game.away_balls
        total_strikes = game.away_strikes
        total_outs = game.away_outs
        total_bases = game.away_bases
        batter = LINK.format(url=PLAYER_URL, id=game.away_batter, name=game.away_batter_name)
    else:
        total_balls = game.home_balls
        total_strikes = game.home_strikes
        total_outs = game.home_outs
        total_bases = game.home_bases
        batter = LINK.format(url=PLAYER_URL, id=game.home_batter, name=game.home_batter_name)

    runners = ["", "", "", ""]
    for base, runner_id, runner in zip(game.bases_occupied, game.base_runners, game.base_runner_names):
        runners[base] = LINK.format(url=PLAYER_URL, id=runner_id, name=runner)

    state = Table.grid(expand=True)
    state.add_column(width=5)
    state.add_column(ratio=1, justify="right")
    state.add_column(ratio=1)
    state.add_row(
        f"B {'●' * game.at_bat_balls}{'○' * (total_balls - game.at_bat_balls - 1)}",
        "",
        f"2 {runners[1]}",
    )
    state.add_row(
        f"S {'●' * game.at_bat_strikes}{'○' * (total_strikes - game.at_bat_strikes - 1)}",
        f"{runners[2]} 3",
        f"1 {runners[0]}",
    )
    state.add_row(
        f"O {'●' * game.half_inning_outs}{'○' * (total_outs - game.half_inning_outs - 1)}",
        f"{runners[3]} 4" if total_bases >= 5 else "",
        f"🏏 {batter}",
    )

    style = highlight(game)
    return Panel(
        RenderGroup(info, "", state, update(game)),
        width=61,
        border_style=style,
    )


def little_game(game: Game) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row(inning(game), game.weather.name)
    grid.add_row(game.away_team_nickname, f"{game.away_score:g}")
    grid.add_row(game.home_team_nickname, f"{game.home_score:g}")

    style = highlight(game)
    return Panel(RenderGroup(grid, update(game)), width=30, border_style=style)


def render_games(games: list[Game]) -> Generator[Panel, None, None]:
    for game in games:
        yield little_game(game)


async def main() -> None:
    phase_progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        expand=True,
    )
    phase = phase_progress.add_task("Phase")
    layout = Layout()
    layout.split(
        Layout(name="phase", size=1),
        Layout(name="games"),
    )
    layout["phase"].update(phase_progress)
    layout["games"].update(Text())

    leagues = None
    with Live(layout, auto_refresh=False) as live:
        async for event in stream_events():
            stream_data = StreamData(event)

            if stream_data.leagues:
                leagues = stream_data.leagues
            if leagues is None:
                continue

            if games := stream_data.games:
                phase_name, completed, total = phase_time(games.sim)
                phase_progress.update(
                    phase,
                    description=f"{phase_name} Day {games.sim.day + 1}",
                    completed=completed,
                    total=total,
                )

                today = sorted(
                    games.schedule.games.values(),
                    key=lambda x: x.home_odds * x.away_odds + x.game_complete,
                )
                try:
                    favored = get_team_game(TEAM, today)
                    # Reposition followed team to the front
                    today.remove(favored)
                    today.insert(0, favored)
                except ValueError:
                    pass

                game_widgets = render_games(today)
                layout["games"].update(
                    Columns(game_widgets, equal=True, expand=True)
                )

            live.refresh()


if __name__ == "__main__":
    asyncio.run(main())
