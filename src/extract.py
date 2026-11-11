from datetime import UTC, datetime

import requests

from src.logger import get_logger

logger=get_logger(__name__)


WEATHER_CODE_MAPPING = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    95: "Thunderstorm"
}


CITIES = [
    {"city": "Lahore", "latitude": 31.5204, "longitude": 74.3584},
    {"city": "Karachi", "latitude": 24.8607, "longitude": 67.0011},
    {"city": "Islamabad", "latitude": 33.6844, "longitude": 73.0479}
]


def fetch_weather(city, latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "weather_code"],
        "temperature_unit": "celsius"
    }

    try:
        if not city:
            logger.info("Missing city name")
            return None

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        weather_data = response.json()

        observation_time = weather_data["current"]["time"]
        temperature = weather_data["current"]["temperature_2m"]
        weather_code = weather_data["current"]["weather_code"]
        temperature_unit = weather_data["current_units"]["temperature_2m"]

        if not observation_time:
            logger.warning("Missing observation time for: %s", city)
            return None

        if not isinstance(temperature, (int, float)):
            logger.warning("Invalid temperature for: %s", city)
            return None

        if weather_code is None:
            logger.warning("Invalid weather code for: %s", city)
            return None

        if not temperature_unit:
            logger.warning("Invalid temperature unit for: %s", city)
            return None

        ingestion_timestamp = datetime.now(UTC).isoformat()

        weather_description = WEATHER_CODE_MAPPING.get(
            weather_code, "Unknown"
        )

        weather_record = {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "observation_time": observation_time,
            "ingestion_timestamp": ingestion_timestamp,
            "weather_code": weather_code,
            "weather_description": weather_description
        }

        return weather_record, weather_data

    except requests.exceptions.HTTPError:
        logger.exception("HTTP error for : %s", city)

    except requests.exceptions.ConnectionError:
        logger.exception("Connection error for: %s", city)

    except requests.exceptions.Timeout:
        logger.exception("Timeout error for: %s",city)

    except (KeyError, TypeError, ValueError):
        logger.exception("Invalid API response for: %s",city)

    return None


def fetch_all_weather():
    """Fetch weather for all configured cities."""

    weather_records = []
    weather_upload_records = []

    for city in CITIES:

        result = fetch_weather(
            city["city"],
            city["latitude"],
            city["longitude"]
        )

        if result is None:
            logger.error("Failed to fetch: %s", city["city"])
            continue

        weather_record, raw_weather_data = result

        weather_records.append(weather_record)

        weather_upload_records.append({
            "city": city["city"],
            "data": raw_weather_data
        })

        logger.info("Successfully fetched: %s", city["city"])

    return weather_records, weather_upload_records
