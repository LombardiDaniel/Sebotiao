import re
from random import choice

import discord
from discord.ext import commands


from utils.docker import docker_log
from utils.dbManager import dbAutoMod, dbStreamManager
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

        # Sends greet to general channel
        msg_sent = False
        for channel in self.client.get_all_channels():
            if 'general' in channel.name:
                general_channel = self.client.get_channel(channel.id)
                await general_channel.send(f'Salve salve, meu lindo povo do {channel.guild.name}.')
                msg_sent = True
                break

        if not msg_sent:
            first_channel = self.client.get_all_channels()[0]
            await first_channel.send(f'Salve salve, meu lindo povo do {first_channel.guild.name}.')
            msg_sent = True

        # Tries to reach the first text_channel of the guild that the bot has send_messages perms
        if not msg_sent:
            bot_user = self.client.get_user(self.client.user.id)
            for channel in self.client.get_all_channels():
                channel_perms = channel.permissions_for(bot_user)
                if channel_perms.send_messages:
                    channel = self.client.get_channel(channel.id)
                    await channel.send(f'Salve salve, meu lindo povo do {channel.guild.name}.')
                    msg_sent = True
                    break

        await self.client.change_presence(activity=discord.Game(name='Truco com o Wanderley'))



    @commands.command(name='ajuda', aliases=['ajuda noix'])
    async def ajuda(self, ctx, *args, **kwargs):
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
    async def set_default_role(self, ctx, our_input, *args, **kwargs):
        '''
        Sets the default role in the guild.
        '''

        role = discord.utils.get(ctx.guild.roles, name=our_input)

        mod = dbAutoMod(ctx.guild.id)
        mod.update_default_role(role.id)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} set default role as {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))



    @commands.command(name='list_banned_words')
    @commands.guild_only()
    async def list_banned_words(self, ctx):
        '''
        Lists all banned words from guild.
        '''

        mod = dbAutoMod(ctx.guild.id)

        for word in mod.banned_words:
            await ctx.message.channel.send(word)



    @commands.command(name='set_banned_word', aliases=[
        'set_banned_words', 'add_banned_words', 'add_banned_word'
    ])
    @commands.guild_only()
    @admin_only
    async def set_banned_words(self, ctx, our_input, *args, **kwargs):
        '''
        Sets the banned words. (curse-?)
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.add_banned_words(words)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} added banned word(s): {our_input}')
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))


    @commands.command(name='unban_word', aliases=[
        'unban_words', 'remove_banned_word', 'remove_banned_words'
    ])
    @commands.guild_only()
    @admin_only
    async def remove_banned_words(self, ctx, our_input, *args, **kwargs):
        '''
        Unban words.
        '''

        words = our_input.split(',')

        mod = dbAutoMod(ctx.guild.id)
        mod.remove_banned_words(words)

        docker_log(
            f'{ctx.guild.id} - {ctx.message.author.name} removed banned word(s): {our_input}')
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

        # bozo xingo
        if any(word in message.content.lower() for word in constants.BOZO_CHINGO_TRIGGERS):
            choice(constants.RESPOSTA_CHINGO)
            await message.channel.send(choice(constants.RESPOSTA_CHINGO))

        # banned_words
        mod = dbAutoMod(message.guild.id)
        if any(word in message.content.lower().split() for word in mod.banned_words):
            await message.channel.send(MessageFormater.banned_words_msg(message.author.id))



    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        When a member joins.
        '''
        print('entrou')
        mod = dbAutoMod(member.guild.id)
        def_role = discord.utils.get(member.guild.roles, id=mod.default_role)

        if def_role is not None:
            await member.add_roles(def_role)
            docker_log(f'AutoMod set autoRole for {member.id} @ {member.guild.id}')



def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(AutoModerator(client))
