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

    Attributes:
        - return_chats (dict of chat_ids) : used to mark the chat used by the bot
            to send queue updates.
            {
                'server_id0': 'chat_id0',
                'server_id1': 'chat_id1',
            }
        - queues (dict of lists) : queue the bot will use recursivelly to play songs.
            {
                'server_id0': ['url0', 'url1', ...],
            }
    '''

    def __init__(self, client):
        self.client = client
        self.logger = DockerLogger(lvl=DockerLogger.INFO, prefix='TiozaoZap')
        self.return_chats = {}
        self.queues = {}
        # Tasks:
        self.check_next_in_queue.start()
        self.exit_dangling_voice_chats.start()


    @tasks.loop(seconds=60.0)
    async def exit_dangling_voice_chats(self):
        '''
        Task to exit dangling voice chats.
        '''
        for guild_id, queue in self.queues.items():
            guild_obj = await self.client.fetch_guild(guild_id)
            voice_client = discord.utils.get(self.client.voice_clients, guild=guild_obj)
            if voice_client is not None and not voice_client.is_playing():
                if queue:
                    await self._play_song_from_queue(guild_id)
                else:
                    # Garbage collection
                    await voice_client.disconnect()
                    del self.return_chats[guild_id]
                    del self.queues[guild_id]

    @tasks.loop(seconds=0.1)
    async def check_next_in_queue(self):
        '''
        Task to check the next song in queue.
        '''
        for guild_id, queue in self.queues.items():
            guild_obj = await self.client.fetch_guild(guild_id)
            voice_client = discord.utils.get(self.client.voice_clients, guild=guild_obj)
            if voice_client is not None and not voice_client.is_playing():
                if queue:
                    await self._play_song_from_queue(guild_id)

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

    async def _play_song_from_queue(self, str_guild_id):
        '''
        Plays the song from queue. IMPORTANT: the bot ONLY plays from queue, when
        a new song is requested by a user, it is simply added to the queue and in
        the 'play' command, this method is called.
        '''

        guild_obj = await self.client.fetch_guild(str_guild_id)

        voice_client = discord.utils.get(self.client.voice_clients, guild=guild_obj)

        text_channel = self.return_chats[str_guild_id]

        video_url = self.queues[str_guild_id].pop(0)
        async with text_channel.typing():
            player = await YTDLSource.from_url(video_url, loop=self.client.loop)
            voice_client.play(
                player,
                after=lambda e: print('Player error: %s' % e) if e else None
            )

            await text_channel.send(f'> Tocando: `{player.title}`')


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

    @commands.command(name='play', aliases=['toca', 'musica'])
    @decorators.in_voice_chat_only
    @commands.guild_only()
    async def play(self, ctx, our_input=None):
        '''
        Plays a video audio to channel.
        '''

        # Filters out the input into individual videos and adds to guild queue
        lst_url = YoutubeHelper.filter_videos_input_from_api_call(our_input)

        if not lst_url:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))
            await ctx.message.channel.send("Só links do.youtube fas o favor ...")
            return

        str_guild_id = str(ctx.guild.id)

        self.return_chats[str_guild_id] = ctx.message.channel

        if str_guild_id not in self.queues.keys():
            self.queues[str_guild_id] = lst_url
        else:
            self.queues[str_guild_id] += lst_url

        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))


        # Connects to channel if not already connected
        voice_channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if not voice_client:
            await voice_channel.connect()
            voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice_client.is_playing():
            await self._play_song_from_queue(str_guild_id)
        else:
            await ctx.message.channel.send('> Adicionado à queue.')

        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.id} requested SONG',
            lvl=self.logger.INFO
        )

    @commands.command(name='limpa_fila', aliases=['limpa', 'clear_queue', 'clear'])
    @decorators.in_voice_chat_only
    @commands.guild_only()
    async def limpa_fila(self, ctx):
        '''
        Clears the queue, does not delete it.
        '''

        str_guild_id = str(ctx.guild.id)

        self.queues[str_guild_id] = []

        await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))

        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice_client.is_playing():
            voice_client.stop()

    @commands.command(name='sai', aliases=['exit', 'stop', 'para', 'encerra'])
    @decorators.in_voice_chat_only
    @commands.guild_only()
    async def encerra(self, ctx):
        '''
        Exits the voice channel and deletes queue.
        '''

        str_guild_id = str(ctx.guild.id)

        del self.queues[str_guild_id]

        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice_client.is_playing():
            voice_client.stop()
            await voice_client.disconnect()
            await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))
            del self.return_chats[str_guild_id]

        else:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))


    @commands.command(name='proximo', aliases=['pula', 'skip', 'next'])
    @decorators.in_voice_chat_only
    @commands.guild_only()
    async def proximo(self, ctx):
        '''
        Skips the video that is currently playing in server.
        '''

        str_guild_id = str(ctx.guild.id)

        try:
            if str_guild_id in self.queues.keys():
                if self.queues[str_guild_id]:
                    await ctx.message.channel.send(choice(constants.POSITIVE_RESPONSES))
                else:
                    await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))
                    await ctx.message.channel.send("já tá no último irmão...")
                    return

        except KeyError:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))


        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice_client.is_playing():
            voice_client.stop()
            # if the queue is not empty, goes to next track
            if len(self.queues[str_guild_id]) > 0:
                await self._play_song_from_queue(str_guild_id)


        self.logger.log(
            f'{ctx.guild.id} - {ctx.message.author.id} skipped SONG',
            lvl=self.logger.INFO
        )


def setup(client):
    '''
    Cog setup.
    '''
    client.add_cog(TiozaoZap(client))
