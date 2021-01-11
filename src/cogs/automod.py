from random import choice

import discord
from discord.ext import commands


from utils.docker import docker_log
from utils.dbManager import dbAutoMod
from utils.decorators import admin_only
from extras import constants
from extras.messages import MessageFormater


class AutoModerator(commands.Cog):
    '''
    AutoModerator Cogs
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Used mainly for logging and a greet for the guilds
        '''

        usr_num = 0
        for guild in self.client.guilds:
            usr_num += guild.member_count

        docker_log(
            f'Logged-in on {len(self.client.guilds)}, at the reach of {usr_num} users')

        await self.client.change_presence(activity=discord.Game(name='Truco com o Wanderley'))

    @commands.command(name='ajuda', aliases=['ajuda noix'])
    async def ajuda(self, ctx):
        '''
        Custom made help command (works in conjunctino to default help
        command).
        '''
        await ctx.channel.send(MessageFormater.ajuda())

    @commands.command(name='set_default_role', aliases=[
        'set_def_role', 'update_def_role', 'update_default_role'
    ])
    @commands.guild_only()
    @admin_only
    async def set_default_role(self, ctx, our_input):
        '''
        Sets the default role in the guild.
        '''

        role = discord.utils.get(ctx.guild.roles, name=our_input)

        mod = dbAutoMod(ctx.guild.id)
        mod.update_default_role(role.id)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} set default role as {role}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

    @commands.command(name='list_cursed_words')
    @commands.guild_only()
    async def list_cursed_words(self, ctx):
        '''
        Lists all cursed words from guild.
        '''

        mod = dbAutoMod(ctx.guild.id)

        for word in mod.cursed_words:
            await ctx.message.channel.send(word)

    @commands.command(name='set_cursed_word', aliases=[
        'set_cursed_words', 'add_cursed_words', 'add_cursed_word'
    ])
    @commands.guild_only()
    @admin_only
    async def set_cursed_words(self, ctx, our_input):
        '''
        Sets the cursed words. (curse-?)
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.add_cursed_words(words)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} added cursed word(s): {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

    @commands.command(name='uncurse_word', aliases=[
        'uncurse_words', 'remove_cursed_word', 'remove_cursed_words'
    ])
    @commands.guild_only()
    @admin_only
    async def remove_cursed_words(self, ctx, our_input):
        '''
        Unban words.
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.remove_cursed_words(words)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} removed cursed word(s): {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

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
        mod = dbAutoMod(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role)

        if def_role is not None:
            await member.add_roles(def_role)
            docker_log(
                f'AutoMod set autoRole for {member.id} @ {member.guild.id}')


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(AutoModerator(client))
