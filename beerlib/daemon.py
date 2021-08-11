import ssl
import time
import json
import schedule
import paho.mqtt.client as paho
from .        import Sensor, Logger
from typing   import Dict, List, Any
from datetime import datetime

class Daemon:
    def __init__( self, client_id, user_name, password, ca_file, url, port, interval ) -> None:
      self.client            = paho.Client( client_id = client_id )
      self.client.username_pw_set( username = user_name, password = password )
      self.client.on_message = self.onMessage
      self.client.on_log     = self.onLog
      self.client.on_connect = self.onConnect
      self.client.tls_set( ca_file, tls_version = ssl.PROTOCOL_TLSv1_2 )
      self.client.tls_insecure_set( True )
      self.client.connect( url, port, 60 )
      
      self.interval = interval
      self.sensors  = []
      self.logger   = Logger()

      schedule.every( interval ).seconds.do( self._process )

    def onMessage( self, client, userdata, message ) -> None:
      pass

    def onLog( self, client, userdata, level, buf ) -> None:
      self.logger.info( buf )

    def onConnect( self, client, userdata, flags, rc ) -> None:
      pass

    def generateJson( self ) -> List[ Dict[ str, Any ] ]:
        return [ sensor.toJson() for sensor in self.sensors ]

    def generateMetrics( self ) -> Dict[ str, Any ]:
      return { "client_id": self.client._client_id.decode( "utf-8" ), 
               "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "metrics": self.generateJson() }

    def addSensor( self, sensor: Sensor ) -> None:
      self.sensors.append( sensor )

    def process( self ) -> None:
      self.client.publish( "metrics", json.dumps( self.generateMetrics() ) )

    def start( self ) -> None:
      self.client.loop_start()

      while True:
        self.process()
        time.sleep( 100 )
