from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Hard-coded weather data
weather_data = {
    "USA": {
        "New York": {"temperature": 30},
        "Los Angeles": {"temperature": 25},
        "Chicago": {"temperature": 18}
    },
    "UK": {
        "London": {"temperature": 15},
        "Manchester": {"temperature": 13},
        "Birmingham": {"temperature": 14}
    },
    "Canada": {
        "Toronto": {"temperature": 20},
        "Vancouver": {"temperature": 22},
        "Montreal": {"temperature": 17}
    },
    "Australia": {
        "Sydney": {"temperature": 25},
        "Melbourne": {"temperature": 23},
        "Brisbane": {"temperature": 28}
    },
    "Germany": {
        "Berlin": {"temperature": 12},
        "Munich": {"temperature": 10},
        "Hamburg": {"temperature": 11}
    }
}

# Sample weather data for latitude and longitude inputs
latitude_longitude_data = {
    "40.7128,-74.0060": {"temperature": 20},  # New York
    "34.0522,-118.2437": {"temperature": 25},  # Los Angeles
    "41.8781,-87.6298": {"temperature": 18},  # Chicago
    "51.5074,-0.1278": {"temperature": 15},  # London
    "53.4830,-2.2446": {"temperature": 13},  # Manchester
    "52.4862,-1.8904": {"temperature": 14}  # Birmingham
}


@app.route('/api', methods=['GET'])
def get_weather():
    # Extracting parameters from the request
    country = request.args.get('country')
    city = request.args.get('city')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    
    # Checking if country and city are provided
    if country and city:
        # Checking if the provided country and city are in the weather data
        if country in weather_data and city in weather_data[country]:
            # Returning the weather data for the provided country and city
            return jsonify(weather_data[country][city])
    # Checking if latitude and longitude are provided
    elif latitude and longitude:
        # Creating a key for latitude and longitude
        lat_long_key = f"{latitude},{longitude}"
        # Checking if the key exists in the latitude_longitude_data
        if lat_long_key in latitude_longitude_data:
            # Returning the weather data for the provided latitude and longitude
            return jsonify(latitude_longitude_data[lat_long_key])
    
    # Returning an error response if the input is invalid
    return jsonify({"error": "Invalid input"}), 400



if __name__ == '__main__':
    app.run(debug=True)
