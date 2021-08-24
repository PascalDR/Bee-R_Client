import json
from .logger import Logger
from .singleton import Singleton
from .daemon import Daemon
from .sensor import Sensor, get_sensor
from .validator import validator


def init(config: str):
    with open(config) as c:
        data = json.load(c)
        validator(data)
        Daemon(data).start()
