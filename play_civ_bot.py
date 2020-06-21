import asyncio
import json
import os
import shlex

import discord
from dotenv import load_dotenv

load_dotenv()
GAME_FILE = os.getenv("GAME_FILE_PATH")
GLOBAL_SETTINGS = os.getenv("GLOBAL_SETTINGS")
bot_location = os.getcwd()
if not GAME_FILE:
    GAME_FILE = os.path.join(bot_location, "game_file.json")
if os.path.exists(GAME_FILE):
    if not os.path.isfile(GAME_FILE):
        raise Exception("{} exists and is not a file!")
else:
    with open(GAME_FILE, "w") as file:
        file.write("{}")
if not GLOBAL_SETTINGS:
    GLOBAL_SETTINGS = os.path.join(bot_location, "global_settings.json")
if os.path.exists(GLOBAL_SETTINGS):
    if not os.path.isfile(GLOBAL_SETTINGS):
        raise Exception("{} exists and is not a file!")
else:
    with open(GLOBAL_SETTINGS, "w") as file:
        file.write("{}")
GUILD_NAME = os.getenv("DISCORD_GUILD_NAME")
PREFIX = "$"


class CivMcCivFace(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)
        self.guild = None
        self.brains = MvCivBrains()

    async def on_ready(self):
        print(self.guilds)
        self.guild = discord.utils.find(lambda g: g.name == GUILD_NAME, self.guilds)
        print(f'{self.user} has connected to Discord to the following server: {self.guild.name} ({self.guild.id})!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith("$"):
            command = message.content.split(":", 1)[0]
            if command == "{}create_game".format(PREFIX):
                await self.create_game(message)
            elif command == "{}delete_game".format(PREFIX):
                await self.delete_game(message)
            elif command == "{}list_games".format(PREFIX):
                await self.list_games(message)
            elif command == "{}add_player".format(PREFIX):
                await self.add_player_to_game(message)
            elif command == "{}remove_player".format(PREFIX):
                await self.remove_player_from_game(message)
            elif command == "{}reset_everything".format(PREFIX):
                await self.reset(message)
            else:
                await message.channel.send(":poop: I don't understand you :poop:")
        if message.content == "Mika olis paras civ taktiikka?":
            await message.channel.send(":radioactive: Nuke everything :radioactive:")

    async def create_game(self, message):
        try:
            game_name = message.content.split(":", 1)[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}create_game:<game_name>".format(PREFIX))
            return

        error = self.brains.create_game(game_name, message.channel.id, message.channel.name)
        if error:
            await message.channel.send(error)
        else:
            await message.channel.send("OK, I created a new game called {}".format(game_name))

    async def delete_game(self, message):
        try:
            game_name = message.content.split(":", 1)[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}delete_game:<game_name>".format(PREFIX))
            return
        error = self.brains.delete_game(game_name)
        if error:
            await message.channel.send(":poop:ERROR: try this: {}delete_game:<game_name>".format(PREFIX))
        else:
            await message.channel.send("Ok, I deleted the game \"{}\"".format(game_name))

    async def list_games(self, message):
        game_db = self.brains.game_db
        await message.channel.send("Here are currently tracked games:\n{}".format(json.dumps(game_db, indent=4,
                                                                                             sort_keys=True)))

    async def add_player_to_game(self, message):
        try:
            parameters = shlex.split(message.content.split(":", 1)[1])
            game_name = parameters[0]
            ingame_name = parameters[1]
            discord_name = parameters[2]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}add_player:<game_name> <ingame_name> <discord_name>".format(PREFIX))
            return
        error = self.brains.add_player_to_game(game_name, ingame_name, discord_name)
        if error:
            await message.channel.send("error")
        else:
            await message.channel.send("{} - {} added to {}".format(ingame_name, discord_name, game_name))

    async def remove_player_from_game(self, message):
        try:
            parameters = shlex.split(message.content.split(":", 1)[1])
            game_name = parameters[0]
            ingame_name = parameters[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}remove_player:<game_name> <ingame_name>".format(PREFIX))
            return
        error = self.brains.remove_player_from_game(game_name, ingame_name)
        if error:
            await message.channel.send(error)
        else:
            await message.channel.send("{} removed from {}".format(ingame_name, game_name))

    async def reset(self, message):
        self.brains.reset()
        await message.channel.send("Game DB has been reset")

    def handle_webhook_message(self, values: dict):
        game_name = values["value1"]
        player_name = values["value2"]
        turn_number = values["value3"]

        channel_id = self.brains.get_channel_for_game(game_name)
        channel = self.get_channel(channel_id)
        discord_username = self.brains.get_discord_username(game_name, player_name)
        mention = self.get_mention_for(discord_username)
        if not mention:
            mention = player_name
        asyncio.run_coroutine_threadsafe(channel.send("{} your turn (turn {}, {})".format(mention, turn_number, game_name)), self.loop)
        self.send_on_deck_message(game_name, player_name, channel)
        self.brains.save_game_database();

    def get_mention_for(self, discord_username):
        mention = discord_username
        if discord_username:
            discord_user = self.guild.get_member_named(discord_username)
            if discord_user:
                mention = discord_user.mention
        return mention

    def send_on_deck_message(self, game_name, player_name, channel):
        next_player = self.get_next_player(game_name,player_name)
        mention = self.get_mention_for(next_player)
        if next_player is not None:
            asyncio.run_coroutine_threadsafe(channel.send("{} you're on deck.".format(mention)), self.loop)

    def get_next_player(self, game_name, player_name):
        players = self.brains.game_db.get(game_name).get("player_turn_order")
        if player_name not in players:
            players.append(player_name)
            self.brains.save_game_database()
            return
        next_player = self.get_player_from_list(player_name, players)
        return self.brains.get_discord_username(game_name, next_player)

    def get_player_from_list(self, player_name, players):
        index = players.index(player_name)
        if index < len(players) - 1:
            return players[index+1]
        else:
            return players[0]

