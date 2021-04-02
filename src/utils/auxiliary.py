import urllib
import json

import discord

import os


class YoutubeHelper:

    @staticmethod
    def _get_channel_id(name):
        pass

    @staticmethod
    def get_all_video_in_channel(channel_id="UCriUl-dY4bFs2wvgPGCmepA", name=None):
        '''
        Uses the YouTube API to get the list of all videos from a channel.
        Args:
            - channel_id (str): Id of the channel.
            - name (str): OPTIONAL, name of the channel
        '''

        if name is not None:
            channel_id = YoutubeHelper._get_channel_id(name)

        api_key = os.getenv('YT_API_TOKEN')

        base_video_url = 'https://www.youtube.com/watch?v='
        base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

        first_url = base_search_url + \
            'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'\
            .format(api_key, channel_id)

        video_links = []
        url = first_url
        while True:
            inp = urllib.urlopen(url)
            resp = json.load(inp)

            for item in resp['items']:
                if item['id']['kind'] == "youtube#video":
                    video_links.append(base_video_url + item['id']['videoId'])

            try:
                next_page_token = resp['nextPageToken']
                url = first_url + '&pageToken={}'.format(next_page_token)
            except Exception:
                break

        return video_links
