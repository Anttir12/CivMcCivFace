import json

from discord.ext import commands

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
        await ctx.send("Here are currently tracked games:\n{}".format(json.dumps(self.bot_brains.game_db, indent=4,
                                                                                 sort_keys=True)))

    @commands.command()
    async def reset(self, ctx):
        """ Resets the game database. You probably don't want to use this """
        self.bot_brains.reset()
        await ctx.send("Game DB has been reset")


    async def send_error_message(self, ctx, error):
        await ctx.send(":poop: ERROR: {} :poop:".format(error))
