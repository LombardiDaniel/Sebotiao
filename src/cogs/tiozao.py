from secrets import choice
from asyncio import sleep

import discord
from discord.ext import tasks, commands

from extras import constants
from utils.audio import YoutubeHelper, YTDLSource
from utils.docker import DockerLogger
from utils import decorators


class TiozaoZap(commands.Cog):
    '''
    TiozaoZap Cogs
    '''

    def __init__(self, client):
        self.client = client
        self.logger = DockerLogger(lvl=DockerLogger.INFO, prefix='TiozaoZap')

    async def _play_zap(self, ctx):
        '''
        Plays the zap audio.
        '''

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
        if any(word in message.content.lower() for word in constants.BOZO_XINGO_TRIGGERS):
            choice(constants.RESPOSTA_XINGO)
            await message.channel.send(choice(constants.RESPOSTA_XINGO))

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

        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.id} requested ZAP_AUDIO',
            lvl=self.logger.INFO
        )

        # Disconnects after 5 seconds of audio ending
        while voice_client.is_playing():
            await sleep(5)

        await voice_client.disconnect()


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(TiozaoZap(client))
