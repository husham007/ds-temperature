import threading

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import logging
import json
from queue import Queue

app = Flask(__name__)
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler('continent_api.log'),
                        logging.StreamHandler()
                    ])

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['continent']
continent = db['continent']

WEBSOCKET_SERVER_PORT = 8008


class DatabaseManager:
    @staticmethod
    def post(data):
        try:
            continent.update_one(
                {'continent': data.get('continent'), 'country': data.get('country'), 'name': data.get('name'),
                 'latitude': data.get('latitude'), 'longitude': data.get('longitude')}, {
                    '$set': data}, upsert=True)
            logging.info("Data inserted into MongoDB")
        except Exception as e:
            logging.error(f"Error inserting data into MongoDB: {e}")

    @staticmethod
    def get_by_location(_continent, country, location):
        try:
            data = continent.find_one({
                'continent': _continent,
                'country': country,
                'name': location
            })
            if data:
                logging.info(f"Data found {data}")
                return {'temperature': data.get('temperature'), 'name': data.get('name'), 'country': data.get('country')}
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving data from MongoDB: {e}")
            return None

    @staticmethod
    def get_by_latitude_longitude(latitude, longitude):
        try:
            data = continent.find_one({
                'latitude': int(latitude),
                'longitude': int(longitude)
            })
            if data:
                logging.info(f"Data found {data}")
                return {'temperature': data.get('temperature'), 'name': data.get('name'), 'country': data.get('country')}
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving data from MongoDB: {e}")
            return None


# Queue to store incoming messages
message_queue = Queue()


# SocketIO event handlers
@socketio.on('connect', namespace='/continent')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/continent')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message', namespace='/continent')
def handle_message(message):
    logging.info(f"message arrived: {message}")
    message_queue.put(message)
    emit('response', {'data': 'Message received'}, broadcast=True)


def process_queue():
    logging.info(f"Waiting to receive messages in the queue")
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            data = json.loads(message)
            # Parse continent, country, location, latitude, longitude, temperature from message
            location = data.get('location')
            _continent = location.get('continent')
            country = location.get('country')
            name = location.get('name')
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            temperature = data.get('value')

            # Save parsed message into MongoDB
            DatabaseManager.post({'continent': _continent, 'country': country, 'name': name, 'latitude': latitude,
                                  'longitude': longitude, 'temperature': temperature})


process_queue_thread = threading.Thread(target=process_queue)
process_queue_thread.daemon = True
process_queue_thread.start()


@app.route('/')
def index():
    return 'Welcome to continent_api'


@app.route('/temperature', methods=['GET'])
def get_temperature():
    _continent = request.args.get('continent')
    country = request.args.get('country')
    location = request.args.get('name')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if _continent and country and location:
        data = DatabaseManager.get_by_location(_continent, country, location)
        if data is not None:
            return jsonify(data), 200
        else:
            return jsonify({'message': 'Data not found'}), 404
    else:
        return jsonify({'message': 'Please provide continent, country, and location'}), 400


@app.route('/temperature/latlong', methods=['GET'])
def get_temperature_by_lat_long():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    logging.info(f"latitude: {latitude}, longitude: {longitude}")
    if latitude and longitude:
        data = DatabaseManager.get_by_latitude_longitude(latitude, longitude)
        if data is not None:
            return jsonify(data), 200
        else:
            return jsonify({'message': 'Data not found'}), 404
    else:
        return jsonify({'message': 'Please provide latitude and longitude'}), 400


if __name__ == '__main__':
    socketio.run(app)
