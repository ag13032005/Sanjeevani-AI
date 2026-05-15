from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from app.config import get_settings


DEFAULT_VITALS = {
    "temperature": 37.1,
    "bp": "122/81",
    "spo2": 97.0,
    "heart_rate": 84.0,
    "ecg": "Normal Sinus Rhythm",
}


def _to_float(value) -> float | None:
    try:
        if value is None:
            return None
        parsed = float(str(value).strip())
        if parsed != parsed:  # NaN check
            return None
        return parsed
    except (TypeError, ValueError):
        return None


def _to_ecg(value) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip()
    return text or "Unknown"


def _parse_bp(bp_value: str | float | int | None) -> tuple[int | None, int | None, bool]:
    if bp_value is None:
        return None, None, False

    text = str(bp_value).strip()
    if "/" in text:
        parts = [part.strip() for part in text.split("/") if part.strip()]
        if len(parts) >= 2:
            first = _to_float(parts[0])
            second = _to_float(parts[1])
            if first is not None and second is not None:
                return int(round(first)), int(round(second)), False

    single = _to_float(text)
    if single is None:
        return None, None, False
    systolic = int(round(single))
    estimated_diastolic = int(round(systolic * 0.67))
    return systolic, estimated_diastolic, True


async def fetch_thingspeak_data() -> tuple[dict, list[str], dict]:
    settings = get_settings()
    warnings: list[str] = []

    if not settings.thingspeak_channel_id:
        warnings.append("ThingSpeak channel is not configured; using fallback sample vitals.")
        mapped = dict(DEFAULT_VITALS)
        mapped["heart_rate"] = float(mapped["heart_rate"])
        return mapped, warnings, {"source": "fallback", "feed": {}}

    query_params: dict[str, str] = {}
    if settings.thingspeak_read_api_key:
        query_params["api_key"] = settings.thingspeak_read_api_key

    url = f"{settings.thingspeak_base_url}/channels/{settings.thingspeak_channel_id}/feeds/last.json"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=query_params)
        response.raise_for_status()
        feed = response.json()

    mapped = {
        "temperature": _to_float(feed.get("field1")),
        "bp": feed.get("field2"),
        "spo2": _to_float(feed.get("field3")),
        "heart_rate": _to_float(feed.get("field4")),
        "ecg": _to_ecg(feed.get("field5")),
    }

    if mapped["temperature"] is None:
        warnings.append("Temperature sensor value missing or invalid.")
    if mapped["bp"] in (None, "", "0", 0, "0/0"):
        warnings.append("Blood pressure feed is missing or invalid.")
    if mapped["spo2"] is None:
        warnings.append("SpO2 sensor value missing or invalid.")
    if mapped["heart_rate"] is None:
        warnings.append("Heart rate sensor value missing or invalid.")

    return mapped, warnings, {"source": "thingspeak", "feed": feed}


def validate_iot_vitals(vitals: dict) -> tuple[dict, list[str]]:
    cleaned = {
        "temperature": vitals.get("temperature"),
        "bp": vitals.get("bp"),
        "spo2": vitals.get("spo2"),
        "heart_rate": vitals.get("heart_rate"),
        "ecg": vitals.get("ecg", "Unknown"),
        "bp_systolic": None,
        "bp_diastolic": None,
    }
    warnings: list[str] = []

    systolic, diastolic, is_estimated = _parse_bp(vitals.get("bp"))
    if systolic is not None:
        cleaned["bp_systolic"] = systolic
        cleaned["bp_diastolic"] = diastolic
        if is_estimated:
            warnings.append("Blood pressure contains one value; diastolic was estimated.")
        if systolic == 0:
            warnings.append("Blood pressure reading is invalid (0).")
    else:
        warnings.append("Blood pressure reading could not be parsed.")

    spo2 = _to_float(vitals.get("spo2"))
    if spo2 is not None:
        cleaned["spo2"] = spo2
        if spo2 > 100:
            warnings.append("Sensor Error: SpO2 above 100.")
    else:
        warnings.append("SpO2 reading is invalid.")

    temperature = _to_float(vitals.get("temperature"))
    if temperature is not None:
        cleaned["temperature"] = temperature
        if temperature < 30 or temperature > 45:
            warnings.append("Suspicious temperature reading detected.")
        if temperature < 35:
            warnings.append("Hypothermia risk detected.")
    else:
        warnings.append("Temperature reading is invalid.")

    heart_rate = _to_float(vitals.get("heart_rate"))
    if heart_rate is not None:
        cleaned["heart_rate"] = heart_rate
        if heart_rate < 40 or heart_rate > 180:
            warnings.append("Abnormal heart rate range detected.")
        if heart_rate > 120:
            warnings.append("Tachycardia detected.")
    else:
        warnings.append("Heart rate reading is invalid.")

    if cleaned["bp_systolic"] is not None and cleaned["bp_diastolic"] is not None:
        if cleaned["bp_systolic"] > 180 or cleaned["bp_diastolic"] > 120:
            warnings.append("Critical Condition: Hypertensive Crisis")

    return cleaned, warnings


