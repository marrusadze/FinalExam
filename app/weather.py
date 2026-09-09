import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather_for_location(location):
    """Return a small dict describing current weather for `location`,
    or None if it can't be fetched (no API key configured, network error,
    city not found, etc.). Never raises.
    """
    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    if not api_key:
        logger.info("Weather lookup skipped for %r: no OPENWEATHER_API_KEY configured.", location)
        return None

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={
                "q": location,
                "appid": api_key,
                "units": "metric",
                "lang": "ka",
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            "humidity": data["main"]["humidity"],
            "city_name": data.get("name", location),
        }
    except requests.exceptions.RequestException as exc:
        logger.error("API request error while fetching weather for %r: %s", location, exc)
        return None
    except (KeyError, ValueError, IndexError) as exc:
        logger.error("API request error: unexpected weather payload for %r: %s", location, exc)
        return None
