# Weather API

REST API that provides current weather information with intelligent caching, rate limiting, and comprehensive monitoring.

## Features

- **Real-time Weather Data** - Fetches weather from Visual Crossing API
- **Smart Caching** - Redis-based caching with 10-minute TTL
- **Rate Limiting** - 5 requests per 60 seconds per user
- **Fail-Safe Design** - Continues operating when Redis is unavailable
- **Health Monitoring** - Built-in health check endpoint
- **Performance Tracking** - Request duration logging
- **Structured Logging** - File-based logs with automatic rotation (10MB)
- **Comprehensive Testing** - 78% test coverage with pytest

## Tech Stack

- **Framework**: FastAPI
- **Cache**: Redis
- **Testing**: pytest, pytest-cov
- **Language**: Python 3.10+
- **External API**: Visual Crossing Weather

## Prerequisites

- Python 3.10 or higher
- Docker (for Redis)
- Visual Crossing API key ([Get free key](https://www.visualcrossing.com/))

## Installation

### 1. Clone and setup
```bash
git clone https://github.com/WasifAkram1997/Weather-API.git
cd weather-api
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `.env` file:
```env
WEATHER_API_KEY=your_api_key_here
WEATHER_BASE_URL=https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/
REDIS_URL=redis://localhost:6379
WEATHER_DATA_TTL=600
```

### 4. Start Redis
```bash
docker run -d --name weather-redis -p 6379:6379 redis:latest
```

### 5. Run the application
```bash
uvicorn src.main:app --reload
```

API available at: `http://localhost:8000`

## API Endpoints

### Get Weather
```http
GET /weather?city={city_name}
```

**Example:**
```bash
curl "http://localhost:8000/weather?city=London"
```

**Response:**
```json
{
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
```

**Error Responses:**
- `400` - Invalid city name
- `404` - City not found
- `429` - Rate limit exceeded
- `503` - Weather service unavailable

### Health Check
```http
GET /health
```

**Response:**
```json
{
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
```

## Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

Run tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

View coverage report:
```bash
# Windows
start htmlcov/index.html
# Mac
open htmlcov/index.html
```

## Project Structure
```
weather-api/
├── src/
│   ├── main.py                 # FastAPI app & routes
│   ├── logger.py               # Logging configuration
│   ├── redis_client.py         # Redis connection
│   ├── exception_handlers.py   # Error handlers
│   ├── exceptions.py           # Custom exceptions
│   └── services/
│       └── weather_client.py   # Weather API client
├── tests/
│   └── test_weather_api.py     # API tests
├── logs/                       # App logs (auto-created)
├── .env                        # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Architecture

### Fail-Safe Pattern
- Continues serving requests when Redis is down
- Rate limiting automatically disabled during Redis outage
- Cache operations degrade gracefully

### Caching Strategy
- 10-minute TTL for weather data
- Cache key format: `weather:{city_lowercase}`
- Reduces API calls and improves response time

### Logging
- **Development**: DEBUG level to console
- **Production**: WARNING level to file
- Automatic log rotation at 10MB

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `WEATHER_API_KEY` | Visual Crossing API key | Required |
| `WEATHER_BASE_URL` | Weather API URL | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `WEATHER_DATA_TTL` | Cache duration (seconds) | `600` |
| `ENV` | Environment (development/production) | `development` |

## Monitoring

### Health Checks
Use `/health` endpoint for:
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Monitoring system integration

### Performance Logs
All requests logged with duration:
```
2026-01-17 18:15:34 - Request: GET /weather completed in 0.8234s with status 200
```

## Author

Gazi Wasif Akram(https://github.com/WasifAkram1997)

## Acknowledgments

- Weather data: [Visual Crossing](https://www.visualcrossing.com/)
- Framework: [FastAPI](https://fastapi.tiangolo.com/)