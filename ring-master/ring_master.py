import threading
import websockets
from websockets.sync.client import connect
import asyncio
import logging
import queue
import json
import time
import socketio

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler('ring_master.log'),
                        logging.StreamHandler()
                    ])
COLLECTOR_SERVER_PORT = 9001


class Continent:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.queue = queue.Queue()
        self.queue_lock = threading.Lock()
        self.sio = None

    def send_data(self):
        while True:
            if not self.queue.empty():
                with self.queue_lock:
                    data = self.queue.queue[0]
                try:
                    if self.sio is None:
                        self.sio = socketio.Client()
                        self.sio.connect(self.url, namespaces='/continent', transports=['websocket'])
                    self.sio.send(data, namespace='/continent')
                    logging.info(f"Sent data to {self.name}: {data}")
                    self.queue.get()
                except Exception as e:
                    self.sio.disconnect()
                    logging.error(f"Error sending data to {self.name}: {e}")
            time.sleep(1)


# Global queue to store temperature data
global_queue = queue.Queue()
global_queue_lock = threading.Lock()


# Create instances of Continent class
continents = [
    Continent("Asia", "http://localhost:5001"),
    Continent("North America", "http://localhost:5002"),
    Continent("South America", "http://localhost:5003"),
    Continent("Europe", "http://localhost:5000"),
    Continent("Australia", "http://localhost:5004"),
    Continent("Africa", "http://localhost:5005"),
    Continent("Antarctica", "http://localhost:5006")
]


async def handle_websocket(websocket, path):
    try:
        while True:
            logging.info("Waiting for message to arrive")
            message = await websocket.recv()
            with global_queue_lock:
                global_queue.put(message)
            logging.info(f"Received temperature data: {message}")
            response = f"Received: {message}"
            await websocket.send(response)
    except websockets.ConnectionClosed as e:
        logging.info(f"connection is closed: {str(e)}")


def start_websockets_servers():
    collector_server = websockets.serve(handle_websocket, "localhost", COLLECTOR_SERVER_PORT, ping_timeout=None)
    asyncio.get_event_loop().run_until_complete(collector_server)
    asyncio.get_event_loop().run_forever()


# Start a separate thread for each continent to send data
continent_threads = []
for continent in continents:
    thread = threading.Thread(target=continent.send_data)
    thread.daemon = True
    thread.start()
    continent_threads.append(thread)


# Start a separate thread to transfer data from global queue to continent queues
def transfer_data():
    while True:
        with global_queue_lock:
            if not global_queue.empty():
                data = global_queue.get()
                for continent in continents:

                    if data_contains_location(data, continent.name):
                        with continent.queue_lock:
                            continent.queue.put(data)
                        logging.info(f"Transferred data to {continent.name} queue")
        time.sleep(1)


def data_contains_location(data, continent):
    parsed_data = json.loads(data)
    return parsed_data.get('location').get('continent') == continent


transfer_thread = threading.Thread(target=transfer_data)
transfer_thread.daemon = True
transfer_thread.start()


start_websockets_servers()


