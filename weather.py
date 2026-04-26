import requests
from cachetools import cached, TTLCache
from config import OPENWEATHER_KEY
weather_now = TTLCache(maxsize=10, ttl=600)

@cached(weather_now)
def get_weather_now():
    response = requests.post(
        "https://api.openweathermap.org/data/2.5/weather",
        params = {
            "q": "Vladivostok",
            "appid": OPENWEATHER_KEY,
            "units": "metric",
            "lang": "ru"
        },
    )
    data = response.json()
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    weather_description = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    return (f'Сейчас на улице {temperature:.0f}°C, по ощущениям {feels_like:.0f}°C, '
            f'{weather_description}, ветер {wind_speed:.1f} м/с. Влажность {humidity}%')

get_weather_now()