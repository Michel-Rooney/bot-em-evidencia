from datetime import datetime


def msg_time() -> datetime:
    """
    Função utilizada para mostra o tempo nos logs
    """

    return f'[{datetime.now().strftime("%H-%m-%d %H:%M")}]'
