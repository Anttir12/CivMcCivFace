import unittest
from unittest import mock

from civ_mc_civ_face.mc_civ_bot import CivMcCivFace


@mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains.save_game_database", mock.Mock())
class MyTestCase(unittest.TestCase):

    @mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains._read_game_db",
                mock.MagicMock(return_value={}))
    def test_webhook(self):
        face = CivMcCivFace("asd", "guild_name", "global_settings", command_prefix="foobar")
        self.assertIsNone(face.brains.game_db.get("test_game"))  # Should not exists
        face.brains.create_game("test_game", "id", "name")
        game_db = face.brains.game_db.get("test_game")
        self.assertIsNotNone(game_db)  # Not it should be there
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "0"})
        self.assertEqual(0, game_db["turn"])
        self.assertEqual("Player 1", game_db["turn_player"])
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "0"})
        self.assertEqual(0, game_db["turn"])
        self.assertEqual("Player 2", game_db["turn_player"])
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "1"})
        self.assertEqual(1, game_db["turn"])
        self.assertEqual("Player 1", game_db["turn_player"])
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "1"})
        self.assertEqual(1, game_db["turn"])
        self.assertEqual("Player 2", game_db["turn_player"])
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "2"})
        self.assertEqual(2, game_db["turn"])
        self.assertEqual("Player 1", game_db["turn_player"])
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "2"})
        self.assertEqual(2, game_db["turn"])
        self.assertEqual("Player 2", game_db["turn_player"])


if __name__ == '__main__':
    unittest.main()
