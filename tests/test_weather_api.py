import pytest

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_weather_valid_city():
    """Test that enfpoint returns data for a valid city name"""

    response = client.get("/weather?city=London")

    assert response.status_code == 200
    data = response.json()

    assert "city" in data
    assert "temp_avg_c" in data
    assert "conditions" in data
    print("Test passed")


def test_weather_invalid_characters():
    """Test that invalid characters in city parameter are rejected"""

    response = client.get("/weather?city=1234")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    print("Test passed")


def test_weather_empty_query():
    """Test that empty city parameter is rejected"""

    response = client.get("/weather?city=")

    assert response.status_code == 422
    print("Test passed")

def test_weather_no_query():
    """Test that providing no query parameter returns validation error"""
    response = client.get("/weather")

    assert response.status_code == 422
    print("Test passed")

# def test_weather_rate_limiting():
#     """Test that rate limiting works when Redis is up"""

#     for i in range(6):
#         response = client.get("/weather?city=London")

#         if i < 4:
#             assert response.status_code == 200
#             print(f"Request {i+1} allowed")
#         else:
#             assert response.status_code == 429
#             print(f"Request {i+1} blocked")

def test_health_check():
    """Test that health check endpoint returns status"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data
    assert "dependencies" in data
    
    # Check dependencies structure
    assert "redis" in data["dependencies"]
    assert "rate_limiting" in data["dependencies"]
    
    # Check redis has status
    assert "status" in data["dependencies"]["redis"]
    
    # Service name should be correct
    assert data["service"] == "weather-api"
    
    print("✅ Health check test passed")