from datetime import datetime


def msg_time():
    return f'[{datetime.now().strftime("%H-%m-%d %H:%M")}]'
