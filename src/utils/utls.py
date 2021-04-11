import random

from discord.ext import commands

from extras import MusicErros as errors

from extras.constants import COMMAND_PREFIXES
from extras.errors import MusicErros as errors


def get_prefix(client, message):
    """
    A callable Prefix for our client. This could be edited to allow per server prefixes.
    """

    prefixes = COMMAND_PREFIXES

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of
    # the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(client, message)


class Queue:
    '''
    Queue used in Music Cog.
    Attributes:
        - _queue (lst): Queue itself
        - is_empty (bool): True if queue is empty
        - current_track (str): Url of current track
        - upcoming (lst): List of all upcoming tracks
        - history (lst): List of all past tracks
    '''
    def __init__(self):
        self._queue = []
        self.position = 0

    @property
    def is_empty(self):
        '''True if queue is empty.'''
        return not self._queue

    @property
    def current_track(self):
        '''Returns the current track.'''
        if not self._queue:
            raise errors.QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

        return None

    @property
    def upcoming(self):
        '''Returns all upcoming items in a list.'''
        if self.is_empty:
            raise errors.QueueIsEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self):
        '''Return all past items in a list.'''
        if self.is_empty:
            raise errors.QueueIsEmpty

        return self._queue[:self.position]

    def __len__(self):
        return len(self._queue)

    def add(self, *args):
        '''Adds new items to the end of the queue.'''
        self._queue.extend(args)

    def get_next_track(self):
        '''Returns the next track. None if already done.'''
        if self.is_empty:
            raise errors.QueueIsEmpty

        self.position += 1

        if self.position < 0 or self.position > len(self._queue) - 1:
            return None

        return self._queue[self.position]

    def shuffle(self):
        '''Shuffles the current reminder queue.'''
        if self.is_empty:
            raise errors.QueueIsEmpty

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def empty(self):
        '''
        Clears the Queue. (does NOT delete it, must be managed by garbege collector)
        '''
        self._queue.clear()
        self.position = 0
