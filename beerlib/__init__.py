import sys
import ssl
import time
import toml
import json
import logging
import sqlite3
import colorlog
from random import random
from datetime import datetime
import paho.mqtt.client as paho

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter( '%(log_color)s[%(asctime)s]%(levelname)s:%(message)s' ) )
logger = colorlog.getLogger( 'console_logger' )
logger.addHandler( handler )

logging.basicConfig( format='[%(asctime)s]%(levelname)s:%(message)s', \
                     filename = 'bee-r.log', encoding = 'utf-8',      \
                     level = logging.DEBUG )

defined_sensors = {}

def defineSensor( sensor_class ):
  defined_sensors[ sensor_class.__name__ ] = sensor_class
  return sensor_class

def sensorDefined( sensor_name ):
  return defined_sensors.get( sensor_name, None ) != None

class Sensor:
  def __init__( self, id, pin ):
    self.pin  = pin
    self.id   = id
  
  def read( self ):
    raise NotImplementedError

  def toJson( self ):
    return { "id": self.id, "values": self.read() }

@defineSensor
class DummySensor( Sensor ):
  def read( self ):
    return [ random() ]

class BeeR:
    def __init__( self, client_id, user_name, password, ca_file, url, port, interval ):
      self.client            = paho.Client( client_id = client_id )
      self.client.username_pw_set( username = user_name, password = password )
      self.client.on_message = self.on_message
      self.client.on_log     = self.on_log
      self.client.on_connect = self.on_connect
      self.client.tls_set( ca_file, tls_version=ssl.PROTOCOL_TLSv1_2 )
      self.client.tls_insecure_set( True )
      self.client.connect( url, port, 60 )
      self.interval = interval
      self.sensors = []
      self.today = datetime.now()

    def on_message( self, client, userdata, message ):
      pass

    def on_log( self, client, userdata, level, buf ):
      logger.info( buf )

    def on_connect( self, client, userdata, flags, rc ):
      pass

    def generateJson( self ):
        return [ sensor.toJson() for sensor in self.sensors ]

    def generateMetrics( self ):
      return { "client_id": self.client._client_id.decode( "utf-8" ), 
               "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "metrics": self.generateJson() }

    def addSensor( self, sensor ):
      self.sensors.append( sensor )

    def _process( self ):
      self.client.publish( "metrics", json.dumps( self.generateMetrics() ) )

    def _everyDay( self ):
      pass

    def _everyMonth( self ):
      pass

    def _everyYear( self ):
      pass

    def start( self ):
      class NoDateChange( Exception ):
        pass
      self.client.loop_start()
      while True:
        self._process()
        try:
          now = datetime.now()
          if now.strftime( "%d" ) != self.today.strftime( "%d" ):
            self._everyDay()
          elif now.strftime( "%m" ) != self.today.strftime( "%m" ):
            self._everyMonth()
          elif now.strftime( "%Y" ) != self.today.strftime( "%Y" ):
            self._everyYear()
          else:
            raise NoDateChange
        except NoDateChange:
          pass
        else:
          self.today = now
        time.sleep( self.interval )

class BeeRDB( BeeR ):
    def __init__( self, db_path, *args, **kargs ):
        super( BeeRDB, self ).__init__( *args, **kargs )
        self.database = sqlite3.connect( db_path )
        self.db_conn  = self.database.cursor()
        self.db_conn.execute( """CREATE TABLE IF NOT EXISTS metrics (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    date TEXT,
                                    metrics TEXT )""" )

    def _everyDay( self ):
      self.db_conn.execute( "DELETE FROM metrics WHERE date <= date( 'now', '-30 day' )" )

    def _process( self ):
      metrics = self.generateMetrics()
      self.client.publish( "metrics", json.dumps( metrics ) )
      self.db_conn.execute( "INSERT INTO metrics VALUES( NULL, ?, ? )", [ metrics[ "date" ], json.dumps( metrics[ "metrics" ] ) ] )

def _readConfig( path ):
  try:
    logger.info( "Parsing '{0}'".format( path ) )

    config_file = open( path ).read()
    config = toml.loads( config_file )

    server_config = config.get( 'ServerConfig', None )
    if server_config != None:
      if server_config.get( 'url', None ) == None:
        raise Exception( "You must provide an 'url' field in 'ServerConfig' section" )
      elif server_config.get( 'port', None ) == None:
        raise Exception( "You must provide an 'port' field in 'ServerConfig' section" )
    else:
      raise Exception( "You must provide a 'ServerConfig' section in '{0}'".format( path ) )

    client_config = config.get( 'ClientConfig', None )
    if client_config != None:
      if client_config.get( 'id', None ) == None:
        raise Exception( "You must provide an 'id' field in 'ClientConfig' section" )
      elif client_config.get( 'metric_interval', None ) == None:
        raise Exception( "You must provide an 'metric_interval' field in 'ClientConfig' section" )
      elif client_config.get( 'username', None ) == None:
        raise Exception( "You must provide an 'username' field in 'ClientConfig' section" )
      elif client_config.get( 'password', None ) == None:
        raise Exception( "You must provide an 'password' field in 'ClientConfig' section" )
      elif client_config.get( 'ca_path', None ) == None:
        raise Exception( "You must provide a 'ca_path' field in 'ClientConfig' section" )
    else:
      raise Exception( "You must provide a 'ClientConfig' section in '{0}'".format( path ) )

    sensors = config.get( 'Sensors', None )
    if sensors != None:
      if len( sensors ) == 0:
        raise Exception( "You must declare almost one sensor in 'Sensor' section of '{0}'".format( path ) )
      for sensor_id in sensors:
        current_sensor = sensors[ sensor_id ]
        if current_sensor.get( 'id', None ) == None:
          raise Exception( "You must provide an 'id' for sensor '{0}' in 'Sensors' section".format( sensor_id ) )
        elif current_sensor.get( 'pin', None ) == None:
          raise Exception( "You must provide a 'pin' for sensor '{0}' in 'Sensors' section".format( sensor_id ) )
        
        if current_sensor.get( 'type', None ) == None:
          raise Exception( "You must provide a 'type' for sensor '{0}' in 'Sensors' section".format( sensor_id ) )
        else:
          if not sensorDefined( current_sensor[ 'type' ] ):
            raise Exception( "Calss for Sensor of type '{0}' not declared".format( current_sensor[ 'type' ] ) )
    else:
      raise Exception( "You must provide a 'Sensor' section in '{0}'".format( path ) )

    logger.info( "'{0}' parsed without errors".format( path ) )
    return config

  except FileNotFoundError as err:
    logger.error( "'config.toml' not found in the current directory" )
    exit( 1 )
  except toml.decoder.TomlDecodeError as err:
    logger.error( "Error occurred parsing 'config.toml': {0}".format( err ) )
    exit( 1 )
  except Exception as err:
    logger.error( "Error occurred parsing 'config.toml': {0}".format( err ) )
  except:
    logger.error( sys.exc_info()[0] )
    exit( 1 )

def fromToml( path = "./config.toml" ):
  conf = _readConfig( path )

  if conf[ 'ClientConfig' ].get( 'db_path', None ):
    beer_i = BeeRDB( conf[ 'ClientConfig' ][ 'db_path' ],
                     conf[ 'ClientConfig' ][ 'id' ],
                     conf[ 'ClientConfig' ][ 'username' ],
                     conf[ 'ClientConfig' ][ 'password' ],
                     conf[ 'ClientConfig' ][ 'ca_path' ], 
                     conf[ 'ServerConfig' ][ 'url' ],
                     conf[ 'ServerConfig' ][ 'port' ],
                     conf[ 'ClientConfig' ][ 'metric_interval' ] )
  else:
    beer_i = BeeR( conf[ 'ClientConfig' ][ 'ca_path' ], 
                   conf[ 'ClientConfig' ][ 'id' ],
                   conf[ 'ClientConfig' ][ 'username' ],
                   conf[ 'ClientConfig' ][ 'password' ],
                   conf[ 'ServerConfig' ][ 'url' ],
                   conf[ 'ServerConfig' ][ 'port' ],
                   conf[ 'ClientConfig' ][ 'metric_interval' ] )

  for sensor_id in conf[ 'Sensors' ]:
    current_sensor = conf[ 'Sensors' ][ sensor_id ]
    beer_i.addSensor( defined_sensors[ current_sensor[ 'type' ] ]( current_sensor[ 'id' ], current_sensor[ 'pin' ] ) )

  return beer_i