from sqlalchemy import Column, Integer, String
from run import Base


class AdminOptions(Base):
    '''
    Admin Model for storage of automod settings.

    Fields:
        - guild_id (int): ID of the discord guild.
        - default_role_id (str): ID of the default role.
        - cursed_words (str): String containing all cursed words;
            Created by: ','.join(cursed_words: lst);

    '''
    __tablename__ = "admin_options"

    guild_id = Column('guild_id', String(100))
    id = Column('id', Integer, primary_key=True)
    default_role_id = Column('default_role_id', String(100), nullable=True)
    cursed_words = Column('cursed_words', String(500), nullable=True)


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
