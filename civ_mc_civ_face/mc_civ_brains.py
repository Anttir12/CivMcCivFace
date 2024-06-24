import json


class McCivBrainException(Exception):
    pass


class McCivBrains:

    def __init__(self, game_file_location):
        self.game_file_location = game_file_location
        self.game_db = self._read_game_db()

    def _read_game_db(self):
        with open(self.game_file_location, "r") as file:
            return json.loads(file.read())

    def reset(self):
        self.game_db = {}
        self.save_game_database()

    def create_game(self, game_name, channel_id, channel_name):
        if game_name in self.game_db:
            raise McCivBrainException("game \"{}\" already exists".format(game_name))
        game_data = {"turn": 0, "players": {}, "channel": {"id": channel_id, "name": channel_name},
                     "player_turn_order": [], "groups": []}
        self.save_game_data(game_name, game_data)

    def delete_game(self, game_name):
        if game_name not in self.game_db:
            raise McCivBrainException("game \"{}\" does not exist".format(game_name))
        del self.game_db[game_name]
        self.save_game_database()

    def add_player_to_game(self, game_name, in_game_name, discord_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        game_data["players"][in_game_name] = {
            "discord_name": discord_name,
            "mention": True,
            "early_mention": False
        }
        self.save_game_data(game_name, game_data)

    def notify_group(self, game_name, discord_group):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        game_data["groups"].append(discord_group)
        self.save_game_data(game_name, game_data)

    def remove_group(self, game_name, discord_group):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        game_data["groups"].remove(discord_group)
        self.save_game_data(game_name, game_data)

    def remove_player_from_game(self, game_name, ingame_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        if ingame_name not in game_data["players"]:
            raise McCivBrainException("Player {} not in game \"{}\"".format(ingame_name, game_name))
        else:
            del game_data["players"][ingame_name]
            self.save_game_database()

    def save_game_database(self):
        with open(self.game_file_location, "w") as f:
            f.write(json.dumps(self.game_db))

    def save_game_data(self, game_name: str, data: dict):
        self.game_db[game_name] = data
        self.save_game_database()

    def get_discord_username(self, game_name, player_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        player = game_data["players"].get(player_name)
        if not player:
            return None
        name = player.get("discord_name")
        return name

    def get_channel_for_game(self, game_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        return game_data.get("channel", {}).get("id") if game_data else None

    def toggle_mention(self, game_name, author):
        game_data = self.game_db.get(game_name)
        for player, data in game_data.get("players").items():
            discord_name = data.get("discord_name")
            if discord_name == author:
                data["mention"] = not data.get("mention")
                self.save_game_database()
                return data.get("mention")

    def get_every_game_info(self):
        game_info = list()
        for game in self.game_db:
            game_info.append(self.get_game_info(game))
        return game_info

    def get_game_info(self, game_name):
        game_data = self.game_db.get(game_name)
        info = ""
        if game_data:
            info += "Game: {}\n".format(game_name)
            info += "\tTurn: {}\n".format(game_data["turn"])
            if "turn_player" in game_data:
                info += "\tPlayer Turn: {}\n".format(game_data["turn_player"])
            info += "\tAdded players: \n{}\n".format(self.get_player_info_for_game(game_name))
        return info

    def get_player_info_for_game(self, game_name, line_prefix="\t\t"):
        info = ""
        players = self.game_db[game_name]["players"]
        for player, data in players.items():
            info += "{prefix}{player}\n".format(prefix=line_prefix, player=player)
            if "discord_name" in data:
                info += "{prefix}\tDiscord name: {dname}\n".format(prefix=line_prefix, dname=data["discord_name"])
            info += "{prefix}\tMention: {mention}\n".format(prefix=line_prefix, mention=data.get("mention", False))
            info += "{prefix}\tEarly mention: {mention}\n".format(prefix=line_prefix, mention=data.get("early_mention", False))
        if "player_turn_order" in self.game_db[game_name]:
            info += "Player turn order: {}\n".format(" -> ".join(self.game_db[game_name]["player_turn_order"]))
        return info

    def toggle_early_mention(self, game_name, author):
        game_data = self.game_db.get(game_name)
        for player, data in game_data.get("players").items():
            discord_name = data.get("discord_name")
            if discord_name == author:
                data["early_mention"] = not data.get("early_mention")
                self.save_game_database()
                return data.get("early_mention")

    def whose_turn(self, game_name):
        """
        :param game_name: name of the game
        :return: Player or discord name and True if the returned name is discord name, else False
        """
        game_data = self.game_db.get(game_name)
        if not game_data:
            raise McCivBrainException("Could not find game \"{}\"".format(game_name))
        player = game_data.get("turn_player")
        if player:
            discord_username = self.get_discord_username(game_name, player)
            if discord_username:
                return discord_username, True
            return player, False
        else:
            raise McCivBrainException("No turn information available??")
