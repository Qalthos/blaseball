import asyncio

from blaseball_mike.events import stream_events
from blaseball_mike.stream_model import StreamData
import requests
from rich.live import Live

from standings import display, postseason, season


async def read_events(live: Live):
    leagues = None
    async for event in stream_events():
        stream_data = StreamData(event)

        if stream_data.leagues:
            leagues = stream_data.leagues

        if (games := stream_data.games) and leagues is not None:
            if games.sim.day < 99:
                game_data = season.get_standings(games, leagues)
                display.update_standings(game_data, games.sim)
            else:
                postseason_data = postseason.get_playoffs(games, leagues)
                display.update_postseason(postseason_data)

        live.refresh()


async def main() -> None:
    with Live(display.layout, auto_refresh=False) as live:
        while True:
            try:
                await read_events(live)
            except requests.exceptions.HTTPError:
                pass


if __name__ == "__main__":
    asyncio.run(main())
