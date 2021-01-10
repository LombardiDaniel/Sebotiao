import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import AdminOptions
from run import Base

from utils.docker import docker_log

class dbManager:
    '''
    This class creates the db engine for use in all sub-classes.
    '''

    def __init__(self, guild_id):
        self.guild_id = str(guild_id)
        db_user = os.environ.get('POSTGRES_USER')
        db_pass = os.environ.get('POSTGRES_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_name = os.environ.get('POSTGRES_DB')
        db_port = os.environ.get('POSTGRES_PORT')

        if int(os.environ.get('DEBUG')):
            self.engine = create_engine(f'sqlite:///sqlite.db', echo=True)
        else:
            self.engine = create_engine(
                f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}',
                echo=False)

        Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)



class dbStreamManager(dbManager):

    def add_streamer(self, disc_id, twitch_url):
        '''
        Adds a streamer to the database.

        Args:
            - disc_id (int): ID of the user that created the request.
            - twitch_url (str): URL of the live-stream from twitch.

        Returns:
            None.

        '''
        session = self.session()

        streamer = Streamer()
        streamer.guild_id = self.guild_id
        streamer.disc_id = str(disc_id)
        streamer.twitch_url = twitch_url

        session.add(streamer)
        session.close()



class dbAutoMod(dbManager):

    def update_default_role(self, default_role_id: int):
        '''
        Adds/Updates the current default role in the database.

        Args:
            - default_role_id (int): ID of default role.

        Returns:
            None.

        '''

        default_role_id = str(default_role_id)

        session = self.session()

        guild_query = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        # if there are already entries for this guild, updates them
        if guild_query.count():
            if guild_query[-1].default_role_id:
                guild_query[-1].default_role_id = default_role_id
                session.commit()

        # if there are no entries for this guild, creates entry
        else:
            admin_options = AdminOptions()
            admin_options.guild_id = self.guild_id
            admin_options.default_role_id = default_role_id
            session.add(admin_options)
            session.commit()

        session.close()


    def add_cursed_words(self, words):
        '''
        Adds/Updates the current list of cursed words.

        Args:
            - words (lst): List of words to add to cursed_words.

        Returns:
            None.

        '''
        session = self.session()

        guild_query = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        # if there are already entries for this guild, updates them
        if guild_query.count():
            if guild_query[-1].cursed_words:
                guild_query[-1].\
                    cursed_words = ','.join(words + guild_query[-1].cursed_words.split(','))
                session.commit()
            else:
                guild_query[-1].cursed_words = ','.join(words)
                session.commit()
        # if there are no entries for this guild, creates entry
        else:
            admin_options = AdminOptions()
            admin_options.guild_id = self.guild_id
            admin_options.cursed_words = ','.join(words)
            session.add(admin_options)
            session.commit()

        session.close()

    def remove_cursed_words(self, words):
        '''
        Removes the current list of cursed words.

        Args:
            - words (lst): List of words to remove from cursed_words.

        Returns:
            None.

        '''
        session = self.session()

        guild_query = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        # if there are already entries for this guild, updates them
        if guild_query.count():
            if guild_query[-1].cursed_words:

                # Removes words
                curr_words = guild_query[-1].cursed_words.split(',')
                for word in words:
                    if word in curr_words:
                        curr_words.remove(word)

                # Updates table
                guild_query[-1].\
                    cursed_words = ','.join(curr_words)
                session.commit()


    @property
    def default_role(self):
        '''
        Gets the default role for new users from database.

        Args:
            None.

        Returns:
            - default_role_id (int): ID of default role.

        '''

        session = self.session()

        admin_options = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        session.close()

        if not admin_options.count():
            return None
        if not admin_options[-1].default_role_id:
            return None

        return admin_options[-1].default_role_id


    @property
    def cursed_words(self):
        '''
        Gets the default role for new users from database.

        Args:
            None.

        Returns:
            - cursed_words (lst): List of all cursed words stored in db.

        '''

        session = self.session()

        admin_options = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        session.close()

        if not admin_options.count():
            return ["sem configuração"]
        if not admin_options[-1].cursed_words:
            return ["nenhuma palavra banida"]

        return admin_options[-1].cursed_words.split(',')
