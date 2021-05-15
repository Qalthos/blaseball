from blaseball_mike import chronicler
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

console = Console()
players = chronicler.get_players()


def sort_players(*stats: str) -> Text:
    all_stars = []
    for player in players:
        data = player["data"]
        player = sum(data.get(f"{stat}Rating", 0) for stat in stats)

        items = 0
        if data.get("items"):
            try:
                items = sum(sum(item.get(f"{stat}Rating", 0) for stat in stats) for item in data["items"])
            except TypeError:
                # IDK
                pass

        all_stars.append((player + items, player, items, data["name"]))

    rendered = Text()
    for total, rating, items, player in sorted(all_stars, reverse=True)[:20]:
        rendered.append(f"{player}: {rating * 5:0.1f} + {items * 5:0.1f}\n")
    return rendered


def main() -> None:
    layout = Layout()
    layout.split_row(
        Layout(name="all"),
        Layout(name="bats"),
        Layout(name="run"),
        Layout(name="def"),
        Layout(name="pitch"),
    )
    layout["all"].update(Panel(
        sort_players("hitting", "defense", "baserunning", "pitching"),
        title="Overall",
    ))
    layout["bats"].update(Panel(
        sort_players("hitting"),
        title="Batting",
    ))
    layout["def"].update(Panel(
        sort_players("defense"),
        title="defense",
    ))
    layout["run"].update(Panel(
        sort_players("baserunning"),
        title="Baserunning",
    ))
    layout["pitch"].update(Panel(
        sort_players("pitching"),
        title="Pitching",
    ))
    console.print(layout)


if __name__ == "__main__":
    main()
