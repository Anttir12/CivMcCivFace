import unittest
from unittest import mock

from civ_mc_civ_face.mc_civ_brains import McCivBrains, McCivBrainException
from tests import mock_data


@mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains.save_game_database", mock.Mock())
@mock.patch("civ_mc_civ_face.mc_civ_brains.McCivBrains._read_game_db",
            mock.MagicMock(return_value=mock_data.test_game_file))
class MyTestCase(unittest.TestCase):

    def test_toggle_mention_me(self):
        test_file = "test_game_file.json"
        brains = McCivBrains(test_file)
        self.assertFalse(brains.toggle_mention("test", "discord_id#1234"))
        self.assertTrue(brains.toggle_mention("test", "discord_id#1234"))

    def test_toggle_early_mention(self):
        test_file = "test_game_file.json"
        brains = McCivBrains(test_file)
        self.assertTrue(brains.toggle_early_mention("test", "discord_id#1234"))
        self.assertFalse(brains.toggle_early_mention("test", "discord_id#1234"))

    def test_add_and_remove_group_notification(self):
        test_file = "test_game_file.json"
        brains = McCivBrains(test_file)
        brains.notify_group("test", "discord_group_id#1234")
        groups = brains.game_db.get("test")["groups"]
        self.assertEqual(1, len(groups))
        brains.remove_group("test", "discord_group_id#1234")
        self.assertEqual(0, len(groups))


if __name__ == '__main__':
    unittest.main()
