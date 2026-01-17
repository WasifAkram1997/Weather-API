import os
import re
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Query, Request, Response, HTTPException

from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from datetime import datetime

from src.services.weather_client import fetch_weather
from src.exception_handlers import register_exception_handlers
from src.exceptions import InvalidInputError
from src.redis_client import initialize_redis, close_redis, get_redis
from src.logger import setup_logger

load_dotenv()

app = FastAPI()
setup_logger()
logger = logging.getLogger(__name__)

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
        logger.warning(f"Rate limiting failed (Redis issue): {e}")
        return


@app.on_event("startup")
async def startup():
    try:
        redis = await initialize_redis()
        await FastAPILimiter.init(redis)
        logger.info("Limiter initialized successfully")
        

    except Exception as e:
        logger.error(f"Limiter initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    await close_redis()


#Endpoint to check application health
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring. Returns API status and dependency health.
    """
    redis_status = "healthy"
    redis_detail = "connected"
    rate_limit_status = "disabled"
    application_status = "ok"

    try:
        redis =await get_redis()
        await redis.ping()
        redis_status = "healthy"
        redis_detail = "connected and responsive"
        # application_status = "ok"
    except Exception as e:
        redis_status = "unhealthy"
        redis_detail = f"connection failed: {str(e)}"
        application_status = "degraded"

    if FastAPILimiter.redis:   
        try:
            await FastAPILimiter.redis.ping()
            rate_limit_status = "enabled"
            # application_status = "ok"
        except Exception:
            pass

    return{
        "status": application_status,
        "timestamp": datetime.now().isoformat(),
        "service": "weather-api",
        "version": "1.0.0",
        "dependencies": {
            "redis": {
                "status": redis_status,
                "detail": redis_detail
            },
            "rate_limiting":{
                "status": rate_limit_status
            }
        }
    }
    

@app.get("/weather", dependencies=[Depends(safe_rate_limit)])
async def get_weather(city: str = Query(..., min_length=1, max_length=60)):
    city = city.strip()
    if not city:
        raise InvalidInputError("City name cannot be empty or whitespace.")
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s,.'-]+", city):
        raise InvalidInputError("City contains invalid characters.")
    return await fetch_weather(city)