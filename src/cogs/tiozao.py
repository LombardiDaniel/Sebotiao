import logging
from secrets import choice
from asyncio import sleep

import discord
from discord.ext import tasks, commands

from extras import constants
from utils.audio import YoutubeHelper, YTDLSource
from utils import decorators


class TiozaoZap(commands.Cog):
    '''
    TiozaoZap Cogs
    '''

    def __init__(self, client):
        self.client = client

        self.logger = logging.getLogger('TiozaoZap')
        file_handler = logging.FileHandler('logs/tiaozap.log')
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

    async def _play_zap(self, ctx):
        '''
        Plays the zap audio.
        '''

        self.logger.debug('playing audio')

        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        video_url = choice(YoutubeHelper.get_urls_list())

        async with ctx.typing():
            player = await YTDLSource.from_url(video_url, loop=self.client.loop)
            voice_client.play(
                player,
                after=lambda e: print('Player error: %s' % e) if e else None
            )

        await ctx.message.channel.send(f'Se liga nesse audio... {player.title}')

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
            self.logger.debug('Xingo triggered')
            await message.channel.send(choice(constants.RESPOSTA_CHINGO))

    @commands.command(name='audio_do_zap', aliases=['zap', 'audio', 'audio_zap'])
    @decorators.in_voice_chat_only
    @commands.guild_only()
    async def audio_do_zap(self, ctx):
        '''
        Plays a video of selection 'audios do zap' to the users channel.
        '''

        voice_channel = ctx.message.author.voice.channel

        # Só tenta conectar se não está conectado, depois reseta
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if not voice_client:
            await voice_channel.connect()
            voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        await self._play_zap(ctx)

        self.logger.info('%d - %d requested ZAP_AUDIO', ctx.guild.id, ctx.message.author.id)

        # Disconnects after 5 seconds of audio ending
        while voice_client.is_playing():
            await sleep(5)

        await voice_client.disconnect()


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(TiozaoZap(client))
