import ssl
import time
import json
import schedule
import paho.mqtt.client as paho
from .sensor import Sensor, sensor_defined, get_sensor
from .logger import Logger
from typing import Dict, List, Any
from datetime import datetime


class Daemon:
    def __init__(self, config: Any) -> None:
        print( config )
        self.client = paho.Client(client_id=config['ClientConfig']['username'])
        self.client.username_pw_set(username=config['ClientConfig']['username'],
                                    password=config['ClientConfig']['password'])
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.client.on_connect = self.on_connect
        self.client.connect(config['ServerConfig']['url'], config['ServerConfig']['port'], 60)

        ca_path = config['ClientConfig'].get('ca_path', None)

        if ca_path is not None:
            self.client.tls_set(ca_path, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.client.tls_insecure_set(True)

        self.sensors: List[Sensor] = []

        for s in config['Sensors']:
            if sensor_defined(s['type']):
                sensor_class = get_sensor(s['type'])
                self.sensors.append(sensor_class(s['id'], s['pin']))

        self.logger: Logger = Logger()

        schedule.every(config['ClientConfig']['metric_interval']).seconds.do(self.process)

    def on_message(self, client, userdata, message) -> None:
        pass

    def on_log(self, client, userdata, level, buf) -> None:
        self.logger.info(buf)

    def on_connect(self, client, userdata, flags, rc) -> None:
        pass

    def generate_json(self) -> List[Dict[str, Any]]:
        return [sensor.generate_json() for sensor in self.sensors]

    def generate_metrics(self) -> Dict[str, Any]:
        return {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reads": self.generate_json()}

    def process(self) -> None:
        metric = self.generate_metrics()
        self.client.publish("metrics", json.dumps(metric))
        self.logger.info('published: "{}"'.format(metric))

    def start(self) -> None:
        self.client.loop_start()

        while True:
            self.process()
            time.sleep(100)
