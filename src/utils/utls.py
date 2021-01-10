from discord.ext import commands
from extras.constants import COMMAND_PREFIXES


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
