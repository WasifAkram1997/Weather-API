from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class WeatherResponse(BaseModel):
    """Response model for weather data"""
    
    version: str = Field(..., description="API version")
    city: str = Field(..., description="City name")
    date: str = Field(..., description="Date of weather data (YYYY-MM-DD)")
    timezone: str = Field(..., description="Timezone of the city")
    summary: Optional[str] = Field(None, description="Weather summary")
    conditions: Optional[str] = Field(None, description="Current conditions")
    
    # Temperature
    temp_avg_c: Optional[float] = Field(None, description="Average temperature in Celsius")
    temp_max_c: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    temp_min_c: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    feels_like_c: Optional[float] = Field(None, description="Feels like temperature in Celsius")
    
    # Precipitation
    precip_mm: Optional[float] = Field(None, description="Precipitation in millimeters")
    precip_prob_percent: Optional[float] = Field(None, description="Precipitation probability percentage")
    
    # Wind
    wind_speed_kmh: Optional[float] = Field(None, description="Wind speed in km/h")
    wind_gust_kmh: Optional[float] = Field(None, description="Wind gust speed in km/h")
    
    # Sun
    sunrise: Optional[str] = Field(None, description="Sunrise time (HH:MM:SS)")
    sunset: Optional[str] = Field(None, description="Sunset time (HH:MM:SS)")
    
    model_config = ConfigDict(json_schema_extra = {
            "example": {
                "version": "v1",
                "city": "London",
                "date": "2026-01-17",
                "timezone": "Europe/London",
                "summary": "Partly cloudy throughout the day",
                "conditions": "Partially cloudy",
                "temp_avg_c": 7.9,
                "temp_max_c": 10.0,
                "temp_min_c": 3.8,
                "feels_like_c": 5.4,
                "precip_mm": 23.0,
                "precip_prob_percent": 100.0,
                "wind_speed_kmh": 23.4,
                "wind_gust_kmh": 54.4,
                "sunrise": "07:59:34",
                "sunset": "16:20:49"
            }
        })



class HealthDependency(BaseModel):
    """Model for health check dependency status"""
    status: str = Field(..., description="Status of the dependency")
    detail: Optional[str] = Field(None, description="Additional details")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(..., description="Overall service status (ok/degraded)")
    timestamp: str = Field(..., description="Current timestamp (ISO format)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    dependencies: dict[str, HealthDependency] = Field(..., description="Status of dependencies")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "timestamp": "2026-01-17T18:00:00",
                "service": "weather-api",
                "version": "1.0.0",
                "dependencies": {
                    "redis": {
                        "status": "healthy",
                        "detail": "connected and responsive"
                    },
                    "rate_limiting": {
                        "status": "enabled"
                    }
                }
            }
        }
    )
            

class ErrorResponse(BaseModel):
    """Response model for error responses"""
    detail: str = Field(..., description="Error message")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "City name contains invalid characters"
            }
        }
    )
# API Response Documentation
WEATHER_RESPONSES = {
    400: {
        "model": ErrorResponse,
        "description": "Invalid input - city name contains invalid characters or is empty",
        "content": {
            "application/json": {
                "example": {"detail": "City contains invalid characters"}
            }
        }
    },
    404: {
        "model": ErrorResponse,
        "description": "City not found in weather database",
        "content": {
            "application/json": {
                "example": {"detail": "InvalidCity123 not found"}
            }
        }
    },
    429: {
        "model": ErrorResponse,
        "description": "Rate limit exceeded (5 requests per 60 seconds)",
        "content": {
            "application/json": {
                "example": {"detail": "Too Many Requests"}
            }
        }
    },
    503: {
        "model": ErrorResponse,
        "description": "Weather service unavailable or returned an error",
        "content": {
            "application/json": {
                "example": {"detail": "Weather api error with status code: 500"}
            }
        }
    }
}