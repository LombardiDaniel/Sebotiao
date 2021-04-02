from random import choice
import os

# import discord
import discord
from discord.ext import commands

import youtube_dl

from extras import constants
from utils.auxiliary import YoutubeHelper
from utils.docker import DockerLogger
# from extras.messages import MessageFormater


class TiozaoZap(commands.Cog):
    '''
    TiozaoZap Cogs
    '''

    def __init__(self, client):
        self.client = client
        self.logger = DockerLogger(lvl=DockerLogger.INFO, prefix='TiozaoZap')

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

    @commands.command(name='audio_do_zap', aliases=['zap', 'audio', 'audio_zap'])
    @commands.guild_only()
    async def audio_do_zap(self, ctx):
        '''
        Plays a video of selection to channel.
        '''

        if not ctx.message.author.voice:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))
            return
        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

        guild_id = ctx.guild.id
        song_file_path = f"/tmp/songs/{guild_id}.mp3"
        song_tmp = os.path.isfile(song_file_path)
        try:
            if song_tmp:
                os.remove(song_file_path)
        except PermissionError:
            await ctx.send("Wait for the current playing music to end or use the 'stop' command")
            return

        voice_channel = ctx.message.author.voice.channel
        await voice_channel.connect()
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmp': '/tmp/songs/%(id)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # song_url = choice(YoutubeHelper.get_all_video_in_channel())
        song_url, song_id = 'https://www.youtube.com/watch?v=fvhbx0bTtrA', 'fvhbx0bTtrA'
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([song_url])
        for file in os.listdir("/tmp/songs/"):
            if file.name == f'{song_id}.mp3':
                os.rename(file, song_file_path)
        voice.play(discord.FFmpegPCMAudio(song_file_path))

        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.name} requested ZAP_AUDIO.')
        await ctx.message.channel.send('Se liga nesse audio...')


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(TiozaoZap(client))
