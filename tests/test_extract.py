from unittest.mock import patch

from src.extract import fetch_weather


def test_fetch_weather_invalid_city():
    result = fetch_weather("", 31.5204, 74.3584)

    assert result is None

def test_fetch_weather_success():
    fake_api_response = {
        "current": {
            "time": "2026-11-10T15:00",
            "temperature_2m": 27.5,
            "weather_code": 1
        },
        "current_units": {
            "temperature_2m": "°C"
        }
    }

    with patch("src.extract.requests.get") as mock_get:

        mock_get.return_value.json.return_value = fake_api_response

        result = fetch_weather(
            "Lahore",
            31.5204,
            74.3584
        )

        assert result is not None

        weather_record, raw_weather_data = result

        assert weather_record["city"] == "Lahore"
        assert weather_record["temperature"] == 27.5
        assert weather_record["temperature_unit"] == "°C"
        assert weather_record["weather_code"] == 1
        assert weather_record["weather_description"] == "Mainly clear"

        assert raw_weather_data == fake_api_response

        mock_get.assert_called_once()

