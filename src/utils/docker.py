from datetime import datetime


class DockerLogger:
    '''
    Basic Logger for .log files and stdout (for docker).
    '''

    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


    def __init__(self, prefix, lvl=2):
        self.prefix = prefix
        self.path = f'./logs/{prefix}.log'
        self.lvl = lvl

    def log(self, msg, lvl=DockerLogger.WARNING):
        '''
        Simple function to log to stdout.

        Args:
            - msg (str): message to be logged
            - lvl (constant): level of logged message
        '''

        if lvl >= self.lvl:

            if self.path is not None:
                with open(self.path, 'a') as log_file:
                    log_file.write(f'{self.lvl_str}; {str(datetime.now())[:-3]}; {msg};')

            DockerLogger.docker_log(msg, lvl=self.lvl_str, prefix=self.prefix)


    @property
    def lvl_str(self):
        '''
        Converts lvl int to appropriate str.
        '''

        lst_lvl = [
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL'
        ]

        return lst_lvl[self.lvl + 1]


    @staticmethod
    def docker_log(msg, lvl='INFO', **kwargs):
        '''
        Simple function to log to stdout.

        Args:
            - msg (str): message to be logged
            - lvl (constant): level of logged message
        '''


        log = f'{lvl.upper()}; {str(datetime.now())[:-3]}; {msg};'

        if 'prefix' in kwargs:
            log = f"{lvl}; {kwargs.get('prefix')}; {str(datetime.now())[:-3]}; {msg};"
            del kwargs['prefix']
        else:
            log = f"{lvl}; {str(datetime.now())[:-3]}; {msg};"

        for key, value in kwargs.items():
            log += f"{key}: {value}; "

        print(log)
