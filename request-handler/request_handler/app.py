import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from geopy.geocoders import Nominatim

def find_country_name(latitude, longitude):
    geolocator = Nominatim(user_agent="DS-PROJECT-LUT")
    location = geolocator.reverse((latitude, longitude), language='en')
    address = location.raw['address']
    country = address.get('country', '')
    return country


app = Flask(__name__)
CORS(app)
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Log to file
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

CONTIENTS = {
    'AF': 'Africa',
    'AS': 'Asia',
    'EU': 'Europe',
    'NA': 'North America',
    'SA': 'South America',
    'OC': 'Oceania',
    'AN': 'Antarctica'
}

SERVERS = {
    'Europe': 'http://localhost:5000',
    'Africa': 'http://localhost:5001',
    'Asia': 'http://localhost:5002',
    'North America': 'http://localhost:5003',
    'South America': 'http://localhost:5004',
    'Oceania': 'http://localhost:5005',
    'Antarctica': 'http://localhost:5006'
}


@app.route('/request_handler', methods=['GET'])
def request_handler():
    try:
        # Receive data from client
        data = request.args
        country = data.get('country')
        name = data.get('name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if country and name:
            # Get continent from country
            country_code = country_name_to_country_alpha2(country)
            continent_code = country_alpha2_to_continent_code(country_code)
            logger.info(f'Continent {continent_code} found')
            if continent_code:
                # Convert continent code to continent name
                continent = CONTIENTS.get(continent_code)
                logger.info(f'Continent {continent} found')
                # Forward request to continent API to get temperature
                continent_api_url = f"{SERVERS.get(continent)}/temperature"
                response = requests.get(continent_api_url, params={'continent': continent, 'country': country, 'name': name})

                if response.status_code == 200:
                    return jsonify(response.json())
                elif response.status_code == 404:
                    return jsonify({'error': response.json().get('message')}), response.status_code
                else:
                    error_msg = f'Failed to get temperature from continent API: {response.status_code}'
                    logger.error(error_msg)
                    return jsonify({'error': error_msg}), 500
            else:
                error_msg = f'Continent not found for country: {country}'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
        elif latitude and longitude:
            country_name = find_country_name(float(latitude), float(longitude))
            logger.info(f'Country {country_name} found')
            country_code = country_name_to_country_alpha2(country_name)
            continent_code = country_alpha2_to_continent_code(country_code)
            logger.info(f'Continent {continent_code} found')
            if continent_code:
                # Convert continent code to continent name
                continent = CONTIENTS.get(continent_code)
                logger.info(f'Continent {continent} found')
                # Forward request to continent API to get temperature
                continent_api_url = f"{SERVERS.get(continent)}/temperature/latlong"
                response = requests.get(continent_api_url,
                                        params={'latitude': int(latitude), 'longitude': int(longitude)})

                if response.status_code == 200:
                    return jsonify(response.json())
                elif response.status_code == 404:
                    return jsonify({'error': response.json().get('message')}), response.status_code
                else:
                    error_msg = f'Failed to get temperature from continent API: {response.status_code}'
                    logger.error(error_msg)
                    return jsonify({'error': error_msg}), 500
            else:
                error_msg = f'Continent not found for country: {country}'
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
        else:
            error_msg = 'country, city, latitude, longitude not given'
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
    except Exception as e:
        error_msg = f'An error occurred: {str(e)}'
        logger.exception(error_msg)
        return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    app.run(port=4999)
