from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings


class OpenWeatherService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _fetch(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_weather(self, lat: float, lon: float) -> dict[str, Any]:
        if not self.settings.openweather_api_key:
            return self._mock_weather(lat, lon)
        url = f"{self.settings.openweather_base_url}/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.settings.openweather_api_key,
            "units": "metric",
        }
        payload = await self._fetch(url, params)
        return {
            "temperature": float(payload["main"]["temp"]),
            "humidity": float(payload["main"]["humidity"]),
            "description": payload["weather"][0]["description"],
            "wind_speed": float(payload.get("wind", {}).get("speed", 0.0)),
            "source": "openweather",
        }

    async def get_aqi(self, lat: float, lon: float) -> dict[str, Any]:
        if not self.settings.openweather_api_key:
            return self._mock_aqi(lat, lon)
        url = f"{self.settings.openweather_base_url}/data/2.5/air_pollution"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.settings.openweather_api_key,
        }
        payload = await self._fetch(url, params)
        aqi_value = int(payload["list"][0]["main"]["aqi"])
        aqi_map = {1: (20, "Good"), 2: (60, "Fair"), 3: (110, "Moderate"), 4: (160, "Poor"), 5: (220, "Very Poor")}
        mapped_aqi, category = aqi_map.get(aqi_value, (110, "Moderate"))
        return {"aqi": mapped_aqi, "category": category, "source": "openweather"}

    def _mock_weather(self, lat: float, lon: float) -> dict[str, Any]:
        base_temp = 24 + ((lat + lon) % 7)
        humidity = 60 + ((lat - lon) % 20)
        return {
            "temperature": round(base_temp, 1),
            "humidity": round(min(95, max(35, humidity)), 1),
            "description": "simulated local conditions",
            "wind_speed": 3.5,
            "source": "mock",
        }

    def _mock_aqi(self, lat: float, lon: float) -> dict[str, Any]:
        aqi = int(75 + abs(lat * lon) % 120)
        category = "Good" if aqi < 50 else "Moderate" if aqi < 100 else "Poor"
        return {"aqi": aqi, "category": category, "source": "mock"}


openweather_service = OpenWeatherService()
