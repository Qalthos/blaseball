#!/usr/bin/env python
import asyncio
from typing import TypedDict
import json

from blaseball_mike.events import stream_events
from rich.progress import Progress, BarColumn, TimeRemainingColumn


class GamesData(TypedDict):
    sim: dict
    season: dict
    standings: dict
    schedule: list[dict]
    tomorrowSchedule: list[dict]
    postseason: dict


class LeagueData(TypedDict):
    leagues: dict
    stadiums: dict
    subleagues: dict
    divisions: dict
    teams: dict
    tiebreakers: dict
    stats: dict


class StreamData(TypedDict):
    games: GamesData
    leagues: LeagueData
    fights: dict
    temporal: dict


async def main():
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.completed}/{task.total}",
        TimeRemainingColumn(),
        expand=True,
    )
    with progress:
        chest = progress.add_task("Community Chest", total=3000)
        async for event in stream_events():
            if "leagues" in event:
                chest_stats = event["leagues"]["stats"]["communityChest"]
                progress.update(chest, completed=float(chest_stats["runs"]))


asyncio.run(main())
