from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import get_database
from app.model import get_risk_recommendation, model
from app.schemas import HistoryItem, PredictionResponse

router = APIRouter(tags=["prediction"])


@router.get("/predict", response_model=PredictionResponse)
async def predict(
    temperature: float = Query(..., description="Temperature in Celsius"),
    humidity: float = Query(..., description="Relative humidity percentage"),
    aqi: float = Query(..., description="Air Quality Index"),
    lat: float | None = Query(default=None, description="Latitude for the selected location"),
    lon: float | None = Query(default=None, description="Longitude for the selected location"),
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    prediction = model.predict(temperature=temperature, humidity=humidity, aqi=aqi)
    location = f"{lat:.4f}, {lon:.4f}" if lat is not None and lon is not None else "Unknown location"
    record = {
        "user_id": current_user["_id"],
        "location": location,
        "temperature": temperature,
        "humidity": humidity,
        "aqi": aqi,
        "risk": prediction.risk_level,
        "risk_level": prediction.risk_level,
        "disease": prediction.disease,
        "confidence": prediction.confidence,
        "recommendation": prediction.recommendation,
        "explanation": prediction.explanation,
        "alert": prediction.alert,
        "feature_score": prediction.feature_score,
        "created_at": datetime.now(timezone.utc),
    }
    await db.predictions.insert_one(record)
    return PredictionResponse(
        risk=prediction.risk_level,
        risk_level=prediction.risk_level,
        disease=prediction.disease,
        explanation=prediction.explanation,
        alert=prediction.alert,
        confidence=prediction.confidence,
        recommendation=f"{prediction.recommendation} {get_risk_recommendation(prediction.risk_level)}",
        inputs={"temperature": temperature, "humidity": humidity, "aqi": aqi},
        feature_score=prediction.feature_score,
        location=location,
    )


@router.get("/history", response_model=list[HistoryItem])
async def prediction_history(current_user=Depends(get_current_user), db=Depends(get_database)):
    cursor = db.predictions.find({"user_id": current_user["_id"]}).sort("created_at", -1).limit(50)
    items: list[HistoryItem] = []
    async for item in cursor:
        items.append(
            HistoryItem(
                id=str(item["_id"]),
                location=item.get("location", "Unknown location"),
                risk=item.get("risk", item["risk_level"]),
                risk_level=item["risk_level"],
                disease=item.get("disease", "None"),
                confidence=float(item["confidence"]),
                recommendation=item["recommendation"],
                temperature=float(item["temperature"]),
                humidity=float(item["humidity"]),
                aqi=float(item["aqi"]),
                created_at=item["created_at"],
            )
        )
    return items