def predict_from_vitals(cleaned_vitals: dict) -> dict:
    score = 0

    temperature = _to_float(cleaned_vitals.get("temperature")) or 0
    spo2 = _to_float(cleaned_vitals.get("spo2")) or 0
    heart_rate = _to_float(cleaned_vitals.get("heart_rate")) or 0
    bp_systolic = cleaned_vitals.get("bp_systolic") or 0
    bp_diastolic = cleaned_vitals.get("bp_diastolic") or 0

    if temperature >= 38.5:
        score += 2
    elif temperature >= 37.5:
        score += 1

    if spo2 < 92:
        score += 3
    elif spo2 < 95:
        score += 2

    if heart_rate > 120:
        score += 2
    elif heart_rate > 100:
        score += 1

    if bp_systolic > 180 or bp_diastolic > 120:
        score += 3
    elif bp_systolic > 140 or bp_diastolic > 90:
        score += 1

    if score >= 7:
        risk = "High"
        confidence = 0.88
    elif score >= 4:
        risk = "Medium"
        confidence = 0.68
    else:
        risk = "Low"
        confidence = 0.43

    if spo2 < 92:
        disease = "Respiratory"
    elif temperature >= 38.5 and bp_systolic < 110:
        disease = "Dengue"
    elif temperature >= 37.5:
        disease = "Flu"
    else:
        disease = "Normal"

    return {
        "risk": risk,
        "disease": disease,
        "confidence": confidence,
    }


def _extract_alerts(text: str) -> list[str]:
    alerts: list[str] = []
    for line in text.splitlines():
        stripped = line.strip(" -\t")
        if not stripped:
            continue
        if ":" in stripped:
            section, value = stripped.split(":", 1)
            if section.lower().strip() in {"alerts", "alert"}:
                alerts.extend(item.strip() for item in value.split(";") if item.strip())
                continue
        lowered = stripped.lower()
        if any(keyword in lowered for keyword in ["alert", "critical", "abnormal", "risk", "urgent", "warning"]):
            alerts.append(stripped)
    return alerts[:6]


def _extract_recommendations(text: str) -> list[str]:
    recommendations: list[str] = []
    for line in text.splitlines():
        stripped = line.strip(" -\t")
        if not stripped:
            continue
        if ":" in stripped:
            section, value = stripped.split(":", 1)
            if section.lower().strip() in {"recommendations", "recommendation"}:
                recommendations.extend(item.strip() for item in value.split(";") if item.strip())
                continue
        if "recommend" in stripped.lower():
            recommendations.append(stripped)
    return recommendations[:3]


async def ollama_analysis(cleaned_vitals: dict, prediction: dict, warnings: list[str]) -> dict:
    settings = get_settings()
    prompt_payload = {
        "vitals": cleaned_vitals,
        "prediction": prediction,
        "warnings": warnings,
    }

    prompt = (
        "Analyze these patient vitals and explain risks, abnormalities, and recommendations. "
        "Return concise plain text with sections: Explanation, Alerts, Recommendations.\n\n"
        f"Input:\n{json.dumps(prompt_payload, indent=2)}"
    )

    body = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(settings.ollama_generate_url, json=body)
            response.raise_for_status()
            output = response.json().get("response", "").strip()
    except Exception:
        output = (
            "Explanation: Vitals indicate active monitoring need.\n"
            "Alerts: Review oxygen saturation, blood pressure, and heart rate against trends.\n"
            "Recommendations: Re-check sensors, repeat readings, and seek clinician review if symptoms persist."
        )

    alerts = _extract_alerts(output)
    recommendations = _extract_recommendations(output) or ["Repeat measurements and consult a clinician if abnormal patterns continue."]

    return {
        "explanation": output,
        "alerts": alerts,
        "recommendations": recommendations,
        "generated_at": datetime.now(timezone.utc),
    }
