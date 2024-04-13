import sys
import threading
import random
import time
import requests
import os
import logging
from queue import Queue
from xmlrpc.server import SimpleXMLRPCServer
from logging.handlers import RotatingFileHandler

# Create a 'logs' directory if it doesn't exist
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler which logs messages to a file
file_handler = RotatingFileHandler(os.path.join(LOGS_DIR, 'sensor_log.log'), maxBytes=10 * 1024 * 1024, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


class Location:
    def __init__(self, country, name, latitude, longitude):
        self.country = country
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


class Sensor:
    def __init__(self, sensor_type, country, location_name, latitude, longitude):
        self.type = sensor_type
        self.location = Location(country, location_name, latitude, longitude)
        self.measurement_queue = Queue()
        self.lock = threading.Lock()
        self.measure_thread_stop_event = threading.Event()
        self.dispatch_thread_stop_event = threading.Event()
        self.measure_thread = None
        self.dispatch_thread = None
        self.server_stopped = False

    def read(self):
        logging.info(f"Reading measurement from sensor {self.type}")
        return round(random.uniform(-50, 50), 2)

    def dispatch_measurement(self):
        logging.info("Dispatch measurement thread started")
        while not self.dispatch_thread_stop_event.is_set():
            if not self.measurement_queue.empty():
                measurement = self.measurement_queue.get()
                try:
                    self.send_measurement(measurement)
                    logging.info("Measurement dispatched successfully.")
                except Exception as e:
                    logging.error(f"Error sending measurement: {e}")
            time.sleep(1)
        logging.info("Dispatch measurement thread stopped.")

    def send_measurement(self, measurement):
        logging.info("Sending measurement to external API")
        # Simulating sending measurement to an external API via POST request
        api_endpoint = "https://example.com/api/measurement"
        payload = {
            "type": self.type,
            "location": {
                "country": self.location.country,
                "name": self.location.name,
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            },
            "value": measurement
        }
        """
        response = requests.post(api_endpoint, json=payload)
        if response.status_code != 200:
            logging.error(f"Failed to send measurement: {response.text}")
        """

    def measure(self):
        while not self.measure_thread_stop_event.is_set():
            measurement = self.read()
            logging.info(f"Reading measurement from sensor {measurement}")
            with self.lock:
                self.measurement_queue.put(measurement)
            time.sleep(60)
        logging.info("Measurement reading thread stopped.")

    def start_measurement(self):
        logging.info("Measurement reading thread started")

        self.measure_thread = threading.Thread(target=self.measure)
        self.measure_thread.daemon = True
        self.measure_thread.start()
        logging.info("Measurement reading started.")

    def stop_measurement(self):
        logging.info("Stopping measurement reading.")
        if self.measure_thread:
            self.measure_thread_stop_event.set()
            self.measure_thread.join()
        logging.info("Measurement reading stopped.")

    def start_dispatch(self):
        logging.info("Starting measurement dispatch.")
        self.dispatch_thread = threading.Thread(target=self.dispatch_measurement)
        self.dispatch_thread.daemon = True
        self.dispatch_thread.start()
        logging.info("Measurement dispatch started.")

    def stop_dispatch(self):
        logging.info("Stopping measurement dispatch.")
        if self.dispatch_thread:
            self.dispatch_thread_stop_event.set()
            self.dispatch_thread.join()
            logging.info("Measurement dispatch stopped.")

    def get_sensor_info(self):
        logging.info("Retrieving sensor information.")
        return {
            "type": self.type,
            "country": self.location.country,
            "location_name": self.location.name,
            "latitude": self.location.latitude,
            "longitude": self.location.longitude
        }

    def stop_server(self):
        logging.info("Stopping XML-RPC server.")
        self.server_stopped = True


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python program.py <sensor_type> <country> <location_name> <latitude> <longitude>")
        sys.exit(1)

    sensor_type = sys.argv[1]
    country = sys.argv[2]
    location_name = sys.argv[3]
    latitude = float(sys.argv[4])
    longitude = float(sys.argv[5])

    sensor = Sensor(sensor_type, country, location_name, latitude, longitude)

    # Create an XML-RPC server
    server = SimpleXMLRPCServer(('localhost', 8000), allow_none=True)
    server.register_instance(sensor)
    logging.info("RPC server started.")

    while not sensor.server_stopped:
        server.handle_request()

    logging.info("Exiting main program.")
