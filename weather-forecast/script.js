const inputBox = document.querySelector('.input-box');
const searchBtn = document.getElementById('searchBtn');
const weather_img = document.querySelector('.weather-img');
const temperature = document.querySelector('.temperature');
const description = document.querySelector('.description');
const humidity = document.getElementById('humidity');
const wind_speed = document.getElementById('wind-speed');
const location_not_found = document.querySelector('.location-not-found');
const weather_body = document.querySelector('.weather-body');
const loading = document.createElement('div');

// Create loading element
loading.className = 'loading';
loading.innerHTML = '<div class="loading-spinner"></div><p>Searching for weather...</p>';
document.querySelector('.container').insertBefore(loading, weather_body);

async function checkWeather(city){
    // Show loading
    loading.style.display = "block";
    location_not_found.style.display = "none";
    weather_body.style.display = "none";

    const api_key = "4c4286de4f6a3794841e570fd8bc4a0b";
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${api_key}`;

    try {
        const response = await fetch(url);
        const weather_data = await response.json();

        if(weather_data.cod === '404'){
            location_not_found.style.display = "flex";
            weather_body.style.display = "none";
            loading.style.display = "none";
            changeBackground('error');
            return;
        }

        console.log("Weather data loaded successfully");
        loading.style.display = "none";
        location_not_found.style.display = "none";
        weather_body.style.display = "flex";
        
        const tempCelsius = Math.round(weather_data.main.temp - 273.15);
        temperature.innerHTML = `${tempCelsius}<sup>°C</sup>`;
        description.innerHTML = `${weather_data.weather[0].description}`;

        humidity.innerHTML = `${weather_data.main.humidity}%`;
        wind_speed.innerHTML = `${weather_data.wind.speed} Km/H`;

        // Update temperature color based on temperature
        updateTemperatureColor(tempCelsius);

        // Change background based on weather condition
        changeBackground(weather_data.weather[0].main.toLowerCase());

        // Update weather image
        updateWeatherImage(weather_data.weather[0].main, weather_data.weather[0].description);

        console.log(weather_data);

    } catch (error) {
        console.error("Error fetching weather data:", error);
        loading.style.display = "none";
        location_not_found.style.display = "flex";
        weather_body.style.display = "none";
        changeBackground('error');
    }
}

function updateWeatherImage(weatherMain, weatherDescription) {
    const weatherCondition = weatherMain.toLowerCase();
    
    switch(weatherCondition){
        case 'clouds':
            if (weatherDescription.toLowerCase().includes('few') || weatherDescription.toLowerCase().includes('scattered')) {
                weather_img.src = "img/partly-cloudy.png";
            } else {
                weather_img.src = "img/cloud.png";
            }
            break;
        case 'clear':
            weather_img.src = "img/clear-sky.png";
            break;
        case 'rain':
            if (weatherDescription.toLowerCase().includes('light') || weatherDescription.toLowerCase().includes('drizzle')) {
                weather_img.src = "img/light-rain.png";
            } else {
                weather_img.src = "img/rain.png";
            }
            break;
        case 'haze':
        case 'mist':
        case 'fog':
            weather_img.src = "img/haze.png";
            break;
        case 'thunderstorm':
            weather_img.src = "img/thunderstorm.png";
            break;
        case 'snow':
            weather_img.src = "img/snow.png";
            break;
        case 'drizzle':
            weather_img.src = "img/drizzle.png";
            break;
        default:
            weather_img.src = "img/cloud.png";
    }
}

function changeBackground(weatherCondition) {
    // Remove all weather background classes
    document.body.className = '';
    
    // Add the appropriate background class
    switch(weatherCondition) {
        case 'clear':
            document.body.classList.add('clear-sky');
            break;
        case 'clouds':
            document.body.classList.add('clouds');
            break;
        case 'rain':
        case 'drizzle':
            document.body.classList.add('rain');
            break;
        case 'snow':
            document.body.classList.add('snow');
            break;
        case 'thunderstorm':
            document.body.classList.add('thunderstorm');
            break;
        case 'mist':
        case 'haze':
        case 'fog':
            document.body.classList.add('mist');
            break;
        case 'error':
            // Keep default background for errors
            break;
        default:
            // Keep default background for unknown conditions
            break;
    }
}

function updateTemperatureColor(temp) {
    // Remove all temperature classes
    temperature.classList.remove('cold', 'moderate', 'warm', 'hot');
    
    // Add appropriate temperature class
    if (temp < 10) {
        temperature.classList.add('cold');
    } else if (temp >= 10 && temp < 20) {
        temperature.classList.add('moderate');
    } else if (temp >= 20 && temp < 30) {
        temperature.classList.add('warm');
    } else {
        temperature.classList.add('hot');
    }
}

// Event listeners
searchBtn.addEventListener('click', ()=>{
    if(inputBox.value.trim() !== '') {
        checkWeather(inputBox.value);
    }
});

inputBox.addEventListener('keypress', (e)=>{
    if(e.key === 'Enter' && inputBox.value.trim() !== '') {
        checkWeather(inputBox.value);
    }
});

// Add some sample cities for quick testing
const sampleCities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney', 'Colombo', 'Mumbai'];

// Function to display sample cities (optional feature)
function showSampleCities() {
    console.log('Try these cities:', sampleCities.join(', '));
}

// Initialize
showSampleCities();

// Add click animation to search button
searchBtn.addEventListener('mousedown', () => {
    searchBtn.style.transform = 'scale(0.95)';
});

searchBtn.addEventListener('mouseup', () => {
    searchBtn.style.transform = 'scale(1)';
});

searchBtn.addEventListener('mouseleave', () => {
    searchBtn.style.transform = 'scale(1)';
});

// Add input validation
inputBox.addEventListener('input', (e) => {
    // Remove any numbers from input (cities don't usually have numbers)
    e.target.value = e.target.value.replace(/[0-9]/g, '');
});