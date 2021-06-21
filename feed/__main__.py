import argparse
import time
from functools import partial
from typing import Any, Optional, Union

from blaseball_mike import database
from blaseball_mike.models import Weather
from blaseball_mike.tables import StatType, Tarot
from rich.live import Live
from rich.table import Table
from rich.text import Text

from feed.enums import Location, ModColor

JSON = dict[str, Any]
TAROT = "#a16dc3"
ITEM = "#6dc0ff"
ITEM_MOD = "bababa"
GAIN = Text("+", style="green")
LOSE = Text("-", style="red")

STAT_TYPE = [
    "Batting",
    "Pitching",
    "Defense",
    "Baserunning",
    "Combined",
]

NO_CHANGE = [
    -1,  # Redacted
    2,  # Inning half announcement
    7,  # Flyout
    8,  # Ground out
    9,  # Home run
    10,  # Single
    11,  # End of game announcement
    12,  # Batter up announcement
    13,  # Strike, swinging
    14,  # Ball
    15,  # Foul ball
    29,  # Entity talking
    54,  # Incineration
    57,  # Ballpark renovations
    60,  # Blessing won
    70,  # Grind Rail trick
    125,  # Entering the Hall
    126,  # Exiting the Hall
    131,  # Reverb lineup shuffle
    132,  # Reverb rotation shuffle
    137,  # New player hatching
    153,  # Team had a stat mass changed
]


def player_feed(player: str, category: Optional[int]) -> list[JSON]:
    return database.get_feed_player(player, category=category)


def team_feed(team: str, category: Optional[int]) -> list[JSON]:
    return database.get_feed_team(team, category=category)


def global_feed(category: Optional[int]) -> list[JSON]:
    return database.get_feed_global(category=category)


