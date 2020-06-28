
def get_test_game_file():
    test_game_file = {
        "test": {
            "turn": 0,
            "turn_player": "civ_nick",
            "players": {
                "civ_nick": {
                    "discord_name": "discord_id#1234",
                    "mention": True,
                    "early_mention": False
                }
            },
            "channel": {
                "id": 123456789,
                "name": "general"
            },
            "player_turn_order": [],
            "groups": []
        }
    }
    return test_game_file
