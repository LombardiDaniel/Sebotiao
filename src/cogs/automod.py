import re
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
            usr_num += len(guild.members)

        docker_log(
            f'Logged-in on {len(self.client.guilds)}, at the reach of {usr_num} users')

        await self.client.change_presence(activity=discord.Game(name='Truco com o Wanderley'))

    @commands.command(name='ajuda', aliases=['ajuda noix'])
    async def ajuda(self, ctx, our_input=None):
        '''
        Custom made help command (works in conjunctino to default help
        command).
        '''
        await ctx.channel.send(MessageFormater.ajuda(our_input))

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

    @commands.command(name='set_welcome_channel', aliases=[
        'set_home_channel', 'set_welcome_msg', 'set_home_msg'
    ])
    @commands.guild_only()
    @admin_only
    async def set_welcome_channel(self, ctx, our_input):
        '''
        Sets the channel where users will be taken to upon log in, and must authenticate.
        Args:
            - our_input (str): Input de embed_title;;embed_description
        '''

        mod = dbAutoMod(ctx.guild.id)
        def_role = discord.utils.get(ctx.guild.roles, id=mod.default_role_id)

        match = re.match(r'(?P<title>.*);(?P<desc>.*)', our_input)
        embed_title = match.group('title')
        embed_desc = match.group('desc')

        home_channel = discord.utils.get(ctx.guild.channels, id=ctx.channel.id)

        if home_channel is not None and def_role is not None:
            await ctx.message.channel.send(
                embed=MessageFormater.home_channel_message(embed_title, embed_desc))
            mod.set_welcome_channel(home_msg_id=ctx.message.channel.last_message_id)
            await ctx.author.send(
                f"Configure as permissões para pessoas sem cargos terem acesso APENAS ao canal `{home_channel.name}`.")

        else:
            await ctx.message.channel.send("Sem default role")

    @commands.command(name='remove_welcome_channel', aliases=[
        'remove_home_channel', 'remove_welcome_msg', 'remove_home_msg', 'unset_home_channel'
    ])
    @commands.guild_only()
    @admin_only
    async def remove_welcome_channel(self, ctx):
        '''
        Sets the channel where users will be taken to upon log in, and must authenticate.
        Args:
            None.
        '''

        mod = dbAutoMod(ctx.guild.id)
        mod.remove_welcome_channel()

        if not mod.home_msg_id:
            await ctx.message.channel.send((choice(constants.POSITIVE_RESPONSES)))
            await ctx.author.send("Lembre-se de resetar as permissões dos canais.")


    @commands.command(name='set_no_role_as_default', aliases=[
        'set_no_role_as_def', 'set_norole_as_def', 'set_norole_as_default'
    ])
    @admin_only
    async def set_no_role_as_default(self, ctx):
        '''
        Sets all members without a role to default role.
        '''

        mod = dbAutoMod(ctx.guild.id)
        def_role = discord.utils.get(ctx.guild.roles, id=mod.default_role_id)

        if def_role is not None:
            for member in ctx.guild.members:
                if len(member.roles) == 1:
                    await member.add_roles(def_role)
                    docker_log(
                        f'AutoMod set Role for {member.id} @ {member.guild.id}')

            await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

        else:
            await ctx.message.channel.send("Sem default role")

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

        docker_log(
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

        docker_log(
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
    @commands.guild_only()
    async def on_reaction_add(self, reaction, member):
        '''
        Adds members to def_role when they react to home_msg.
        '''

        if member.bot:
            return

        mod = dbAutoMod(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role_id)

        if reaction.message.id != mod.home_msg_id:
            return

        if mod.home_msg_id:
            if def_role is not None:
                await member.add_roles(def_role)
                docker_log(
                    f'AutoMod set autoRole for {member.id} @ {member.guild.id}')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        When a member joins.
        '''
        mod = dbAutoMod(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role_id)

        # mod.home_msg_id == 0 means that autorole is managed by home channel
        if not mod.home_msg_id:
            if def_role is not None:
                await member.add_roles(def_role)
                docker_log(
                    f'AutoMod set autoRole for {member.id} @ {member.guild.id}')


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(AutoModerator(client))