class MvCivBrains:

    def __init__(self):
        with open(GAME_FILE, "r") as file:
            self.game_db = json.loads(file.read())

    def reset(self):
        self.game_db = {}
        self.save_game_database()

    def create_game(self, game_name, channel_id, channel_name):
        if game_name in self.game_db:
            return ":poop:ERROR: game \"{}\" already exists".format(game_name)
        else:
            game_data = {"turn": 0, "players": {}, "channel": {"id": channel_id, "name": channel_name}, "player_turn_order":[""]}
            self.save_game_data(game_name, game_data)
        return None

    def delete_game(self, game_name):
        if game_name not in self.game_db:
            return ":poop:ERROR: game \"{}\" does not exist".format(game_name)
        del self.game_db[game_name]
        self.save_game_database()

    def add_player_to_game(self, game_name, ingame_name, discord_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            return ":poop:ERROR: Could not find game \"{}\"".format(game_name)
        game_data["players"][ingame_name] = discord_name
        self.save_game_data(game_name, game_data)

    def remove_player_from_game(self, game_name, ingame_name):
        game_data = self.game_db.get(game_name)
        if not game_data:
            return ":poop:ERROR: Could not find game \"{}\"".format(game_name)
        if ingame_name not in game_data["players"]:
            return ":poop:ERROR: Player {} not in game \"{}\"".format(ingame_name, game_name)
        else:
            del game_data["players"][ingame_name]
            self.save_game_database()

    def save_game_database(self):
        with open(GAME_FILE, "w") as f:
            f.write(json.dumps(self.game_db))

    def save_game_data(self, game_name: str, data: dict):
        self.game_db[game_name] = data
        self.save_game_database()

    def get_discord_username(self, game_name, player_name):
        game_data = self.game_db.get(game_name)
        return game_data["players"].get(player_name) if game_data else None

    def get_channel_for_game(self, game_name):
        game_data = self.game_db.get(game_name)
        return game_data.get("channel", {}).get("id") if game_data else None
