import os
from dotenv import load_dotenv
import httpx
from src.exceptions import WeatherProviderError, WetaherNotFoundError
from redis.asyncio import Redis
import json



load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_BASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL = int(os.getenv("WEATHER_DATA_TTL", "60"))

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

def _cache_key(city: str) -> str:
    return f"weather:{city.strip().lower()}"


def _to_human_readable(data: dict) -> dict:
    # Visual Crossing data is inside data["message"] in your current output
    msg = data.get("message", data)

    city = msg.get("resolvedAddress") or msg.get("address") or "Unknown"
    timezone = msg.get("timezone")

    days = msg.get("days") or []
    today = days[0] if days else {}

    date = today.get("datetime")
    conditions = today.get("conditions")
    desc = today.get("description") or msg.get("description")

    temp = today.get("temp")
    tempmax = today.get("tempmax")
    tempmin = today.get("tempmin")
    feelslike = today.get("feelslike")

    precip = today.get("precip")
    precipprob = today.get("precipprob")
    preciptype = today.get("preciptype") or []
    snow = today.get("snow")

    windspeed = today.get("windspeed")
    windgust = today.get("windgust")
    winddir = today.get("winddir")

    sunrise = today.get("sunrise")
    sunset = today.get("sunset")

    # current conditions (optional)
    current = msg.get("currentConditions") or {}
    current_time = current.get("datetime")
    current_cond = current.get("conditions")
    current_temp = current.get("temp")
    current_feels = current.get("feelslike")

    return {
        "city": city,
        "date": date,
        "timezone": timezone,
        "summary": desc,
        "conditions": conditions,
        "temperature_c": {
            "average": temp,
            "high": tempmax,
            "low": tempmin,
            "feels_like": feelslike,
        },
        "precipitation": {
            "amount_mm": precip,
            "chance_percent": precipprob,
            "types": preciptype,
            "snow": snow,
        },
        "wind": {
            "speed_kmh": windspeed,
            "gust_kmh": windgust,
            "direction_degrees": winddir,
        },
        "sun": {
            "sunrise": sunrise,
            "sunset": sunset,
        },
        "current": {
            "time": current_time,
            "conditions": current_cond,
            "temp_c": current_temp,
            "feels_like_c": current_feels,
        } if current else None,
    }

async def fetch_weather(city : str) -> dict:
    if not API_KEY:
        raise RuntimeError("Weather api is not set")
    cache_key = _cache_key(city)
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    
    url = f"{BASE_URL}{city}/today"
    params = {
        "unitGroup": "metric",
        "contentType": "json",
        "key": API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
        
        if response.status_code == 404:
            raise WetaherNotFoundError(f"{city} not found")
        if response.status_code >= 400:
            raise WeatherProviderError(f"Weather api error with status code: {response.status_code}")
        
        raw = response.json()
        result = _to_human_readable(raw)
        await redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
        return result
        
    except httpx.TimeoutException:
        raise WeatherProviderError("Weather api timed out")
    except httpx.RequestError as e:
        raise WeatherProviderError(f"Network error: {e}")    

 