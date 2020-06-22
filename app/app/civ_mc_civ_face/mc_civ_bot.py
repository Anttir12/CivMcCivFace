import asyncio
import os

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, CommandNotFound
from dotenv import load_dotenv

from app.civ_mc_civ_face.cogs import Game
from app.civ_mc_civ_face.mc_civ_brains import McCivBrains

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


class CivMcCivFace(commands.Bot):

    def __init__(self, **options):
        super().__init__(**options)
        self.guild = None
        self.brains = McCivBrains(GAME_FILE)
        self.add_cog(Game(self.brains))

    async def on_ready(self):
        print(self.guilds)
        self.guild = discord.utils.find(lambda g: g.name == GUILD_NAME, self.guilds)
        print(f'{self.user} has connected to Discord to the following server: {self.guild.name} ({self.guild.id})!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == "Mika olis paras civ taktiikka?":
            await message.channel.send(":radioactive: Nuke everything :radioactive:")
        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, MissingRequiredArgument) or isinstance(exception, CommandNotFound):
            await ctx.send("Error: {}".format(exception))

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
        self.brains.save_game_database()

    def get_mention_for(self, discord_username):
        mention = discord_username
        if discord_username:
            discord_user = self.guild.get_member_named(discord_username)
            if discord_user:
                mention = discord_user.mention
        return mention

    def send_on_deck_message(self, game_name, player_name, channel):
        next_player = self.get_next_player(game_name, player_name)
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
