import datetime
import logging


# enable logging
logging.basicConfig(filename='logging.txt', level=logging.INFO)


def enable_backend_logging(file_path: str):
    handler = logging.FileHandler(file_path, encoding='utf-8')
    handler.setFormatter(logging.Formatter(f'{_now_until_seconds()}:Backend:%(message)s'))

    logger = logging.getLogger('fallback')
    logger.addHandler(handler)
    logger.setLevel(level=logging.INFO)


def _now_until_seconds() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str):
    logger = logging.getLogger('fallback')
    logger.info(msg=msg)
