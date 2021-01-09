import discord
from discord.ext import commands

def get_prefix(client, message):
    """A callable Prefix for our client. This could be edited to allow per server prefixes."""

    prefixes = ['tiao ', 'ei ', 'psiu ']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of
    # the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(client, message)
