import os
import discord

from discord.ext import commands
from sqlalchemy.ext.declarative import declarative_base

from utils.utls import get_prefix


Base = declarative_base()

cogs = [filename for filename in os.listdir(
    './cogs') if filename[-3::] == '.py']


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, intents=intents)


if __name__ == '__main__':
    for filename in cogs:
        client.load_extension(f'cogs.{filename[:-3]}')

    TOKEN = os.environ.get('BOT_TOKEN')
    client.run(TOKEN)
