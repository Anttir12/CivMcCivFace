import unittest
from unittest import mock

from civ_mc_civ_face.mc_civ_brains import McCivBrains, McCivBrainException
from tests import mock_data


@mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains.save_game_database", mock.Mock())
class MyTestCase(unittest.TestCase):

    # mock.patch as class decorator only works for test_* functions.
    @mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains._read_game_db",
                side_effect=mock_data.get_test_game_file)
    def setUp(self, mocked_read_game_db):
        self.brains = McCivBrains("test_file")
        mocked_read_game_db.assert_called_once()

    def test_toggle_mention_me(self):
        self.brains.test = 12323
        self.assertFalse(self.brains.toggle_mention("test", "discord_id#1234"))
        self.assertTrue(self.brains.toggle_mention("test", "discord_id#1234"))

    def test_toggle_early_mention(self):
        self.assertTrue(self.brains.toggle_early_mention("test", "discord_id#1234"))
        self.assertFalse(self.brains.toggle_early_mention("test", "discord_id#1234"))

    def test_add_and_remove_group_notification(self):
        self.brains.notify_group("test", "discord_group_id#1234")
        groups = self.brains.game_db.get("test")["groups"]
        self.assertEqual(1, len(groups))
        self.brains.remove_group("test", "discord_group_id#1234")
        self.assertEqual(0, len(groups))

    def test_create_game(self):
        self.brains.create_game("new_game", "1234", "test_channel")
        game_data = self.brains.game_db.get("new_game")
        self.assertIsNotNone(game_data)  # exists
        self.assertEqual("1234", game_data["channel"]["id"])
        self.assertEqual("test_channel", game_data["channel"]["name"])
        self.assertEqual({}, game_data["players"])
        self.assertEqual([], game_data["groups"])
        self.assertEqual([], game_data["player_turn_order"])

    def test_create_duplicate_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.create_game("test", "1", "channel")
        self.assertEqual("game \"test\" already exists", str(context.exception))

    def test_delete_game(self):
        self.assertIn("test", self.brains.game_db)  # Make sure the test game exists
        self.brains.delete_game("test")
        self.assertNotIn("test", self.brains.game_db)  # Make sure the test game is deleted

    def test_add_player_to_game(self):
        self.brains.add_player_to_game("test", "player1", "user1")
        player_data = self.brains.game_db["test"]["players"].get("player1")
        self.assertIsNotNone(player_data)
        self.assertEqual("user1", player_data["discord_name"])
        self.assertTrue(player_data["mention"])
        self.assertFalse(player_data["early_mention"])

    def test_add_player_to_non_existing_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.add_player_to_game("idontexist", "player1", "user1")
        self.assertEqual("Could not find game \"idontexist\"", str(context.exception))

    def test_remove_player_from_game(self):
        self.brains.remove_player_from_game("test", "civ_nick")
        self.assertNotIn("civ_nick", self.brains.game_db["test"]["players"])

    def test_remove_nonexistent_player_from_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.remove_player_from_game("test", "koffi")
        self.assertEqual("Player koffi not in game \"test\"", str(context.exception))

    def test_remove_player_from_nonexistent_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.remove_player_from_game("foo", "koffi")
        self.assertEqual("Could not find game \"foo\"", str(context.exception))

    def test_get_discord_username(self):
        discord_name = self.brains.get_discord_username("test", "civ_nick")
        self.assertEqual("discord_id#1234", discord_name)

    def test_get_nonexistent_discord_username(self):
        discord_name = self.brains.get_discord_username("test", "foo")
        self.assertIsNone(discord_name)

    def test_get_discord_username_from_nonexistent_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.get_discord_username("bar", "foo")
        self.assertEqual("Could not find game \"bar\"", str(context.exception))

    def test_get_channel_for_game(self):
        channel_id = self.brains.get_channel_for_game("test")
        self.assertEqual(123456789, channel_id)

    def test_get_channel_for_nonexistent_game(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.get_channel_for_game("bar")
        self.assertEqual("Could not find game \"bar\"", str(context.exception))

    def test_whose_turn(self):
        self.brains.game_db["test"]["turn_player"] = "foobar"  # Manually set the turn for foobar
        player, is_discord_name = self.brains.whose_turn("test")
        self.assertFalse(is_discord_name)
        self.assertEqual("foobar", player)

    def test_whose_turn_with_discord_name(self):
        player, is_discord_name = self.brains.whose_turn("test")
        self.assertTrue(is_discord_name)
        self.assertEqual("discord_id#1234", player)

    def test_whose_turn_with_game_not_found(self):
        with self.assertRaises(McCivBrainException) as context:
            self.brains.whose_turn("barfoo")
        self.assertEqual("Could not find game \"barfoo\"", str(context.exception))

if __name__ == '__main__':
    unittest.main()
