from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions import WeatherProviderError, WetaherNotFoundError, InvalidInputError

def register_exception_handlers(app):
    @app.exception_handler(WeatherProviderError)
    async def weather_provider_error_handler(request: Request, exc: WeatherProviderError):
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc)}
        )

    @app.exception_handler(WetaherNotFoundError)
    async def weather_not_found_error_handler(request: Request, exc: WetaherNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )
    @app.exception_handler(InvalidInputError)
    async def invalid_input_error_handler(request: Request, exc: InvalidInputError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )