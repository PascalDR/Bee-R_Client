
from random import random
from typing import List, Dict
from .      import Read, Metric

class Sensor:
    def __init__( self, id, pin ) -> None:
        self.pin  = pin
        self.id   = id
  
    def read( self ) -> Metric:
        raise NotImplementedError

defined_sensors: Dict[ str, Sensor ] = {}

def defineSensor( sensor_class ) -> Sensor:
  defined_sensors[ sensor_class.__name__ ] = sensor_class
  return sensor_class

def sensorDefined( sensor_name ) -> bool:
  return defined_sensors.get( sensor_name, None ) != None

@defineSensor
class DummySensor( Sensor ):
    def read( self ) -> Metric:
        return [ Read( sensor_id = id, value = random() ) ]