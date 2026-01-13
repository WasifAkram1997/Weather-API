from fastapi import FastAPI
from src.services.weather_client import fetch_weather
from src.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)


@app.get("/weather")
async def get_weather(city: str):
    return await fetch_weather(city)
    # return {"message":  f"Hello {city}. It is expected to be {weather_data['days']['description']} today"}
    # return {"message": weather_data}