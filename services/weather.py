from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import requests
from flask import current_app
from requests.exceptions import RequestException


class WeatherService:
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),  
        wait=wait_exponential(multiplier=1, min=2, max=10), 
        retry=retry_if_exception_type(RequestException),
        reraise=True,  
    )
    def _call_weather_api(location, days):
        response = requests.get(
            "https://api.weatherapi.com/v1/forecast.json",
            params={
                "key": current_app.config["WEATHER_API_KEY"],
                "q": location,
                "days": days,
                "aqi": "no",
                "alerts": "no",
            },
            timeout=10,  
        )
        response.raise_for_status()  
        return response.json()

    @staticmethod
    def get_forecast(location, days=3):
        try:
            return WeatherService._call_weather_api(location, days)
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"Weather API HTTP Error: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"Weather API Request failed after retries: {str(e)}"
            )
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected weather API error: {str(e)}")
            return None
