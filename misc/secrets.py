from blaseball_mike import database


def show_secrets() -> None:
    sim = database.get_simulation_data()
    games = database.get_games(season=sim["season"] + 1, day=sim["day"] + 1)
    secret_runners: dict[str, str] = {
        game["homeTeamNickname"]: game["secretBaserunner"]
        for game in games.values()
    }
    runner_ids = [runner_id for runner_id in secret_runners.values() if runner_id]
    runners = {}
    if any(runner_ids):
        runners = database.get_player(id_=runner_ids)

    for team, runner in secret_runners.items():
        if runner:
            print(f"{runners[runner]['name']} is hiding at {team}")
        else:
            print(f"No one is hiding at {team}")


if __name__ == "__main__":
    show_secrets()
