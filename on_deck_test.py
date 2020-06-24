import unittest
from play_civ_bot import CivMcCivFace

civ = CivMcCivFace()


class TestCiv(unittest.TestCase):

    def test_get_next_player(self):
        game_data = {"turn": 0, "players": {}, "channel": {"id": "message.channel.id", "name": "message.channel.name"},
                     "player_turn_order": []}

        assert civ.get_next_player(game_data, "player1") is None
        assert civ.get_next_player(game_data, "player2") is None
        assert civ.get_next_player(game_data, "player3") is None
        assert civ.get_next_player(game_data, "player1") == "player2"
        assert civ.get_next_player(game_data, "player2") == "player3"
        assert civ.get_next_player(game_data, "player3") == "player1"

if __name__ == '__main__':
    unittest.main()
