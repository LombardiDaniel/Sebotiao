from random import choice

# import discord
from discord.ext import commands


# from utils.docker import docker_log
from extras import constants
# from extras.messages import MessageFormater


class TiozaoZap(commands.Cog):
    '''
    AutoModerator Cogs
    '''

    def __init__(self, client):
        self.client = client

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


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(TiozaoZap(client))
