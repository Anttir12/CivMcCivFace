import json

from discord.ext import commands
from discord.ext.commands import Context

from civ_mc_civ_face.mc_civ_brains import McCivBrains, McCivBrainException


class Game(commands.Cog):

    def __init__(self, brains: McCivBrains):
        self.bot_brains = brains

    @commands.command()
    async def create_game(self, ctx, game_name):
        """ Creates new game to track """
        try:
            self.bot_brains.create_game(game_name, ctx.channel.id, ctx.channel.name)
            await ctx.send("OK, I created a new game called {}".format(game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def delete_game(self, ctx, game_name):
        """ Delete game. Bot can no longer track this """
        try:
            self.bot_brains.delete_game(game_name)
            await ctx.send("Ok, I deleted the game \"{}\"".format(game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def add_player(self, ctx, game_name, ingame_name, discord_name):
        """ Adds player to the game. This allows bot to add mention to the next turn messages for this user """
        try:
            self.bot_brains.add_player_to_game(game_name, ingame_name, discord_name)
            await ctx.send("{} - {} added to {}".format(ingame_name, discord_name, game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def add_me(self, ctx, game_name, ingame_name):
        """ Adds player to the game. This allows bot to add mention to the next turn messages for this user """
        try:
            author = str(ctx.author)
            self.bot_brains.add_player_to_game(game_name, ingame_name, author)
            await ctx.send("{} - {} added to {}".format(ingame_name, author, game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def toggle_mention_me(self, ctx, game_name):
        """ Disables/enables bot mentioning you on messages """
        try:
            author = str(ctx.author)
            mention = self.bot_brains.toggle_mention(game_name, author)
            await ctx.send("Mention {} in game {}: {}".format(author, game_name, mention))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def toggle_early_mention(self, ctx, game_name):
        """ Disables/enables bot early mentioning you: 'X you're on deck' """
        try:
            author = str(ctx.author)
            mention = self.bot_brains.toggle_early_mention(game_name, author)
            await ctx.send("Early mention {} in game {}: {}".format(author, game_name, mention))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def remove_player(self, ctx, game_name, ingame_name):
        """ Remove player from the game. This user no longer gets mentioned by the bot """
        try:
            self.bot_brains.remove_player_from_game(game_name, ingame_name)
            await ctx.send("{} removed from {}".format(ingame_name, game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def list_games(self, ctx):
        """ Bot prints entire game db in json format """
        game_info_list = self.bot_brains.get_every_game_info()
        for game_info in game_info_list:
            await ctx.send("```\n{}```".format(game_info))

    @commands.command()
    async def whose_turn(self, ctx, game_name, ping=False):
        try:
            player, discord_name = self.bot_brains.whose_turn(game_name)
            if discord_name and ping:
                mention = await self.get_mention_from_context(ctx, player)
                player = mention if mention else player
            await ctx.send("{}! It is your turn in the game \"{}\"".format(player, game_name))
        except McCivBrainException as e:
            await self.send_error_message(ctx, e)

    @commands.command()
    async def reset(self, ctx):
        """ Resets the game database. You probably don't want to use this """
        self.bot_brains.reset()
        await ctx.send("Game DB has been reset")

    async def cog_command_error(self, ctx, error):
        await ctx.send(":poop: unhandled error: {}".format(error))

    async def send_error_message(self, ctx, error):
        await ctx.send(":poop: ERROR: {} :poop:".format(error))

    async def get_mention_from_context(self, ctx: Context, discord_name: str):
        return next((user.mention for user in ctx.channel.members if str(user).startswith(discord_name)), None)
