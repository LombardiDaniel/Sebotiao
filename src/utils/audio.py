import os
import asyncio
from datetime import datetime

import requests

import discord
import youtube_dl

from utils.docker import DockerLogger
from utils.dbManager import dbBotConfig

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    '''Needed for playback'''
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        '''Plays audio from video URL.'''
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class YoutubeHelper:
    '''Utils for youtube related functionality.'''

    @staticmethod
    def filter_videos_input_from_api_call(our_input):
        '''
        Filters out each video from youtube playlist.
        Args:
            - our_input (str) : url of video/playlist.
        Returns:
            - lst_urls (lst) : list of videos included in url passed as input. Can be:
                - empty :               invalid link
                - single element:       single video url
                - multiple elements:    urls of videos in playlist
        '''

        if our_input[0:24] != 'https://www.youtube.com/':
            return []

        lst_urls = YoutubeHelper._playlist_to_list(our_input) if \
            '&list=' in our_input else [our_input]

        return lst_urls




    @staticmethod
    def get_urls_list():
        '''
        Controls the buffer to reduce number of youtubeAPI calls (max 1 per day).
        Uses the database to save content of day, if day expires, makes api call
        to update list.

        Args:
            - None.
        Returns:
            - url_list (list of str): List of URLs.
        '''

        logger = DockerLogger(prefix='BufferYouTubeAPI', lvl=DockerLogger.INFO)

        now = datetime.now()
        date_now = now.strftime("%Y-%m-%d")

        bot_confs = dbBotConfig()
        contents = bot_confs.yt_yaml

        if contents is None:
            logger.log(lvl=logger.INFO, msg="Content of buffer is None, making API Call")
            videos_lst = YoutubeHelper._make_api_call()
            contents = {date_now:videos_lst}
            bot_confs.update_yt_yaml(contents)
            return videos_lst

        date_time_obj = None

        # Only has 1 key, but we use for anyway
        for key in contents.keys():
            date_time_obj = datetime.strptime(key, '%Y-%m-%d')

        videos_lst = list(contents.values())[0]

        if (now - date_time_obj).days > 1:
            logger.log(lvl=logger.INFO, msg="Buffer Expired, making API Call")

            new_videos_lst = YoutubeHelper._make_api_call()
            new_videos_lst = list(set(videos_lst + new_videos_lst))

            new_contents = {date_now:new_videos_lst}
            bot_confs.update_yt_yaml(new_contents)

            return new_videos_lst

        logger.log(lvl=logger.INFO, msg="Using buffer")
        return videos_lst

    @staticmethod
    def _get_channel_id(name):
        pass

    @staticmethod
    def _playlist_to_list(url):
        '''
        '''

        api_key = os.getenv('YT_API_KEY')

        playlist_id = url.split("&list=")[-1]
        count = 20

        videos_url = ""
        videos_url += f"https://www.googleapis.com/youtube/v3/playlistItems?key={api_key}"
        videos_url += f"&playlistId={playlist_id}&part=contentDetails&maxResults={count}"

        request = requests.get(videos_url).json()

        videos_ids = []
        for item in request['items']:
            videos_ids.append(item['contentDetails']['videoId'])

        videos_urls = [f"https://www.youtube.com/watch?v={id}" for id in videos_ids]

        return videos_urls


    @staticmethod
    def _make_api_call(channel_id="UCriUl-dY4bFs2wvgPGCmepA", name=None, count=20):
        '''
        Uses the YouTube API to get the last videos from a channel.
        Args:
            - channel_id (str): Id of the channel.
            - name (str): OPTIONAL, name of the channel.
            - count (int): OPTIONAL, ammount of videos to get.
        Returns:
            - videos_urls (list of str): list of videos urls.
        '''

        if name is not None:
            channel_id = YoutubeHelper._get_channel_id(name)

        api_key = os.getenv('YT_API_KEY')

        videos_url = ""
        videos_url += f"https://www.googleapis.com/youtube/v3/search?key={api_key}"
        videos_url += f"&channelId={channel_id}&part=id&order=date&maxResults={count}"

        request = requests.get(videos_url).json()

        videos_ids = []
        for item in request['items']:
            videos_ids.append(item['id']['videoId'])

        videos_urls = [f"https://www.youtube.com/watch?v={id}" for id in videos_ids]

        return videos_urls
