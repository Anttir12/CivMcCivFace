import unittest

from civ_mc_civ_face.mc_civ_brains import McCivBrains, McCivBrainException


class MyTestCase(unittest.TestCase):

    def test_toggle_mention_me(self):
        test_file = "test_game_file.json"
        brains = McCivBrains(test_file)
        self.assertEqual(False, brains.toggle_mention("test", "discord_id#1234"))
        self.assertEqual(True, brains.toggle_mention("test", "discord_id#1234"))

    def test_toggle_early_mention(self):
        test_file = "test_game_file.json"
        brains = McCivBrains(test_file)
        self.assertEqual(True, brains.toggle_early_mention("test", "discord_id#1234"))
        self.assertEqual(False, brains.toggle_early_mention("test", "discord_id#1234"))

if __name__ == '__main__':
    unittest.main()
