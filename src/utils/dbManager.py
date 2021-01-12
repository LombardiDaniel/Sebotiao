import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import AdminOptions
from run import Base


class dbManager:
    '''
    This class creates the db engine for use in all sub-classes.

    Args:
        - guild_id (str): string containing the guild id.

    Attributes:
        - session: sessionmaker object from SQLalchemy
        - engine: engine object from SQLalchemy

    Methods:
        None.

    '''

    def __init__(self, guild_id):
        self.guild_id = str(guild_id)
        db_user = os.environ.get('POSTGRES_USER')
        db_pass = os.environ.get('POSTGRES_PASSWORD')

        host = os.environ.get('DB_HOST')
        db_host = host if host is not None else 'db'

        db_name = os.environ.get('POSTGRES_DB')
        db_port = os.environ.get('POSTGRES_PORT')

        # If debug mode, creates local sqlite database
        if int(os.environ.get('DEBUG')):
            self.engine = create_engine(f'sqlite:///sqlite.db', echo=False)
        else:
            # Raises an error if any of the needed env vars were not declared
            if any(not var for var in [db_user, db_pass, db_name, db_port]):
                raise NameError(
                    f"""Missing ENV VARS:
                        POSTGRES_USER: '{db_user}',
                        POSTGRES_PASSWORD: '{db_pass}',
                        POSTGRES_DB: '{db_name}',
                        DB_HOST: '{db_host}',
                        POSTGRES_PORT: '{db_port}'
                        """)

            self.engine = create_engine(
                f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}',
                echo=False)

        Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)


# class dbStreamManager(dbManager):
#
#     def add_streamer(self, disc_id, twitch_url):
#         '''
#         Adds a streamer to the database.
#
#         Args:
#             - disc_id (int): ID of the user that created the request.
#             - twitch_url (str): URL of the live-stream from twitch.
#
#         Returns:
#             None.
#
#         '''
#         session = self.session()
#
#         streamer = Streamer()
#         streamer.guild_id = self.guild_id
#         streamer.disc_id = str(disc_id)
#         streamer.twitch_url = twitch_url
#
#         session.add(streamer)
#         session.close()


class dbAutoMod(dbManager):
    '''
    This class that abstracts the interaction with the database, offering simpler methods.
    When creating an object from this class, all methods will use self.guild_id to
    select what row should be altered in the desired table.

    Args:
        - guild_id (str): string containing the guild id.

    Attributes:
        - default_role_id (int): the id of the default role.
        - cursed_words (lst): List of all cursed words stored in the database.

    Methods:
        - update_default_role: Updates the default role in database.
        - add_cursed_words: Adds a new cursed word to the database.
        - remove_cursed_words: Removes a cursed word from the database.
    '''

    def update_default_role(self, default_role_id):
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

    def set_welcome_channel(self, home_msg_id):
        '''
        Adds/Updates the current home channel msg in the database.

        Args:
            - home_msg_id (int): ID of home channel message.

        Returns:
            None.

        '''

        home_msg_id = str(home_msg_id)

        session = self.session()

        guild_query = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        # if there are already entries for this guild, updates them
        if guild_query.count():
            guild_query[-1].home_msg_id = str(home_msg_id)
            session.commit()

        # if there are no entries for this guild, creates entry
        else:
            admin_options = AdminOptions()
            admin_options.guild_id = self.guild_id
            admin_options.home_msg_id = str(home_msg_id)
            session.add(admin_options)
            session.commit()

        session.close()

    def remove_welcome_channel(self):
        '''
        Adds/Updates the current home channel msg in the database.

        Args:
            None.

        Returns:
            None.

        '''

        session = self.session()

        guild_query = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        # if there are already entries for this guild, updates them
        if guild_query.count():
            if guild_query[-1].home_msg_id:
                guild_query[-1].home_msg_id = "0"
                session.commit()

        # if there are no entries for this guild, creates entry
        else:
            admin_options = AdminOptions()
            admin_options.guild_id = self.guild_id
            admin_options.home_msg_id = "0"
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
                    cursed_words = ','.join(
                        words + guild_query[-1].cursed_words.split(','))
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
    def default_role_id(self):
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

        return int(admin_options[-1].default_role_id)

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

    @property
    def home_msg_id(self):
        '''
        Gets the home channel message id.

        Args:
            None.

        Returns:
            - home_msg_id (int): ID of the home channel message.

        '''

        session = self.session()

        admin_options = session.query(AdminOptions).filter(
            AdminOptions.guild_id == self.guild_id)

        session.close()

        if not admin_options.count() or not admin_options[-1].home_msg_id:
            return 0

        return int(admin_options[-1].home_msg_id)
