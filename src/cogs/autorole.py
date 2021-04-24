import re
from secrets import choice

import discord
from discord.ext import commands

from utils.docker import DockerLogger
from utils.dbManager import dbAutoRole
from utils.decorators import admin_only
from extras import constants
from extras.messages import MessageFormater


class AutoRole(commands.Cog):
    '''
    AutoRole Cogs
    '''

    def __init__(self, client):
        self.client = client
        self.logger = DockerLogger(lvl=DockerLogger.INFO, prefix='AutoRole')

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

        mod = dbAutoRole(ctx.guild.id)
        mod.update_default_role(role.id)

        mod.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.id} set default role as {role}',
            lvl=self.logger.INFO)
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

        mod = dbAutoRole(ctx.guild.id)
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

        mod = dbAutoRole(ctx.guild.id)
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

        mod = dbAutoRole(ctx.guild.id)

        if mod is not None and (default_role_id_buffer := mod.default_role_id) is not None:
            def_role = discord.utils.get(ctx.guild.roles, id=default_role_id_buffer)

            for member in ctx.guild.members:
                if len(member.roles) == 1:
                    await member.add_roles(def_role)
                    mod.logger.log(
                        f'AutoMod set Role for {member.id} @ {member.guild.id}')

            await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

        else:
            await ctx.message.channel.send("Sem default role")

    @commands.command(name='set_react_role_message', aliases=[])
    @admin_only
    async def set_react_role_message(self, ctx, our_input):
        '''
        Sets a new react_role_msg
        '''

        mod = dbAutoRole(ctx.guild.id)
        try:
            mod.set_react_role_message(int(our_input))
            await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))
        except ValueError:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES) +
                                           "Lembre de enviar o `id` da mensagem.")

    @commands.command(name='add_react_role', aliases=[])
    @admin_only
    async def add_react_role(self, ctx, our_input):
        '''
        Sets a new react_role combo.
        '''

        mod = dbAutoRole(ctx.guild.id)

        # If there is no msg set
        if not mod.react_role_msg_id:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES) +
                                           "Você precisa setar uma mensagem antes. " +
                                           "Utilize `tiao set_react_role_message ID_DA_MENSAGEM\n`")
            return

        # Gets Emoji obj
        emoji_str = our_input.split(';')[0]
        # USE API TO GET EMOJI UNICODE ID
        for emoji in self.client.emojis:
            if emoji.name == emoji_str:
                emoji_obj = emoji
                break

        # Gets Role obj
        role_name = our_input.split(';')[1]
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        # Searches for message to add react
        msg_id = mod.react_role_msg_id
        for channel in ctx.guild.text_channels:
            try:
                react_role_msg_obj = await channel.fetch_message(id=msg_id)
                break
            except:
                pass


        # If message exists, adds react and saves to db, else sends waning
        if react_role_msg_obj:
            await react_role_msg_obj.add_reaction(emoji_obj)

            # Creates react_role_dict and saves to db
            react_role_dict = {str(emoji_obj.id): str(role.id)}
            mod.add_react_role(react_role_dict)
        else:
            await ctx.message.channel.send(
                "Não consegui encontrar a mensagem, envie-a novamente, e não envie outras mensagens no canal." +
                "\nTente novamente.")

    # AUTO:
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_add(self, reaction, member):
        '''
        Adds members to def_role when they react to home_msg.
        '''

        if member.bot:
            return

        mod = dbAutoRole(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role_id)

        # For the home_msg
        if mod is not None:
            if mod.home_msg_id:
                if def_role is not None and reaction.message.id == mod.home_msg_id:
                    await member.add_roles(def_role)
                    mod.logger.log(
                        f'AutoMod set autoRole for {member.id} @ {member.guild.id}')

            if mod.react_role_msg_id == reaction.message.id:
                if reaction.emoji[-1] in mod.react_role_dict.keys():
                    role = discord.utils.get(member.guild.roles,
                                             id=mod.react_role_dict[f"{reaction.emoji[-1]}"])
                    await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        When a member joins.
        '''
        mod = dbAutoRole(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role_id)

        # mod.home_msg_id == 0 means that autorole is managed by home channel
        if not mod.home_msg_id:
            if def_role is not None:
                await member.add_roles(def_role)
                mod.logger.log(
                    f'AutoMod set autoRole for {member.id} @ {member.guild.id}')


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(AutoRole(client))
