import argparse
import time
from functools import partial
from typing import Optional, Union

from blaseball_mike import database
from rich.live import Live
from rich.table import Table
from rich.text import Text

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


def player_feed(player: str, category: Optional[int]):
    return _do_feed(database.get_feed_player(player, category=category))


def team_feed(team: str, category: Optional[int]):
    return _do_feed(database.get_feed_team(team, category=category))


def global_feed(category: Optional[int]):
    return _do_feed(database.get_feed_global(category=category))


def _do_feed(feed: list[dict]) -> Table:
    table = Table()
    table.add_column("Day")
    table.add_column("Description")
    table.add_column("Changes")

    print(feed[0])
    for entry in feed:
        day = f"{entry['season'] + 1}-{entry['day'] + 1}"
        description = entry["description"]

        metadata = entry["metadata"]
        changes: Union[str, Text] = f"{entry['type']}: {metadata}"
        if entry["type"] == 29:
            # Entity talking
            changes = ""
        elif entry["type"] == 57:
            # Ballpark renovations
            changes = ""
        elif entry["type"] == 70:
            # Grind Rail trick
            changes = ""
        elif entry["type"] == 106:
            # Modification added
            mod_type = MOD[metadata["type"]]
            changes = Text.assemble(
                "+",
                (f"{metadata['mod']}", mod_type),
            )
        elif entry["type"] == 107:
            # Modification removed
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
                f"{metadata['aPlayerName']}: {LOC[metadata['aLocation']]} -> {LOC[metadata['bLocation']]}\n"
                f"{metadata['bPlayerName']}: {LOC[metadata['bLocation']]} -> {LOC[metadata['aLocation']]}"
            )
        elif entry["type"] == 115:
            # Move a player
            changes = (
                f"{metadata['playerName']}: {metadata['sendTeamName']} "
                f"{LOC[metadata['location']]} -> {metadata['receiveTeamName']} "
                f"{LOC[metadata['receiveLocation']]}"
            )
        elif entry["type"] == 117:
            # Player stars increased
            changes = Text.assemble(
                f"{metadata['before'] * 5:0.1f} -> ",
                (f"{metadata['after'] * 5:0.1f}", "green"),
            )
        elif entry["type"] == 118:
            # Player stars decreased
            changes = Text.assemble(
                f"{metadata['before'] * 5:0.1f} -> ",
                (f"{metadata['after'] * 5:0.1f}", "red"),
            )
        elif entry["type"] == 127:
            # Item stats increasing
            changes = Text.assemble(
                f"{metadata['itemName']}: ",
                f"{metadata['playerItemRatingBefore'] * 5:0.1f} -> ",
                (f"{metadata['playerItemRatingAfter'] * 5:0.1f}", "green"),
            )
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
        elif entry["type"] == 180:
            # Player secret stats reduced?
            changes = Text.assemble(
                f"{metadata['before']:0.2f} -> ",
                (f"{metadata['after']:0.2f}", "red"),
            )

        table.add_row(day, description, changes)

    return table


def main():
    parser = argparse.ArgumentParser(description="Show Blaseball Feeds")
    parser.add_argument("--category", type=int, default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--team", type=str)
    group.add_argument("--player", type=str)

    args = parser.parse_args()
    if args.player:
        func = partial(player_feed, args.player, args.category)
    elif args.team:
        func = partial(team_feed, args.team, args.category)
    else:
        func = partial(global_feed, args.category)

    with Live(func()) as live:
        while True:
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                break

            live.update(func())


if __name__ == "__main__":
    main()
