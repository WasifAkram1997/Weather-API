import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Query, Request, Response, HTTPException

from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.services.weather_client import fetch_weather
from src.exception_handlers import register_exception_handlers
from src.exceptions import InvalidInputError
from src.redis_client import initialize_redis, close_redis

load_dotenv()

app = FastAPI()

register_exception_handlers(app)

async def safe_rate_limit(request: Request, response: Response):
    """Rate limiter that fails open if Redis is unavailable"""
    
    if not FastAPILimiter.redis:
        # Redis is down, skip rate limiting
        return
    
    try:
        # Apply rate limiting when Redis is available
        limiter = RateLimiter(times=5, seconds=60)
        await limiter(request, response)
    except Exception as e:
        # Only fail open for connection errors, not rate limit errors
        error_message = str(e)
        if "429" in error_message or "Too Many Requests" in error_message:
            # This is a legitimate rate limit - re-raise it
            raise
        # For other errors (Redis connection issues), fail open
        print(f"Rate limiting failed (Redis issue): {e}")
        return


@app.on_event("startup")
async def startup():
    try:
        redis = await initialize_redis()
        await FastAPILimiter.init(redis)
        print("Limiter initialized successfully")
    except Exception as e:
        print(f"Limiter initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    await close_redis()


@app.get("/weather", dependencies=[Depends(safe_rate_limit)])
async def get_weather(city: str = Query(..., min_length=1, max_length=60)):
    city = city.strip()
    if not city:
        raise InvalidInputError("City name cannot be empty or whitespace.")
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s,.'-]+", city):
        raise InvalidInputError("City contains invalid characters.")
    return await fetch_weather(city)