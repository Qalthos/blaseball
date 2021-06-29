#!/usr/bin/env python
import asyncio
from datetime import datetime, timezone
from typing import Generator

from blaseball_mike.events import stream_events
from blaseball_mike.models import Weather
from rich.columns import Columns
from rich.console import RenderGroup
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress
from rich.table import Table
from rich.text import Text

from models.game import Game, SimData
from models.team import Stadium
from models.live import StreamData

TEAM_URL = "https://www.blaseball.com/team"
PLAYER_URL = "https://www.blaseball.com/player"
LINK = "[link={url}/{id!s}]{name}"


def inning(game: Game) -> Text:
    if not game.game_start:
        style = "#9a9531"
        inning = "UPCOMING"
    else:
        if game.shame:
            style = "#800878"
            inning = "SHAME"
        elif game.state.holiday_inning:
            style = "#ff66f9"
            inning = "PARTY"
        elif game.game_complete:
            style = "red"
            inning = "FINAL"
        else:
            style = "green"
            inning = "LIVE"

        inning += f" - {game.inning + 1:X}"
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
    else:
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
    return update


def phase_time(sim: SimData) -> tuple[str, int, int]:
    if sim.phase == 0:
        phase = "Rest"
        start = sim.gods_day_date
        end = sim.preseason_date
    elif sim.phase == 1:
        phase = "Earlseason"
        start = sim.preseason_date
        end = sim.earlseason_date
    elif sim.phase == 2:
        phase = "Earlseason"
        start = sim.earlseason_date
        end = sim.earlsiesta_date
    elif sim.phase == 3:
        phase = "Earlsiesta"
        start = sim.earlsiesta_date
        end = sim.midseason_date
    elif sim.phase == 4:
        phase = "Midseason"
        start = sim.midseason_date
        end = sim.latesiesta_date
    elif sim.phase == 5:
        phase = "Latesiesta"
        start = sim.latesiesta_date
        end = sim.lateseason_date
    elif sim.phase == 6:
        phase = "Lateseason"
        start = sim.lateseason_date
        end = sim.endseason_date
    elif sim.phase == 7:
        phase = "Endseason"
        start = sim.endseason_date
        end = sim.earlpostseason_date
    elif sim.phase == 8:
        phase = "Prepostseason"
        start = sim.endseason_date
        end = sim.earlpostseason_date
    elif sim.phase == 9:
        phase = "Earlpostseason"
        start = sim.earlpostseason_date
        end = sim.latepostseason_date
    elif sim.phase == 10:
        phase = "Postearlpostseason"
        start = sim.earlpostseason_date
        end = sim.latepostseason_date
    elif sim.phase == 11:
        phase = "Latepostseason"
        start = sim.latepostseason_date
        end = sim.election_date
    elif sim.phase == 12:
        phase = "Postpostseason"
        start = sim.latepostseason_date
        end = sim.election_date
    elif sim.phase == 13:
        phase = "Election"
        start = sim.election_date
        end = sim.gods_day_date + timedelta(days=7)
    else:
        raise Exception(f"Not sure what phase {sim.phase} is")
    now = datetime.now(tz=timezone.utc)
    current = int((now - start).total_seconds())
    total = int((end - start).total_seconds())
    return phase, current, total


def big_game(game: Game, stadium: Stadium) -> Panel:
    weather = Weather.load_one(game.weather).name
    if game.is_postseason:
        series = f"First to ±{game.series_length}"
    else:
        series = f"{game.series_index} of {game.series_length}"

    info = Table.grid(expand=True)
    info.add_column()
    info.add_column()
    info.add_column(justify="right")

    info.add_row(inning(game), weather, series)
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
    secret = ""
    if "SECRET_BASE" in stadium.mods:
        if game.secret_baserunner:
            secret = LINK.format(url=PLAYER_URL, id=game.secret_baserunner, name=game.secret_baserunner_name)
        secret += "🔒"
    for base, runner_id, runner in zip(game.bases_occupied, game.base_runners, game.base_runner_names):
        runners[base] = LINK.format(url=PLAYER_URL, id=runner_id, name=runner)

    state = Table.grid(expand=True)
    state.add_column(width=5)
    state.add_column(ratio=1, justify="right")
    state.add_column(ratio=1)
    state.add_row(
        f"B {'●' * game.at_bat_balls}{'○' * (total_balls - game.at_bat_balls - 1)}",
        secret,
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
    weather = Weather.load_one(game.weather).name

    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row(inning(game), weather)
    grid.add_row(game.away_team_nickname, f"{game.away_score:g}")
    grid.add_row(game.home_team_nickname, f"{game.home_score:g}")

    style = highlight(game)
    return Panel(RenderGroup(grid, update(game)), width=30, border_style=style)


def render_games(games: list[Game], stadia: list[Stadium]) -> Generator[Panel, None, None]:
    highlight = None
    stadium = None
    for game in games:
        if game.game_start and not game.game_complete:
            highlight = game
            break
    else:
        highlight = games[0]
    stadium = [stadium for stadium in stadia if stadium.id == highlight.stadium_id][0]
    yield big_game(highlight, stadium)

    for game in games:
        if game is not highlight:
            yield little_game(game)


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
        Layout(name="highlight"),
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
                chest_stats = leagues.stats.community_chest
                chest_progress.update(chest, completed=float(chest_stats.runs))

            if games := stream_data.games:
                phase_name, completed, total = phase_time(games.sim)
                phase_progress.update(
                    phase,
                    description=f"{phase_name} Day {games.sim.day + 1}",
                    completed=completed,
                    total=total,
                )

                today = sorted(
                    games.schedule,
                    key=lambda x: x.home_odds * x.away_odds + x.game_complete,
                )
                try:
                    mechanics = games.get_team_today("Mechanics")
                    # Reposition followed team to the front
                    today.remove(mechanics)
                    today.insert(0, mechanics)
                except ValueError:
                    pass

                game_widgets = render_games(today, leagues.stadiums)
                layout["highlight"].update(next(game_widgets))
                layout["games"].update(
                    Columns(game_widgets, equal=True, expand=True)
                )

            live.refresh()


if __name__ == "__main__":
    asyncio.run(main())
