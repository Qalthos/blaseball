from blaseball_mike import chronicler, database

PARTY_START = 7
NOW = database.get_simulation_data()["season"]

# Look at complete seasons
for season in range(PARTY_START, NOW):
    times = chronicler.time_season(season=season)[0]

    updates = chronicler.get_team_updates(
        after=times["startTime"],
        before=times["endTime"],
        order="asc",
    )
    print(updates[0])

    # parties = chronicler.get_game_updates(
    #     after=times["startTime"],
    #     before=times["endTime"],
    #     search="is Partyng!",
    # )
