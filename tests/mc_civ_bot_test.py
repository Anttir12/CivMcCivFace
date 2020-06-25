import unittest

from civ_mc_civ_face.mc_civ_bot import CivMcCivFace


class MyTestCase(unittest.TestCase):

    def test_webhook(self):
        test_file = "face_test.json"
        face = CivMcCivFace(test_file, "guild_name", "global_settings", command_prefix="foobar")
        face.brains.reset()
        face.brains.create_game("test_game", "id", "name")
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "0"})
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "0"})
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "1"})
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "1"})
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 1", "value3": "2"})
        face.handle_webhook_message({"value1": "test_game", "value2": "Player 2", "value3": "2"})


if __name__ == '__main__':
    unittest.main()
