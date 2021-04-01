import os
import discord

from discord.ext import commands
from sqlalchemy.ext.declarative import declarative_base

from utils.utls import get_prefix
from utils.docker import DockerLogger


logger = DockerLogger(prefix='main', lvl=DockerLogger.INFO)

logger.log('Initializing bot...', lvl=DockerLogger.INFO)

Base = declarative_base()

cogs = [filename for filename in os.listdir(
    './cogs') if filename[-3::] == '.py']


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=get_prefix, intents=intents)

client.remove_command('help')


if __name__ == '__main__':

    logger.log('Initializing bot...', lvl=DockerLogger.INFO)

    for filename in cogs:
        client.load_extension(f'cogs.{filename[:-3]}')

    TOKEN = os.environ.get('BOT_TOKEN')

    if not TOKEN:
        raise NameError("Missing env variable: BOT_TOKEN")

    client.run(TOKEN)

    logger.log('Initialization Complete.', lvl=DockerLogger.INFO)
