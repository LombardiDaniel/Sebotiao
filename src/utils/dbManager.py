import os
import logging

import json

from abc import ABC

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import AdminOptions, BotConfigs
from main import Base

from utils.docker import DockerLogger


class dbManager(ABC):
    '''
    This class creates the db engine for use in all sub-classes.
    The ID of discord Snowflake Objects are stored as strings in the database.

    Args:
        - guild_id (str): string containing the guild id.

    Attributes:
        - session: sessionmaker object from SQLalchemy
        - engine: engine object from SQLalchemy

    Methods:
        None.

    '''

    def __init__(self, guild_id):
        self.logger = DockerLogger(prefix='dbManager', lvl=DockerLogger.INFO)

        self.log_handler = logging.FileHandler('./logs/sqlalchemy.log', mode='a+')
        self.log_handler.setLevel(logging.INFO)
        self.db_logger = logging.getLogger('sqlalchemy')
        self.db_logger.addHandler(self.log_handler)
        self.db_logger.setLevel(logging.INFO)

        self.guild_id = str(guild_id)

        db_user = os.environ.get('POSTGRES_USER')
        db_pass = os.environ.get('POSTGRES_PASSWORD')

        host = os.environ.get('DB_HOST')
        db_host = host if host is not None else 'db'

        db_name = os.environ.get('POSTGRES_DB')
        db_port = os.environ.get('POSTGRES_PORT')

        # If debug mode, creates local sqlite database
        if int(os.environ.get('DEBUG')):
            self.engine = create_engine(
                'sqlite:////devdb/sqlite.db?check_same_thread=False',
                echo=True
            )
            self.logger.log("Connected to SQLITE DB (Do NOT use in production)",
                lvl=self.logger.WARNING)
        else:
            # Raises an error if any of the needed env vars were not declared
            if any(not var for var in [db_user, db_pass, db_name, db_port]):
                self.logger.log(
                f"""Missing ENV VARS:
                    POSTGRES_USER: '{db_user}',
                    POSTGRES_PASSWORD: '{db_pass}',
                    POSTGRES_DB: '{db_name}',
                    DB_HOST: '{db_host}',
                    POSTGRES_PORT: '{db_port}'
                    """, lvl=self.logger.ERROR)
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
                echo=False
            )
            self.logger.log("Connected to PostgreSQL",
                lvl=self.logger.INFO)

        logging.getLogger('sqlalchemy').addHandler(self.log_handler)
        Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)


# class dbStatic():
#     def __init__()


class dbAutoMod(dbManager):
    '''
    This class that abstracts the interaction with the database, offering simpler methods.
    When creating an object from this class, all methods will use self.guild_id to
    select what row should be altered in the desired table.

    Args:
        - guild_id (str): string containing the guild id.

    Attributes:
        - cursed_words (lst): List of all cursed words stored in the database.

    Methods:
        - add_cursed_words: Adds a new cursed word to the database.
        - remove_cursed_words: Removes a cursed word from the database.
    '''

    def add_cursed_words(self, words):
        '''
        Adds/Updates the current list of cursed words.

        Args:
            - words (lst): List of words to add to cursed_words.

        Returns:
            None.

        '''

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                if guild_query.cursed_words:

                    new_words = set(words + guild_query.cursed_words.split(','))

                    guild_query.\
                        cursed_words = ','.join(new_words)

                    session.commit()
                else:
                    guild_query.cursed_words = ','.join(set(words))
                    session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.cursed_words = ','.join(set(words))
                session.add(admin_options)
                session.commit()

    def remove_cursed_words(self, words):
        '''
        Removes the current list of cursed words.

        Args:
            - words (lst): List of words to remove from cursed_words.

        Returns:
            None.

        '''

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                if guild_query.cursed_words:

                    # Removes words
                    curr_words = guild_query.cursed_words.split(',')
                    for word in words:
                        if word in curr_words:
                            curr_words.remove(word)
                            break

                    # Updates table
                    guild_query.\
                        cursed_words = ','.join(set(curr_words))
                    session.commit()

    @property
    def cursed_words(self):
        '''
        Gets the default role for new users from database.

        Args:
            None.

        Returns:
            - cursed_words (lst): List of all cursed words stored in db.

        '''

        with self.session() as session:
            admin_options = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            if admin_options is None:
                return ["sem configuração"]
            if not admin_options.cursed_words:
                return ["nenhuma palavra banida"]

            return admin_options.cursed_words.split(',')


