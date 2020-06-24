import asyncio
import logging

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, CommandNotFound

from civ_mc_civ_face.cogs import Game
from civ_mc_civ_face.mc_civ_brains import McCivBrains


logger = logging.getLogger("bot")


class CivMcCivFace(commands.Bot):

    def __init__(self, game_file, guild_name, global_settings, **options):
        logger.info("Initialising bot!")

        super(CivMcCivFace, self).__init__(**options)
        self.guild_name = guild_name
        self.gloval_settings = global_settings  # Not used yet
        self.guild = None
        self.brains = McCivBrains(game_file)
        self.add_cog(Game(self.brains))
        logger.info("Bot initialised guild_name: {}".format(guild_name))

    def run(self, *args, **kwargs):
        logger.info("Running bot!")
        super(CivMcCivFace, self).run(*args, **kwargs)

    async def on_ready(self):
        logger.info("Bot ready!")
        logger.info(self.guilds)
        self.guild = discord.utils.find(lambda g: g.name == self.guild_name, self.guilds)
        logger.info(f'{self.user} has connected to Discord to the following server: {self.guild.name} ({self.guild.id})!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == "Mikä olis paras civ taktiikka?":
            await message.channel.send(":radioactive: Nuke everything :radioactive:")
        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, MissingRequiredArgument) or isinstance(exception, CommandNotFound):
            await ctx.send("Error: {}".format(exception))

    def handle_webhook_message(self, values: dict):
        game_name = values["value1"]
        in_game_name = values["value2"]
        turn_number = values["value3"]

        game_data = self.brains.game_db.get(game_name)
        player_data = game_data["players"].get(in_game_name)

        channel_id = self.brains.get_channel_for_game(game_name)
        channel = self.get_channel(channel_id)
        discord_username = self.brains.get_discord_username(game_name, in_game_name)
        mention = discord_username
        if player_data is not None and player_data.get("mention"):
            mention = self.get_mention_for(discord_username)
        if not mention:
            mention = in_game_name
        asyncio.run_coroutine_threadsafe(channel.send("{} your turn (turn {}, {})".format(mention, turn_number, game_name)), self.loop)
        self.send_on_deck_message(game_name, in_game_name, channel)
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
        if next_player:
            mention = self.get_mention_for(next_player)
            asyncio.run_coroutine_threadsafe(channel.send("{} you're on deck.".format(mention)), self.loop)

    def get_next_player(self, game_name, player_name):
        players = self.brains.game_db.get(game_name).get("player_turn_order")
        if player_name not in players:
            players.append(player_name)
            self.brains.save_game_database()
            return
        next_player = self.get_player_from_list(player_name, players)
        game_data = self.brains.game_db.get(game_name)
        player_data = game_data["players"].get(next_player)
        if player_data.get("early_mention"):
            return self.brains.get_discord_username(game_name, next_player)

    def get_player_from_list(self, player_name, players):
        index = players.index(player_name)
        if index < len(players) - 1:
            return players[index+1]
        else:
            return players[0]
