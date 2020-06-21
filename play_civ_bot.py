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

    async def on_ready(self):
        print(self.guilds)
        guild = discord.utils.find(lambda g: g.name == GUILD_NAME, self.guilds)
        print(f'{self.user} has connected to Discord to the following server: {guild.name} ({guild.id})!')
        self.guild = guild

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

    async def create_game(self, message):
        try:
            game_name = message.content.split(":", 1)[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}create_game:<game_name>".format(PREFIX))
            return
        if self.get_game_data(game_name):
            await message.channel.send(":poop:ERROR: game \"{}\" already exists".format(game_name))
            return
        else:
            game_data = {"turn": 0, "players": {}, "channel": {"id": message.channel.id, "name": message.channel.name}}
            self.save_game_data(game_name, game_data)

        await message.channel.send("OK, I created a new game called {}".format(game_name))

    async def delete_game(self, message):
        try:
            game_name = message.content.split(":", 1)[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}delete_game:<game_name>".format(PREFIX))
            return
        game_db = self.get_game_database()
        if game_name not in game_db:
            await message.channel.send(":poop:ERROR: game \"{}\" does not exist".format(game_name))
            return
        del game_db[game_name]
        self.save_game_database(game_db)
        await message.channel.send("Ok, I deleted the game \"{}\"".format(game_name))

    async def list_games(self, message):
        game_db = self.get_game_database()
        await message.channel.send("Here are currently tracked games:\n{}".format(json.dumps(game_db, indent=4, sort_keys=True)))

    async def add_player_to_game(self, message):
        try:
            parameters = shlex.split(message.content.split(":", 1)[1])
            game_name = parameters[0]
            ingame_name = parameters[1]
            discord_name = parameters[2]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}add_player:<game_name> <ingame_name> <discord_name>".format(PREFIX))
            return
        game_data = self.get_game_data(game_name)
        if not game_data:
            await message.channel.send(":poop:ERROR: Could not find game \"{}\"".format(game_name))
            return
        game_data["players"][ingame_name] = discord_name
        self.save_game_data(game_name, game_data)
        await message.channel.send("{} - {} added to {}".format(ingame_name, discord_name, game_name))

    async def remove_player_from_game(self, message):
        try:
            parameters = shlex.split(message.content.split(":", 1)[1])
            game_name = parameters[0]
            ingame_name = parameters[1]
        except IndexError:
            await message.channel.send(":poop:ERROR: try this: {}remove_player:<game_name> <ingame_name>".format(PREFIX))
            return
        game_data = self.get_game_data(game_name)
        if not game_data:
            await message.channel.send(":poop:ERROR: Could not find game \"{}\"".format(game_name))
            return
        if ingame_name in game_data["players"]:
            del game_data["players"][ingame_name]
            self.save_game_data(game_name, game_data)
            await message.channel.send("{} removed from {}".format(ingame_name, game_name))
        else:
            await message.channel.send(":poop:ERROR: Player {} not in game \"{}\"".format(ingame_name, game_name))

    async def reset(self, message):
        self.save_game_database({})
        await message.channel.send("Game DB has been reset")

    def handle_webhook_message(self, values: dict):
        game_name = values["value1"]
        player_name = values["value2"]
        turn_number = values["value3"]

        game_data = self.get_game_data(game_name)
        if not game_data:
            return
        discord_username = game_data["players"].get(player_name)
        mention = None
        if discord_username:
            discord_user = self.guild.get_member_named(discord_username)
            if discord_user:
                mention = discord_user.mention
        if not mention:
            mention = player_name
        channel = self.get_channel(game_data["channel"]["id"])
        asyncio.run_coroutine_threadsafe(channel.send("{} Your turn (turn {})".format(mention, turn_number)), self.loop)

    def get_game_database(self):
        game_db = dict()
        with open(GAME_FILE, "r") as file:
            game_db = json.loads(file.read())
        return game_db

    def save_game_database(self, game_db: dict):
        with open(GAME_FILE, "w") as file:
            file.write(json.dumps(game_db))

    def save_game_data(self, game_name: str, data: dict):
        game_db = self.get_game_database()
        game_db[game_name] = data
        self.save_game_database(game_db)

    def get_game_data(self, game_name: str):
        game_db = self.get_game_database()
        return game_db.get(game_name)
