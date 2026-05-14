from fastapi import APIRouter, HTTPException, Query

from app.schemas import AQIResponse, WeatherResponse
from app.services_openweather import openweather_service

router = APIRouter(tags=["weather"])


@router.get("/weather", response_model=WeatherResponse)
async def weather(lat: float = Query(...), lon: float = Query(...)):
    try:
        return await openweather_service.get_weather(lat, lon)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Unable to fetch weather data: {exc}") from exc


@router.get("/aqi", response_model=AQIResponse)
async def aqi(lat: float = Query(...), lon: float = Query(...)):
    try:
        return await openweather_service.get_aqi(lat, lon)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Unable to fetch AQI data: {exc}") from exc
