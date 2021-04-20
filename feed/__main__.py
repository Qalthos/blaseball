import argparse
import time
from functools import partial
from typing import Any, Optional, Union

from blaseball_mike import database
from rich.live import Live
from rich.table import Table
from rich.text import Text

JSON = dict[str, Any]
LOC = [
    "Lineup",
    "Rotation",
    "Shadow Lineup",
    "Shadow Rotation",
]
MOD = [
    "#dbbc0b",
    "#c2157a",
    "#0a78a3",
    "#639e47",
]
TAROT = "#a16dc3"
ITEM = "#6dc0ff"


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
        if entry["type"] == 29:
            # Entity talking
            changes = ""
        elif entry["type"] == 54:
            # Incineration
            changes = ""
        elif entry["type"] == 57:
            # Ballpark renovations
            changes = ""
        elif entry["type"] == 70:
            # Grind Rail trick
            changes = ""
        elif entry["type"] == 81:
            # Tarot reading
            changes = Text(
                " ".join(str(card + 1) for card in metadata["spread"]),
                style=TAROT,
            )
        elif entry["type"] == 106:
            # Modification added
            if metadata["mod"] in excludes:
                continue
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                "+",
                (f"{metadata['mod']}", mod_type),
            )
        elif entry["type"] == 107:
            # Modification removed
            if metadata["mod"] in excludes:
                continue
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                "-",
                (f"{metadata['mod']}", mod_type),
            )
        elif entry["type"] == 108:
            # Modifications expiring
            mod_type = MOD[metadata["type"]]
            changes = Text("-")
            changes.append(metadata["mods"][0], style=mod_type)
            for mod in metadata["mods"][1:]:
                changes.append(" -")
                changes.append(mod, style=mod_type)
        elif entry["type"] == 109:
            # Player added to team
            changes = f"{LOC[metadata['location']]}: +{metadata['playerName']}"
        elif entry["type"] == 113:
            # Exchange players between teams
            changes = (
                f"{metadata['aPlayerName']}: {metadata['aTeamName']} {LOC[metadata['aLocation']]}"
                f" -> {metadata['bTeamName']} {LOC[metadata['bLocation']]}\n"
                f"{metadata['bPlayerName']}: {metadata['bTeamName']} {LOC[metadata['bLocation']]}"
                f" -> {metadata['aTeamName']} {LOC[metadata['aLocation']]}"
            )
        elif entry["type"] == 114:
            # Exchange players within a team
            changes = (
                f"{metadata['aPlayerName']}:\n"
                f" {LOC[metadata['aLocation']]} -> {LOC[metadata['bLocation']]}\n"
                f"{metadata['bPlayerName']}:\n"
                f" {LOC[metadata['bLocation']]} -> {LOC[metadata['aLocation']]}"
            )
        elif entry["type"] == 115:
            # Move a player
            changes = (
                f"{metadata['playerName']}: {metadata['sendTeamName']} "
                f"{LOC[metadata['location']]} -> {metadata['receiveTeamName']} "
                f"{LOC[metadata['receiveLocation']]}"
            )
        elif entry["type"] == 116:
            # Replace a player
            changes = (
                f"{metadata['teamName']} {LOC[metadata['location']]}: "
                f"{metadata['outPlayerName']} -> {metadata['inPlayerName']} "
            )
        elif entry["type"] == 117:
            # Player stars increased
            changes = Text.assemble(
                f"{_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata["after"]), "green"),
            )
        elif entry["type"] == 118:
            # Player stars decreased
            changes = Text.assemble(
                f"{_to_stars(metadata['before'])} -> ",
                (_to_stars(metadata["after"]), "red"),
            )
        elif entry["type"] == 125:
            # Entering the Hall
            changes = ""
        elif entry["type"] == 127:
            # Player item added
            item = _item_stars(metadata["playerItemRatingAfter"])
            player = _to_stars(metadata["playerRating"])
            changes = Text.assemble(
                ("+", "green"),
                f"{metadata['itemName']}:\n",
                f"  {player} -> {player} + ",
                item,
            )
            for mod in metadata["mods"]:
                changes.append(f"\n  +{mod}")
        elif entry["type"] == 128:
            # Player item dropped
            item = _item_stars(metadata["playerItemRatingAfter"])
            player = _to_stars(metadata["playerRating"])
            changes = Text.assemble(
                ("-", "red"),
                f"{metadata['itemName']}:\n",
                f"  {player} + ",
                item,
                f" -> {player}",
            )
            for mod in metadata["mods"]:
                changes.append(f"\n  -{mod}")
        elif entry["type"] == 131:
            # Reverb lineup shuffle
            changes = ""
        elif entry["type"] == 132:
            # Reverb rotation shuffle
            changes = ""
        elif entry["type"] == 137:
            # New player hatching
            changes = ""
        elif entry["type"] == 144:
            # Exchange modifications
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                (metadata["from"], mod_type),
                " -> ",
                (metadata["to"], mod_type),
            )
        elif entry["type"] == 146:
            # Modifier added by source
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                f"{metadata['source']}:\n  +",
                (metadata["mod"], mod_type),
            )
        elif entry["type"] == 147:
            # Modifier removed by source
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                f"{metadata['source']}:\n  -",
                (metadata["mod"], mod_type),
            )
        elif entry["type"] == 148:
            # Modifier exchange with source
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                f"{metadata['source']}:\n  ",
                (metadata["from"], mod_type),
                " -> ",
                (metadata["to"], mod_type),
            )
        elif entry["type"] == 153:
            # Team had a stat mass changed
            changes = ""
        elif entry["type"] == 171:
            # A dependent mod was removed due to its dependency being removed
            changes = Text(f"{metadata['source']}:")
            for mod in metadata["removes"]:
                changes.append("\n  -")
                changes.append(mod["mod"], style=MOD[mod["type"]])
        elif entry["type"] == 172:
            # Dependent mods were added by another mod
            changes = Text(f"{metadata['source']}:")
            for mod in metadata["adds"]:
                changes.append("\n  +")
                changes.append(mod["mod"], style=MOD[mod["type"]])
        elif entry["type"] == 180:
            # Player secret stats reduced?
            changes = Text.assemble(
                f"{metadata['before']:0.2f} -> ",
                (f"{metadata['after']:0.2f}", "red"),
            )
        elif entry["type"] == 185:
            # Player item is destroyed
            changes = Text.assemble(
                f"Durability: {metadata['itemHealthBefore']} -> ",
                (str(metadata["itemHealthAfter"]), "red"),
                f"\n  {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingBefore"]),
                f" -> {_to_stars(metadata['playerRating'])}",
            )
        elif entry["type"] == 186:
            # Player item is damaged
            changes = Text.assemble(
                f"Durability: {metadata['itemHealthBefore']} -> ",
                (str(metadata["itemHealthAfter"]), "red"),
            )
        elif entry["type"] == 187:
            # Player item is repaired
            changes = Text.assemble(
                f"Durability: {metadata['itemHealthBefore']} -> ",
                (str(metadata["itemHealthAfter"]), "green"),
                f"\n  {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingBefore"]),
                f" -> {_to_stars(metadata['playerRating'])} + ",
                _item_stars(metadata["playerItemRatingAfter"]),
            )

        table.add_row(day, description, changes)

    return table


def _to_stars(rating: float) -> str:
    return f"{rating * 5:0.1f}"


def _item_stars(rating: float) -> Text:
    if rating is None:
        # I really don't know what to do about this
        return "None?"
    style = ITEM if rating >= 0 else "red"
    return Text(_to_stars(rating), style=style)


def main():
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