class dbAutoRole(dbManager):
    '''
    This class that abstracts the interaction with the database, offering simpler methods.
    When creating an object from this class, all methods will use self.guild_id to
    select what row should be altered in the desired table.

    Args:
        - guild_id (str): string containing the guild id.

    Attributes:
        - default_role_id (int): ID of the default role.
        - home_msg_id (int): ID of home welcome message.
        - react_role_dict (dict): dictionary {"emoji_id": role_id}.
        - react_role_msg_id (int): ID of react/role msg.

    Methods:
        - update_default_role: Updates the default role in database.
        - set_welcome_channel: Sets the welcome channel in db.
        - remove_welcome_channel: Removes the welcome channel in db.
        - set_react_role_message: Sets the react/role message.
        - add_react_role: Adds a react/role combo to db.

    '''

    def update_default_role(self, default_role_id):
        '''
        Adds/Updates the current default role in the database.

        Args:
            - default_role_id (int): ID of default role.

        Returns:
            None.

        '''

        str_default_role_id = str(default_role_id)

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                if guild_query.default_role_id:
                    guild_query.default_role_id = str_default_role_id
                    session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.default_role_id = str_default_role_id
                session.add(admin_options)
                session.commit()

    def set_welcome_channel(self, home_msg_id):
        '''
        Adds/Updates the current home channel msg in the database.

        Args:
            - home_msg_id (int): ID of home channel message.

        Returns:
            None.

        '''

        home_msg_id = str(home_msg_id)

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                guild_query.home_msg_id = home_msg_id
                session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.home_msg_id = home_msg_id
                session.add(admin_options)
                session.commit()

    def remove_welcome_channel(self):
        '''
        Removes the current home channel msg in the database.

        Args:
            None.

        Returns:
            None.

        '''

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()


            # if there are already entries for this guild, updates them
            if guild_query is not None:
                if guild_query.home_msg_id:
                    guild_query.home_msg_id = "0"
                    session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.home_msg_id = "0"
                session.add(admin_options)
                session.commit()

    def set_react_role_message(self, message_id):
        '''
        Adds/Updates the current ract_role_message_id.
        Args:
            - message_id (int): ID of message from react_role.
        Returns:
            None.
        '''

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                guild_query.ract_role_message_id = str(message_id)
                session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.ract_role_message_id = str(message_id)
                session.add(admin_options)
                session.commit()

    def add_react_role(self, react_role_dict):
        '''
        Adds/Updates the current ract_role_dictionary.

        Args:
            - react_role_dict (dict): dictionary in the format:
                {
                    "react_emote": role_id,
                }

        Returns:
            None.

        '''

        with self.session() as session:
            guild_query = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            # if there are already entries for this guild, updates them
            if guild_query is not None:
                if guild_query.react_role_dict:

                    curr_dict = json.loads(guild_query.react_role_dict)
                    curr_dict.update(react_role_dict)

                    guild_query.react_role_dict = json.dumps(curr_dict)
                    session.commit()
                else:
                    guild_query.react_role_dict = json.dumps(react_role_dict)
                    session.commit()

            # if there are no entries for this guild, creates entry
            else:
                admin_options = AdminOptions()
                admin_options.guild_id = self.guild_id
                admin_options.react_role_dict = json.dumps(react_role_dict)
                session.add(admin_options)
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

        with self.session() as session:
            admin_options = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            if admin_options is None:
                return None
            if not admin_options.default_role_id:
                return None

            return int(admin_options.default_role_id)

    @property
    def home_msg_id(self):
        '''
        Gets the home channel message id.

        Args:
            None.

        Returns:
            - home_msg_id (int): ID of the home channel message.

        '''

        with self.session() as session:
            admin_options = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            if admin_options is None or admin_options.home_msg_id is None:
                return 0

            return int(admin_options.home_msg_id)

    @property
    def react_role_dict(self):
        '''
        Gets the {"emoji_id": role_id} dict

        Args:
            None.

        Returns:
            - react_role_dict (dict): dict containing reacts and role_ids
                that they point to.

        '''

        with self.session() as session:
            admin_options = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            return json.loads(admin_options.react_role_dict)


    @property
    def react_role_msg_id(self):
        '''
        Gets the {"emoji_id": role_id} message_id

        Args:
            None.

        Returns:
            - react_role_msg_id (int): ID of message to monitor.

        '''

        with self.session() as session:
            admin_options = session.query(AdminOptions).filter(
                AdminOptions.guild_id == self.guild_id).one_or_none()

            return int(admin_options.react_role_message_id) if admin_options is not None else None


class dbBotConfig(dbManager):
    '''
    Bot Configs, such as yt_yaml_lst.
    '''

    def __init__(self):
        '''
        Guild id passed as -1 to ignore error message from not having a guild.
        '''
        super().__init__(guild_id=-1)


    def update_yt_yaml(self, yaml_lst):
        '''
        Replaces the existing yt_yaml row in the database.

        Args:
            - yaml_lst (str): parsed yaml in the form:
                {'%Y-%m-%d': ['url1', 'url2', ...]}
        '''

        with self.session() as session:
            conf_query = session.query(BotConfigs).filter(
                BotConfigs.id == 0).one_or_none()

            # if there are already entries, updates them
            if conf_query is not None:
                self.logger.log("Updating BotConfig update_yt_yaml", lvl=self.logger.INFO)
                conf_query.yaml_yt_list = json.dumps(yaml_lst)
                session.commit()

            # if there are no entries, creates one
            else:
                self.logger.log("Addin a new BotConfig entry from update_yt_yaml",
                    lvl=self.logger.WARNING)
                conf_new = BotConfigs()
                conf_new.id = 0
                conf_new.yaml_yt_list = json.dumps(yaml_lst)
                session.add(conf_new)
                session.commit()

    @property
    def yt_yaml(self):
        '''
        Gets the yaml format from memory.
        Returns:
            - yt_yaml (dict): parsed json dictionary.
        '''

        with self.session() as session:
            conf_query = session.query(BotConfigs).filter(
                BotConfigs.id == 0).one_or_none()

            if conf_query is not None:
                return json.loads(conf_query.yaml_yt_list)

            return None
