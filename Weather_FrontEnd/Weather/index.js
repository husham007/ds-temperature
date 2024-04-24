
// Weather by City/Country Button
document.getElementById('weatherByCityBtn').addEventListener('click', function () {
    document.getElementById('weatherByCityDiv').style.display = 'block';
    document.getElementById('weatherByLatLongDiv').style.display = 'none';
});

// Weather by Latitude/Longitude Button
document.getElementById('weatherByLatLongBtn').addEventListener('click', function () {
    document.getElementById('weatherByCityDiv').style.display = 'none';
    document.getElementById('weatherByLatLongDiv').style.display = 'block';
});

// Weather by City/Country Button
document.getElementById('weatherByCityBtn').addEventListener('click', function() {
    document.getElementById('weatherByCityDiv').classList.remove('fade-out');
    document.getElementById('weatherByCityDiv').classList.add('fade-in');
    
    document.getElementById('weatherByLatLongDiv').classList.remove('fade-in');
    document.getElementById('weatherByLatLongDiv').classList.add('fade-out');
});

// Weather by Latitude/Longitude Button
document.getElementById('weatherByLatLongBtn').addEventListener('click', function() {
    document.getElementById('weatherByCityDiv').classList.remove('fade-in');
    document.getElementById('weatherByCityDiv').classList.add('fade-out');
    
    document.getElementById('weatherByLatLongDiv').classList.remove('fade-out');
    document.getElementById('weatherByLatLongDiv').classList.add('fade-in');
});

function findWeatherContryCity() {
    var country = document.getElementById("country").value;
    var city = document.getElementById("city").value;
    var url = "http://127.0.0.1:4999/request_handler?country=" + country + "&name=" + city;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById("countryValue").innerText = country;
            document.getElementById("cityValue").innerText = city;
            document.getElementById("countryCitytemperatureValue").innerText = data.temperature + "°C";
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
function findWeatherLatLong() {
    var latitude = document.getElementById("latitude").value;
    var longitude = document.getElementById("longitude").value;
    var url = "http://127.0.0.1:4999/request_handler?latitude=" + latitude + "&longitude=" + longitude;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById("latitudeValue").innerText = latitude;
            document.getElementById("longitudeValue").innerText = longitude;
            document.getElementById("latLongtemperatureValue").innerText = data.temperature + "°C";
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
// Function to toggle temperature unit between Celsius and Fahrenheit
function toggleTemperatureUnit() {
    var temperatureElement;
    var temperatureValue;
    var currentUnit;

    // Check if weather by city/country div is displayed
    if (document.getElementById("weatherByCityDiv").style.display === "block") {
        temperatureElement = document.getElementById("countryCitytemperatureValue");
        temperatureValue = parseFloat(temperatureElement.dataset.temperature);
        currentUnit = temperatureElement.dataset.unit;
    } else {
        // If not, weather by latitude/longitude div is displayed
        temperatureElement = document.getElementById("latLongtemperatureValue");
        temperatureValue = parseFloat(temperatureElement.dataset.temperature);
        currentUnit = temperatureElement.dataset.unit;
    }

    var convertedTemperature;
    var newUnit;

    if (currentUnit === "C") {
        // Convert Celsius to Fahrenheit
        convertedTemperature = (temperatureValue * 9 / 5) + 32;
        newUnit = "F";
    } else {
        // Convert Fahrenheit to Celsius
        convertedTemperature = (temperatureValue - 32) * 5 / 9;
        newUnit = "C";
    }

    // Update temperature display with new unit
    if (document.getElementById("weatherByCityDiv").style.display === "block") {
        temperatureElement.innerText = Math.round(convertedTemperature) + "°" + newUnit;
        temperatureElement.dataset.temperature = Math.round(convertedTemperature);
        temperatureElement.dataset.unit = newUnit;
    } else {
        temperatureElement.innerText = Math.round(convertedTemperature) + "°" + newUnit;
        temperatureElement.dataset.temperature = Math.round(convertedTemperature);
        temperatureElement.dataset.unit = newUnit;
    }
}
// Function to fetch weather information for city/country
function findWeatherContryCity() {
    var country = document.getElementById("country").value;
    var city = document.getElementById("city").value;
    var url = "http://127.0.0.1:4999/request_handler?country=" + country + "&name=" + city;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            var toogleBtn = document.getElementById("toggleUnitButton");
            document.getElementById("countryValue").innerText = country;
            document.getElementById("cityValue").innerText = city;
            var temperatureElement = document.getElementById("countryCitytemperatureValue");
            temperatureElement.innerText = data.temperature ? data.temperature + "°C" : "Not available";
            temperatureElement.dataset.temperature = data.temperature || undefined;
            temperatureElement.dataset.unit = data.temperature ? "C" : '';
            document.getElementById("weatherByCityDiv").style.display = "block";
            
            // Call setWeatherIcon to set the weather icon based on the temperature
            data.temperature && setWeatherIcon(data.temperature);
            if (data.temperature){
                toogleBtn.disabled = false;
            }
            else toogleBtn.disabled = true;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to fetch weather information for latitude/longitude
function findWeatherLatLong() {
    var latitude = document.getElementById("latitude").value;
    var longitude = document.getElementById("longitude").value;
    var url = "http://127.0.0.1:4999/request_handler?latitude=" + latitude + "&longitude=" + longitude;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById("latitudeValue").innerText = data.country;
            document.getElementById("longitudeValue").innerText = data.name;
            var temperatureElement = document.getElementById("latLongtemperatureValue");
            temperatureElement.innerText = data.temperature ? data.temperature + "°C" : "Not available";
            temperatureElement.dataset.temperature = data.temperature || undefined;
            temperatureElement.dataset.unit = data.temperature ? "C" : '';
            document.getElementById("weatherByLatLongDiv").style.display = "block";
            
            // Call setWeatherIcon to set the weather icon based on the temperature
            data.temperature && setWeatherIcon(data.temperature);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Add event listeners for toggle buttons
document.getElementById("toggleUnitButton").addEventListener("click", toggleTemperatureUnit);
document.getElementById("toggleUnitButtonLatLong").addEventListener("click", toggleTemperatureUnit);

// Function to set weather icon based on temperature
function setWeatherIcon(temperature) {
    var weatherIconElement;

    // Check if weather by city/country div is displayed
    if (document.getElementById("weatherByCityDiv").style.display === "block") {
        weatherIconElement = document.getElementById("weatherIconCountryCity");
    } else {
        // If not, weather by latitude/longitude div is displayed
        weatherIconElement = document.getElementById("weatherIconLatLong");
    }

    // Set weather icon based on temperature range
    if (temperature > 25) {
        weatherIconElement.style.backgroundImage = "url('hot-weather-icon.png')";
    } else if (temperature > 15) {
        weatherIconElement.style.backgroundImage = "url('moderate-weather-icon.png')";
    } else if (temperature > 0)  {
        weatherIconElement.style.backgroundImage = "url('cold-weather-icon.png')";
    }
    else {
         weatherIconElement.style.backgroundImage = "url('icon-weather-snowheavy.png')";
    }
}