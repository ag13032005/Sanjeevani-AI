from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import get_database
from app.schemas import IotLiveResponse
from app.services_iot import fetch_thingspeak_data, ollama_analysis, predict_from_vitals, validate_iot_vitals

router = APIRouter(tags=["iot"])


@router.get("/iot-live", response_model=IotLiveResponse)
async def get_iot_live(current_user=Depends(get_current_user), db=Depends(get_database)):
    vitals, fetch_warnings, source_meta = await fetch_thingspeak_data()
    cleaned_vitals, validation_warnings = validate_iot_vitals(vitals)
    warnings = [*fetch_warnings, *validation_warnings]

    prediction = predict_from_vitals(cleaned_vitals)
    ai_analysis = await ollama_analysis(cleaned_vitals, prediction, warnings)

    record = {
        "user_id": current_user["_id"],
        "timestamp": datetime.now(timezone.utc),
        "vitals": vitals,
        "cleaned_vitals": cleaned_vitals,
        "prediction": prediction,
        "ai_analysis": ai_analysis,
        "warnings": warnings,
        "source": source_meta,
    }
    await db.iot_records.insert_one(record)

    return IotLiveResponse(
        timestamp=record["timestamp"],
        vitals=vitals,
        cleaned_vitals=cleaned_vitals,
        warnings=warnings,
        prediction=prediction,
        explanation=ai_analysis["explanation"],
        alerts=[*warnings, *ai_analysis.get("alerts", [])][:8],
        recommendations=ai_analysis.get("recommendations", []),
    )
