from datetime import datetime


def docker_log(msg, lvl='INFO'):
    '''
    Simple function to log to stdout.

    Args:
        - msg (str): message to be logged
        - lvl (str, optional): level of logged message
    '''
    print(f'{str(datetime.now())[:-3]}; {lvl.upper()}; {msg};')
