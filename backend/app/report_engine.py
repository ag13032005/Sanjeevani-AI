from __future__ import annotations

from datetime import date
from typing import Any


def validate_vitals(vitals: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Validate and normalize patient vitals for the report."""
    corrected_values = dict(vitals)
    warnings: list[str] = []

    spo2 = float(corrected_values.get("spo2", 0))
    temperature = float(corrected_values.get("temperature", 0))
    systolic = int(corrected_values.get("bp_systolic", 0))
    diastolic = int(corrected_values.get("bp_diastolic", 0))
    heart_rate = int(corrected_values.get("heart_rate", 0))

    corrected_values["spo2_status"] = "Normal"
    corrected_values["temperature_status"] = "Normal"
    corrected_values["bp_status"] = "Normal"
    corrected_values["heart_rate_status"] = "Normal"

    if spo2 > 100:
        corrected_values["spo2_status"] = "Sensor Error"
        warnings.append("SpO2 value exceeds physiological limit -> likely sensor error.")

    if temperature < 35:
        corrected_values["temperature_status"] = "Hypothermia"
        warnings.append("Temperature below 35°C -> possible hypothermia.")

    if systolic >= 180 or diastolic >= 120:
        corrected_values["bp_status"] = "Hypertensive Crisis"
        warnings.append("BP above 180/120 -> hypertensive crisis.")

    if heart_rate > 120:
        corrected_values["heart_rate_status"] = "Tachycardia"
        warnings.append("Heart rate above 120 bpm -> tachycardia.")
    elif heart_rate < 50:
        corrected_values["heart_rate_status"] = "Bradycardia"
        warnings.append("Heart rate below 50 bpm -> bradycardia.")

    corrected_values["temperature"] = temperature
    corrected_values["bp_systolic"] = systolic
    corrected_values["bp_diastolic"] = diastolic
    corrected_values["heart_rate"] = heart_rate
    corrected_values["spo2"] = spo2
    corrected_values["bp"] = f"{systolic}/{diastolic}"

    return corrected_values, warnings


def diagnose_report(validated_vitals: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    """Combine simple rule-based logic with a lightweight severity score."""
    heart_rate = int(validated_vitals["heart_rate"])
    systolic = int(validated_vitals["bp_systolic"])
    diastolic = int(validated_vitals["bp_diastolic"])
    temperature = float(validated_vitals["temperature"])
    spo2 = float(validated_vitals["spo2"])

    condition = "Stable"
    severity = "Normal"
    confidence = 88.0

    if validated_vitals.get("spo2_status") == "Sensor Error":
        condition = "Sensor Error"
        severity = "Warning"
        confidence = 98.0
    elif validated_vitals.get("bp_status") == "Hypertensive Crisis":
        condition = "Hypertensive Crisis"
        severity = "Critical"
        confidence = 97.0
    elif validated_vitals.get("heart_rate_status") == "Tachycardia":
        condition = "Tachycardia"
        severity = "High"
        confidence = 93.0
    elif validated_vitals.get("heart_rate_status") == "Bradycardia":
        condition = "Bradycardia"
        severity = "High"
        confidence = 92.0
    elif validated_vitals.get("temperature_status") == "Hypothermia":
        condition = "Hypothermia"
        severity = "High"
        confidence = 91.0
    elif spo2 < 92:
        condition = "Hypoxemia"
        severity = "High"
        confidence = 94.0

    if condition == "Stable" and warnings:
        severity = "Moderate"
        confidence = 84.0
        if temperature >= 37.8 and heart_rate >= 100:
            condition = "Fever with Stress Response"
        elif systolic >= 140 or diastolic >= 90:
            condition = "Elevated Blood Pressure"
        elif spo2 < 95:
            condition = "Mild Oxygen Desaturation"
        else:
            condition = "Needs Clinical Review"

    if severity == "Critical":
        confidence = min(99.0, confidence)
    elif severity == "High":
        confidence = min(95.0, confidence)
    elif severity == "Moderate":
        confidence = min(88.0, confidence)

    if condition == "Stable":
        condition = "No Immediate Concern"
        severity = "Normal"
        confidence = 90.0

    return {
        "condition": condition,
        "severity": severity,
        "confidence": round(confidence, 1),
    }


def build_report(
    patient: dict[str, str],
    vitals: dict[str, Any],
) -> dict[str, Any]:
    validated_vitals, warnings = validate_vitals(vitals)
    diagnosis = diagnose_report(validated_vitals, warnings)

    insights: list[str] = []
    alerts: list[str] = []

    if validated_vitals.get("spo2_status") == "Sensor Error":
        insights.append("SpO2 value exceeds physiological limit -> likely sensor error.")
        alerts.append("Critical warning: SpO2 sensor reading should be rechecked immediately.")

    if validated_vitals.get("temperature_status") == "Hypothermia":
        insights.append("Temperature below 35°C -> hypothermia detected.")
        alerts.append("Patient is at risk of hypothermia.")

    if validated_vitals.get("bp_status") == "Hypertensive Crisis":
        insights.append("BP > 180/120 -> hypertensive crisis.")
        alerts.append("Hypertensive crisis detected. Urgent medical attention is recommended.")

    if validated_vitals.get("heart_rate_status") == "Tachycardia":
        insights.append("Heart rate exceeds 120 bpm -> tachycardia.")
        alerts.append("Tachycardia detected.")

    if validated_vitals.get("heart_rate_status") == "Bradycardia":
        insights.append("Heart rate below 50 bpm -> bradycardia.")
        alerts.append("Bradycardia detected.")

    if not insights:
        insights.append("Vital readings are within acceptable ranges for the selected screening profile.")

    if warnings:
        alerts.extend(warnings)

    if diagnosis["severity"] == "Critical":
        recommendation = "Immediate emergency escalation is advised. Recheck vitals, notify clinical staff, and prepare urgent intervention."
    elif diagnosis["severity"] == "High":
        recommendation = "Prompt clinician review is recommended. Repeat abnormal measurements and monitor the patient closely."
    elif diagnosis["severity"] == "Moderate":
        recommendation = "Monitor closely, repeat the readings, and advise follow-up assessment if symptoms persist."
    else:
        recommendation = "Continue routine monitoring and maintain preventive care guidance."

    return {
        "patient": {
            "name": patient.get("name", "Unknown"),
            "id": patient.get("id", "Unknown"),
            "date": patient.get("date", date.today().isoformat()),
        },
        "vitals": validated_vitals,
        "diagnosis": diagnosis,
        "insights": insights,
        "alerts": alerts,
        "recommendation": recommendation,
    }
