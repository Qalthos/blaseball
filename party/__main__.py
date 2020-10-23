from blaseball_mike import database

from party.models.subleague import Subleague


def main() -> None:
    sim_data = database.get_simulation_data()
    game_day = sim_data["day"] + 1
    games_left = 99 - game_day

    # Pick out all standings
    season = database.get_season(season_number=sim_data["season"] + 1)
    standings = database.get_standings(id_=season["standings"])

    # Get teams
    all_teams = database.get_all_teams()
    league = database.get_league(id_=sim_data["league"])
    # IDK why this is so weird
    tiebreakers = database.get_tiebreakers(id=league["tiebreakers"])[league["tiebreakers"]]
    print(f"{league['name']} Day {game_day}", end="\n\n")
    for subleague_id in league["subleagues"]:
        subleague = Subleague.load(
            id_=subleague_id,
            all_teams=all_teams,
            standings=standings,
            tiebreakers=tiebreakers["order"],
        )
        print(subleague.name)
        print("Current playoff teams:")
        for team in subleague.playoff:
            if team.wins - subleague.playoff_cutoff[0] > games_left:
                print(f"{team} 🏆")
            else:
                print(team)
        print()
        required_losses = games_left - subleague.playoff_cutoff[0]
        for team in subleague.remainder:
            party_countdown = required_losses + team.wins
            if party_countdown <= 0:
                print(f"{team} 🥳🎉")
            else:
                print(f"{team} {party_countdown} losses until party time")
                points_per_game = team.wins / game_day
                delta_to_playoffs = subleague.playoff_cutoff[0] - team.wins
                if delta_to_playoffs > games_left * points_per_game:
                    print(f"  Estimated to occur on day {(subleague.playoff_cutoff[0] - 99) // (points_per_game - 1) + 1:.0f}")

        print()


if __name__ == "__main__":
    main()
