from datetime import datetime


class DockerLogger:
    '''
    Basic Logger for .log files and stdout (for docker).

    properties:
        - prefix (str): Used for name of log_file and flag on stdout.
        - path (str): Path of log_file.
        - lvl (int by constant): Logger will log all messages flagged with higher
            or equal to this.
    '''

    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


    def __init__(self, prefix, lvl):
        self.prefix = prefix
        self.path = f'./logs/{prefix}.log'
        self.lvl = lvl

    def log(self, msg, lvl=2):
        '''
        Simple function to log to stdout.

        Args:
            - msg (str): message to be logged
            - lvl (constant): level of logged message
        '''

        if lvl >= self.lvl:

            if self.path is not None:
                with open(self.path, 'a') as log_file:
                    log_file.write(f'{self._lvl_str(lvl)}; {str(datetime.now())[:-3]}; {msg};\n')

            DockerLogger.stdout_log(msg, lvl=self._lvl_str(lvl), prefix=self.prefix)


    @staticmethod
    def _lvl_str(lvl):
        '''
        Converts lvl int to appropriate str.
        '''

        lst_lvl = [
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL'
        ]

        return lst_lvl[lvl - 1]


    @staticmethod
    def stdout_log(msg, lvl='INFO', **kwargs):
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
