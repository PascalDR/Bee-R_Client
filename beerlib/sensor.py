from random import random
from typing import Dict, Any, Union, Callable


class Sensor:
    def __init__(self, sid, pin) -> None:
        self.pin = pin
        self.id = sid
  
    def read(self) -> float:
        raise NotImplementedError

    def generate_json(self) -> Dict[str, Any]:
        return {'sensor_id': self.id, 'value': self.read()}


defined_sensors: Dict[str, Sensor] = {}


def define_sensor(sensor_class: Sensor) -> Sensor:
    defined_sensors[sensor_class.__name__] = sensor_class
    return sensor_class


def sensor_defined(sensor_name: str) -> bool:
    return defined_sensors.get(sensor_name, None) is not None


def get_sensor(sensor_name: str) -> Union[Any, None]:
    return defined_sensors.get(sensor_name, None)


@define_sensor
class DummySensor(Sensor):
    def read(self) -> float:
        return random()