def _do_feed(feed: list[JSON], excludes: list[str]) -> Table:
    table = Table(expand=True)
    table.add_column("Day")
    table.add_column("Description")
    table.add_column("Changes", max_width=20)

    for entry in feed:
        day = f"{entry['season'] + 1}-{entry['day'] + 1}"
        description = entry["description"]

        metadata = entry["metadata"]
        changes: Union[str, Text] = f"{entry['type']}: {metadata}"
        if entry["type"] in NO_CHANGE:
            changes = ""
        elif entry["type"] == 26:
            # Weather changed
            changes = Text.assemble(
                f"{Weather.load_one(metadata['before']).name} -> ",
                Weather.load_one(metadata["after"]).name,
            )
        elif entry["type"] == 81:
            # Tarot reading
            changes = Text(
                "\n".join(Tarot(card).text for card in metadata["spread"]),
                style=TAROT,
            )
        elif entry["type"] == 106:
            # Modification added
            if metadata["mod"] in excludes:
                continue
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                GAIN,
                (f"{metadata['mod']}", mod_type),
            )
        elif entry["type"] == 107:
            # Modification removed
            if metadata["mod"] in excludes:
                continue
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                LOSE,
                (f"{metadata['mod']}", mod_type),
            )
        elif entry["type"] == 108:
            # Modifications expiring
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                LOSE,
                (metadata["mods"][0], mod_type),
            )
            for mod in metadata["mods"][1:]:
                changes.append("\n")
                changes.append(LOSE)
                changes.append(mod, style=mod_type)
        elif entry["type"] == 109:
            # Player added to team
            location = Location(metadata["location"]).name
            changes = f"{location}: +{metadata['playerName']}"
        elif entry["type"] == 112:
            # Player removed from team
            changes = f"{metadata['teamName']}: -{metadata['playerName']}"
        elif entry["type"] == 113:
            # Exchange players between teams
            location_a = Location(metadata["aLocation"]).name
            location_b = Location(metadata["bLocation"]).name
            changes = (
                f"{metadata['aPlayerName']}: {metadata['aTeamName']} {location_a}"
                f" -> {metadata['bTeamName']} {location_b}\n"
                f"{metadata['bPlayerName']}: {metadata['bTeamName']} {location_b}"
                f" -> {metadata['aTeamName']} {location_a}"
            )
        elif entry["type"] == 114:
            # Exchange players within a team
            location_a = Location(metadata["aLocation"]).name
            location_b = Location(metadata["bLocation"]).name
            changes = (
                f"{metadata['aPlayerName']}:\n"
                f" {location_a} -> {location_b}\n"
                f"{metadata['bPlayerName']}:\n"
                f" {location_b} -> {location_a}"
            )
        elif entry["type"] == 115:
            # Move a player
            location_src = Location(metadata["location"]).name
            location_dest = Location(metadata["receiveLocation"]).name
            changes = (
                f"{metadata['playerName']}: "
                f"{metadata['sendTeamName']} {location_src} -> "
                f"{metadata['receiveTeamName']} {location_dest}"
            )
        elif entry["type"] == 116:
            # Replace a player
            location = Location(metadata["location"]).name
            changes = (
                f"{metadata['teamName']} {location}: "
                f"{metadata['outPlayerName']} -> {metadata['inPlayerName']} "
            )
        elif entry["type"] == 117:
            # Player stars increased
            block = STAT_TYPE[metadata["type"]]
            changes = Text.assemble(
                f"{block}: {_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata["after"]), "green"),
            )
        elif entry["type"] == 118:
            # Player stars decreased
            block = STAT_TYPE[metadata["type"]]
            changes = Text.assemble(
                f"{block}: {_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata["after"]), "red"),
            )
        elif entry["type"] == 122:
            # Superallergic reaction
            changes = Text.assemble(
                f"{_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata["after"]), "red"),
            )
        elif entry["type"] == 127:
            # Player item added
            item = _item_stars(metadata["playerItemRatingAfter"])
            player = _to_stars(metadata["playerRating"])
            changes = Text.assemble(
                GAIN,
                f"{metadata['itemName']}:\n",
                f"  {player} -> {player} + ",
                item,
            )
            for mod in metadata["mods"]:
                changes.append("\n  ")
                changes.append(GAIN)
                changes.append(mod, style=ITEM_MOD)
        elif entry["type"] == 128:
            # Player item dropped
            item = _item_stars(metadata["playerItemRatingAfter"])
            player = _to_stars(metadata["playerRating"])
            changes = Text.assemble(
                LOSE,
                f"{metadata['itemName']}:\n",
                f"  {player} + ",
                item,
                f" -> {player}",
            )
            for mod in metadata["mods"]:
                changes.append("\n  ")
                changes.append(LOSE)
                changes.append(mod)
        elif entry["type"] == 144:
            # Exchange modifications
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                (metadata["from"], mod_type),
                " -> ",
                (metadata["to"], mod_type),
            )
        elif entry["type"] == 145:
            # Alternate called
            changes = (
                f"{_to_stars(metadata['before'])} -> "
                f"{_to_stars(metadata['after'])}"
            )
        elif entry["type"] == 146:
            # Modifier added by source
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                f"{metadata['source']}:\n  ",
                GAIN,
                (metadata["mod"], mod_type),
            )
        elif entry["type"] == 147:
            # Modifier removed by source
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                f"{metadata['source']}:\n  ",
                LOSE,
                (metadata["mod"], mod_type),
            )
        elif entry["type"] == 148:
            # Modifier exchange with source
            mod_type = ModColor(metadata["type"]).name
            changes = Text.assemble(
                f"{metadata['source']}:\n  ",
                (metadata["from"], mod_type),
                " -> ",
                (metadata["to"], mod_type),
            )
        elif entry["type"] == 171:
            # A dependent mod was removed due to its dependency being removed
            changes = Text(f"{metadata['source']}:")
            for mod in metadata["removes"]:
                mod_type = ModColor(mod["type"]).name
                changes.append("\n  ")
                changes.append(LOSE)
                changes.append(mod["mod"], style=mod_type)
        elif entry["type"] == 172:
            # Dependent mods were added by another mod
            changes = Text(f"{metadata['source']}:")
            for mod in metadata["adds"]:
                mod_type = ModColor(mod["type"]).name
                changes.append("\n  ")
                changes.append(GAIN)
                changes.append(mod["mod"], style=mod_type)
        elif entry["type"] == 179:
            # Player advanced stats increased
            stat = StatType(metadata["type"]).stat_name.capitalize()
            changes = Text.assemble(
                f"{stat}:\n  ",
                f"{_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata['after']), "green"),
            )
        elif entry["type"] == 180:
            # Player advanced stats reduced
            stat = StatType(metadata["type"]).stat_name.capitalize()
            changes = Text.assemble(
                f"{stat}:\n  ",
                f"{_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata['after']), "red"),
            )
        elif entry["type"] == 184:
            # Player item is restored?
            changes = Text.assemble(
                _item_durability(metadata),
                f"\n  {_to_stars(metadata['playerRating'])}",
                f" -> {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingAfter"]),
            )
        elif entry["type"] == 185:
            # Player item is destroyed
            changes = Text.assemble(
                _item_durability(metadata),
                f"\n  {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingBefore"]),
                f" -> {_to_stars(metadata['playerRating'])}",
            )
        elif entry["type"] == 186:
            # Player item is damaged
            changes = _item_durability(metadata)
        elif entry["type"] == 187:
            # Player item is restored?
            changes = Text.assemble(
                _item_durability(metadata),
                f"\n  {_to_stars(metadata['playerRating'])}",
                f" -> {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingAfter"]),
            )
        elif entry["type"] == 188:
            # Player item is repaired
            changes = _item_durability(metadata)
        elif entry["type"] == 199:
            # Player Soul restored
            changes = Text.assemble(
                f"{metadata['before']} -> ",
                (str(metadata["after"]), "green"),
            )
        elif entry["type"] == 206:
            # Hype building
            changes = Text.assemble(
                f"{metadata['before']:0.2f} -> ",
                (f"{metadata['after']:0.2f}", "green"),
            )

        table.add_row(day, description, changes)

    return table


def _to_stars(rating: float) -> str:
    return f"{rating * 5:0.1f}"


def _item_stars(rating: float) -> Text:
    if rating is None:
        # I really don't know what to do about this
        return "???"
    style = ITEM if rating >= 0 else "red"
    return Text(_to_stars(rating), style=style)


def _item_durability(metadata: JSON) -> Text:
    durability = metadata["itemDurability"]
    health_before = metadata["itemHealthBefore"]
    before = "●" * health_before + "○" * (durability - health_before)
    health_after = metadata["itemHealthAfter"]
    after = "●" * health_after + "○" * (durability - health_after)
    after_color = "green" if health_after > health_before else "red"
    return Text.assemble(
        str(health_before),
        (before, ITEM),
        " -> ",
        (str(health_after), after_color),
        (after, ITEM),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Show Blaseball Feeds")
    parser.add_argument("-c", "--category", type=int, default=None)
    parser.add_argument("-n", "--interval", type=int, default=60)
    parser.add_argument("--no-ghosts", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--team", type=str)
    group.add_argument("-p", "--player", type=str)
    args = parser.parse_args()

    excludes = []
    if args.no_ghosts:
        excludes.append("INHABITING")

    if args.player:
        func = partial(player_feed, args.player, args.category)
    elif args.team:
        func = partial(team_feed, args.team, args.category)
    else:
        func = partial(global_feed, args.category)

    with Live(Table(), vertical_overflow="crop") as live:
        while True:
            live.update(_do_feed(func(), excludes))

            try:
                time.sleep(args.interval)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
