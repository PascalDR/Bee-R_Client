import logging
from .singleton import Singleton
from colorlog import StreamHandler, ColoredFormatter, getLogger


class Logger(Singleton):
    def __init__(self) -> None:
        super().__init__()

        handler = StreamHandler()
        handler.setFormatter(ColoredFormatter('%(log_color)s[%(asctime)s]%(levelname)s:%(message)s'))
        logger = getLogger('console_logger')
        logger.addHandler(handler)

        logging.basicConfig(format='[%(asctime)s]%(levelname)s:%(message)s',
                            filename='bee-r.log', level=logging.DEBUG)

        self.logger = logger

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)
