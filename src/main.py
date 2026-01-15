import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Query

from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.services.weather_client import fetch_weather
from src.exception_handlers import register_exception_handlers
from src.exceptions import InvalidInputError

load_dotenv()

app = FastAPI()

register_exception_handlers(app)
REDIS_URL = os.getenv("REDIS_URL")


@app.on_event("startup")
async def startup():
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    await FastAPILimiter.init(redis)


@app.get("/weather", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_weather(city: str = Query(..., min_length=1, max_length=60)):
    city = city.strip()
    if not city:
        raise InvalidInputError("City name cannot be empty or whitespace.")
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s,.'-]+", city):
        raise InvalidInputError("City contains invalid characters.")
    return await fetch_weather(city)
    # return {"message":  f"Hello {city}. It is expected to be {weather_data['days']['description']} today"}
    # return {"message": weather_data}