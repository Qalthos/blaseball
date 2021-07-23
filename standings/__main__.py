import asyncio

from blaseball_mike.events import stream_events
from rich.live import Live

from models.live import StreamData
from standings import display, postseason, season


async def main() -> None:
    leagues = None
    with Live(display.layout, auto_refresh=False) as live:
        async for event in stream_events():
            stream_data = StreamData.parse_obj(event)

            if stream_data.leagues:
                leagues = stream_data.leagues

            if (games := stream_data.games) and leagues is not None:
                if games.sim.day < 99:
                    game_data = season.get_standings(games, leagues)
                    display.update_standings(game_data, games.sim.day + 1)
                else:
                    postseason_data = postseason.get_playoffs(games, leagues)
                    display.update_postseason(postseason_data)

            live.refresh()


if __name__ == "__main__":
    asyncio.run(main())
