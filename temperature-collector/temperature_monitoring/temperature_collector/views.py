# temperature_collector/views.py
import json
import os
import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from queue import Queue
import threading
import websocket
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler which logs messages to a file
file_handler = RotatingFileHandler(os.path.join(LOGS_DIR, 'temperature_collector.log'), maxBytes=10 * 1024 * 1024,
                                   backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Create a queue for storing temperature data
temperature_queue = Queue()
temperature_queue_lock = threading.Lock()

# Websocket configuration
RING_MASTER_WEBSOCKET_URL = "ws://localhost:9001"
WEBSOCKET_TIMEOUT = 20  # Timeout for websocket connection retry (in seconds)

ws_connection = None


def connect_websocket():
    global ws_connection
    while ws_connection is None:
        try:
            # Attempt to connect to websocket server
            ws_connection = websocket.create_connection(RING_MASTER_WEBSOCKET_URL)
            logging.info("Connected to websocket server.")
            return ws_connection
        except Exception as e:
            logging.error(f"Failed to connect to websocket server: {e}")
            logging.info(f"Retrying connection in {WEBSOCKET_TIMEOUT} seconds...")
            time.sleep(WEBSOCKET_TIMEOUT)


# Start a separate thread for websocket connection
websocket_thread = threading.Thread(target=connect_websocket)
websocket_thread.daemon = True
websocket_thread.start()


def send_temperature_data_websocket():
    global ws_connection
    # Wait for websocket connection to be established
    while ws_connection is None:
        logging.info("Waiting for websocket connection...")
        time.sleep(1)
        try:
            connect_websocket()
        except Exception as e:
            logging.error(f"Error establishing websocket connection: {e}")

    while True:
        if not temperature_queue.empty():
            with temperature_queue_lock:
                data = temperature_queue.queue[0]
            # Convert data to JSON format
            data_json = json.dumps(data)
            try:
                # Send data to websocket server
                ws_connection.send(data_json)
                logging.info("Temperature data sent via websocket.")
                with temperature_queue_lock:
                    temperature_queue.get()
            except Exception as e:
                logging.error(f"Error sending temperature data via websocket: {e}")
                ws_connection = None
                try:
                    connect_websocket()
                except Exception as e:
                    logging.error(f"Error re-establishing websocket connection: {e}")
        time.sleep(1)


"""
def send_temperature_data_websocket():
    while True:
        if not temperature_queue.empty():
            data = temperature_queue.get()
            logging.info(f"Popped temperature data from queue {data}")
            # Convert data to JSON format
            data_json = json.dumps(data)
            # Send data to external websocket server
            # ws = websocket.create_connection("ws://external_websocket_server_url")
            # ws.send(data_json)
            # ws.close()
            logging.info("Temperature data sent via websocket.")
        time.sleep(1)
"""

# Start a separate thread for sending temperature data via websocket
websocket_thread = threading.Thread(target=send_temperature_data_websocket)
websocket_thread.daemon = True
websocket_thread.start()


@csrf_exempt
def temperature_collector(request):
    if request.method == 'POST':
        try:
            # Parse POST data
            post_data = json.loads(request.body)
            country = post_data.get('location').get('country')
            name = post_data.get('location').get('name')
            latitude = post_data.get('location').get('latitude')
            longitude = post_data.get('location').get('longitude')
            sensor_type = post_data.get('type')
            value = post_data.get('value')

            logging.info(
                f"Received temperature measurement: {value}, from country: {country}, location: {name}, lt: {latitude}, lg:{longitude}")
            logging.info(f"Putting temperature data into queue")
            # Put temperature data in the queue
            with temperature_queue_lock:
                temperature_queue.put(post_data)

            # Respond with OK
            # Respond with status code 200
            return JsonResponse(status=200, data={'status': 'ok'})
        except Exception as e:
            logging.error(f"Error processing temperature data: {e}")
            return JsonResponse({'status': 'Error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'Error', 'message': 'Only POST requests are allowed'})
