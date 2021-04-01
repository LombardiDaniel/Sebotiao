import re
from random import choice

import discord
from discord.ext import commands

from utils.docker import DockerLogger
from utils.dbManager import dbAutoMod, dbAutoRole
from utils.decorators import admin_only
from extras import constants
from extras.messages import MessageFormater


class AutoModerator(commands.Cog):
    '''
    AutoModerator Cogs
    '''

    def __init__(self, client):
        self.client = client
        self.logger = DockerLogger(lvl=DockerLogger.INFO, prefix='AutoModerator')

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Used mainly for logging and a greet for the guilds
        '''

        usr_num = 0
        for guild in self.client.guilds:
            usr_num += len(guild.members)

        self.logger.log(
            msg=f'Logged-in on {len(self.client.guilds)}, at the reach of {usr_num} users',
            lvl=self.logger.INFO)

        await self.client.change_presence(activity=discord.Game(name='Truco com o Wanderley'))

    @commands.command(name='ping', aliases=["ping server"])
    async def ping(self, ctx):
        '''
        Pings the bot server.
        '''
        await ctx.channel.send(f"Latency: {round(self.client.latency * 1000)}ms")

    @commands.command(name='ajuda', aliases=['ajuda noix'])
    async def ajuda(self, ctx, our_input=None):
        '''
        Custom made help command. Pulls configs from extras/commands.yml
        '''
        await ctx.channel.send(MessageFormater.ajuda(our_input))

    @commands.command(name='desenvolvimento', aliases=[
        'dev', 'development', 'git', 'info', 'status', '-v', '--version'])
    async def desenvolvimento(self, ctx):
        '''
        Replies with an embed about the current state of development.
        '''
        await ctx.channel.send(embed=MessageFormater.development())

    @commands.command(name='set_cursed_words', aliases=[
        'set_cursed_word', 'add_cursed_words', 'add_cursed_word',
    ])
    @commands.guild_only()
    @admin_only
    async def set_cursed_words(self, ctx, our_input):
        '''
        Sets the cursed words.
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.add_cursed_words(words)

        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.name} added cursed word(s): {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

    @commands.command(name='list_cursed_words', aliases=[
        'list_curse_words', 'ls_curse_words', 'ls_cursed_words'
    ])
    @commands.guild_only()
    async def list_cursed_words(self, ctx):
        '''
        Lists all cursed words from guild.
        '''

        mod = dbAutoMod(ctx.guild.id)

        for word in mod.cursed_words:
            await ctx.message.channel.send(word)

    @commands.command(name='remove_cursed_words', aliases=[
        'uncurse_words', 'remove_cursed_word', 'uncurse_word'
    ])
    @commands.guild_only()
    @admin_only
    async def remove_cursed_words(self, ctx, our_input):
        '''
        Uncurse words.
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.remove_cursed_words(words)

        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.name} removed cursed word(s): {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

    # AUTO:
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        '''
        When any member sends a message inside a guild text-channel.
        '''
        # Cancels the request if the sender was a bot.
        if message.author.bot:
            return

        # Cancels the request if the mwessage sent was a command.
        if any(word in message.content for word in constants.COMMAND_PREFIXES):
            return

        # cursed_words
        mod = dbAutoMod(message.guild.id)
        if any(word in message.content.lower().split() for word in mod.cursed_words):
            await message.channel.send(MessageFormater.cursed_words_msg(message.author.id))


    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        When a member joins.
        '''
        mod = dbAutoRole(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role_id)


        # TODO: add welcome msg for newcomer
        # mod.home_msg_id == 0 means that autorole is managed by home channel
        # if not mod.home_msg_id:
        #     if def_role is not None:
        #         await member.add_roles(def_role)
        #         self.logger.log(
        #             f'AutoMod set autoRole for {member.id} @ {member.guild.id}')


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(AutoModerator(client))
