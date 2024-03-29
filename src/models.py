from sqlalchemy import Column, Integer, String, Text
from main import Base


class AdminOptions(Base):
    '''
    Admin Model Table for storage of automod settings.

    Rows:
        - guild_id (int): ID of the discord guild.
        - default_role_id (str): ID of the default role.
        - home_msg_id (str): ID of the home message.
        - cursed_words (str): String containing all cursed words;
            Created by: ','.join(cursed_words: lst);
        - react_role_dict (str): String contining parsed json dictionary
            {"emote_id": role_id, }
        - ract_role_message_id (str): ID of the react_role message.

    '''
    __tablename__ = "admin_options"

    id = Column('id', Integer, primary_key=True)

    guild_id = Column('guild_id', String(100))
    default_role_id = Column('default_role_id', String(100), nullable=True)
    home_msg_id = Column('home_msg_id', String(100), nullable=True)
    react_role_dict = Column('react_role_dict', Text, nullable=True)
    ract_role_message_id = Column('ract_role_message_id', String(100), nullable=True)
    cursed_words = Column('cursed_words', String(500), nullable=True)


class BotConfigs(Base):
    '''
    Bot Configs.

    Rows:
        - yaml_yt_list (text): String containing parsed yaml dictionary
            {"%Y-%m-%d": ["url1", "url2", ...]}

    '''

    __tablename__ = "bot_configs"

    id = Column('id', Integer, primary_key=True)

    yaml_yt_list = Column('yaml_yt_list', Text, nullable=True)

    # Migration:
    # CREATE TABLE bot_configs (
    #       id INTEGER NOT NULL,
    #       yaml_yt_list TEXT,
    #       PRIMARY KEY (id)
    # )

# class Streamer(Base):
#     '''
#     Streamer Model for storage of notifications settings.
#
#     Fields:
#         - guild_id (int): ID of the discord guild.
#         - disc_id (str): ID of the ctx author.
#         - twitch_url (str): URL of twitch stream.
#
#     '''
#     __tablename__ = "streamer"
#
#     guild_id = Column('guild_id', String(100))
#     id = Column('id', Integer, primary_key=True)
#     disc_id = Column('disc_id', String(100))
#     twitch_url = Column('twitch_url', String(150), unique=True)
#
#     def __repr__(self):
#         return f'{self.id} - {self.disc_id} - {self.twitch_url}'
