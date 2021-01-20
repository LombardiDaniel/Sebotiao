import re
from random import choice

import discord
from discord.ext import commands

from utils.docker import docker_log
from utils.dbManager import dbAutoMod
from utils.decorators import admin_only
from extras import constants
from extras.messages import MessageFormater


class AutoRole(commands.Cog):
    '''
    AutoRole Cogs
    '''

    def __init__(self, client):
        self.client = client

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

        # For home message:
        if reaction.message.id != mod.home_msg_id:
            return

        if mod.home_msg_id:
            if def_role is not None and reaction.message.id == mod.home_msg_id:
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
    client.add_cog(AutoRole(client))
