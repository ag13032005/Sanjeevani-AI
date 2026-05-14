from __future__ import annotations

from dataclasses import dataclass
from random import Random


RNG = Random(42)


@dataclass
class ModelPrediction:
    risk_level: str
    confidence: float
    feature_score: float
    recommendation: str
    disease: str
    explanation: str
    alert: str


class OutbreakModel:
    def __init__(self) -> None:
        self.forest = self._build_forest()

    def _build_forest(self) -> list[dict[str, float | str]]:
        # The workspace runs on Python 3.14, so we use a lightweight ensemble
        # that behaves like a tiny decision forest without external ML wheels.
        return [
            {"feature": "humidity", "threshold": 68.0, "weight": 1.1, "direction": "high"},
            {"feature": "humidity", "threshold": 78.0, "weight": 1.4, "direction": "high"},
            {"feature": "aqi", "threshold": 95.0, "weight": 1.0, "direction": "high"},
            {"feature": "aqi", "threshold": 145.0, "weight": 1.5, "direction": "high"},
            {"feature": "temperature", "threshold": 30.0, "weight": 0.9, "direction": "high"},
            {"feature": "temperature", "threshold": 25.0, "weight": 0.5, "direction": "low"},
        ]

    def _explain(self, temperature: float, humidity: float, aqi: float, risk_level: str) -> str:
        if risk_level == "High":
            return f"High outbreak risk driven by humidity at {humidity:.1f}% and AQI {aqi:.0f}."
        if risk_level == "Medium":
            return f"Moderate outbreak risk due to environmental pressure from humidity {humidity:.1f}% and AQI {aqi:.0f}."
        return f"Low outbreak risk. Conditions are currently less favorable for rapid spread."

    def predict_disease(self, temperature: float, humidity: float, aqi: float, risk_level: str) -> tuple[str, str, str]:
        if risk_level == "High":
            if humidity >= 75 and aqi >= 120:
                disease = "Dengue"
                explanation = "High humidity and polluted air create a strong mosquito-breeding and outbreak environment."
                alert = "High dengue risk due to humidity and AQI."
            elif aqi >= 140:
                disease = "Respiratory Infection"
                explanation = "Very poor air quality can increase respiratory stress and infection risk."
                alert = "High respiratory disease risk due to very poor AQI."
            elif temperature <= 20:
                disease = "Flu"
                explanation = "Cooler conditions combined with high outbreak pressure can favor flu spread."
                alert = "High flu risk due to low temperature and outbreak pressure."
            else:
                disease = "Malaria"
                explanation = "Warm and humid conditions with elevated environmental pressure can support vector spread."
                alert = "High malaria risk due to warm, humid conditions."
        elif risk_level == "Medium":
            if humidity >= 70 and aqi >= 100:
                disease = "Dengue"
                explanation = "Humidity and AQI are trending upward, which may increase mosquito-borne disease risk."
                alert = "Moderate dengue risk developing."
            elif aqi >= 100:
                disease = "Respiratory Infection"
                explanation = "Air quality is enough to irritate airways and raise respiratory concerns."
                alert = "Moderate respiratory disease risk due to AQI."
            elif temperature <= 18:
                disease = "Flu"
                explanation = "Cool weather can help flu-like illnesses spread more easily."
                alert = "Moderate flu risk due to cooler weather."
            else:
                disease = "Malaria"
                explanation = "Conditions are suitable for mosquito growth, but not yet at peak risk."
                alert = "Moderate mosquito-borne disease risk."
        else:
            if temperature <= 18:
                disease = "Flu"
                explanation = "Lower temperatures can still favor seasonal flu spread."
                alert = "Low flu risk, but keep monitoring seasonal changes."
            elif aqi >= 90:
                disease = "Respiratory Infection"
                explanation = "Air quality is somewhat elevated, so respiratory irritation is possible."
                alert = "Low respiratory disease risk, but AQI should still be monitored."
            else:
                disease = "None"
                explanation = "Conditions are currently not strongly supportive of a disease outbreak."
                alert = "Low outbreak risk. Continue routine monitoring."

        return disease, explanation, alert

    def _score(self, temperature: float, humidity: float, aqi: float) -> tuple[float, float, float]:
        low_score = 2.2
        medium_score = 2.0
        high_score = 1.8

        for stump in self.forest:
            feature_value = {
                "temperature": temperature,
                "humidity": humidity,
                "aqi": aqi,
            }[stump["feature"]]
            weight = float(stump["weight"])
            threshold = float(stump["threshold"])
            direction = str(stump["direction"])

            if direction == "high":
                if feature_value >= threshold:
                    high_score += weight
                else:
                    low_score += weight * 0.6
            else:
                if feature_value <= threshold:
                    low_score += weight
                else:
                    medium_score += weight * 0.5

        pressure = (humidity * 0.35) + (aqi * 0.45) + (temperature * 0.2)
        if pressure > 130:
            high_score += 1.8
        elif pressure > 100:
            medium_score += 1.4
        else:
            low_score += 1.2

        total = low_score + medium_score + high_score
        return low_score / total, medium_score / total, high_score / total

    def predict(self, temperature: float, humidity: float, aqi: float) -> ModelPrediction:
        low_probability, medium_probability, high_probability = self._score(temperature, humidity, aqi)
        probability_map = {"Low": low_probability, "Medium": medium_probability, "High": high_probability}
        risk_level = max(probability_map, key=probability_map.get)
        confidence = float(probability_map[risk_level])
        feature_score = round((temperature * 0.2) + (humidity * 0.4) + (aqi * 0.4), 2)
        recommendation = self._explain(temperature, humidity, aqi, risk_level)
        disease, explanation, alert = self.predict_disease(temperature, humidity, aqi, risk_level)
        return ModelPrediction(
            risk_level=risk_level,
            confidence=confidence,
            feature_score=feature_score,
            recommendation=recommendation,
            disease=disease,
            explanation=explanation,
            alert=alert,
        )


model = OutbreakModel()


def get_risk_recommendation(risk_level: str) -> str:
    mapping = {
        "Low": "Maintain routine hygiene, stay hydrated, and keep monitoring local updates.",
        "Medium": "Increase mosquito control, avoid stagnant water, and watch for symptoms.",
        "High": "Limit outdoor exposure, intensify vector control, and follow public health guidance immediately.",
    }
    return mapping.get(risk_level, mapping["Low"])
