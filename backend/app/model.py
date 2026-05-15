from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any

import joblib
import numpy as np


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
        self.models_loaded = False
        self.risk_model: Any = None
        self.disease_model: Any = None
        self.risk_encoder: Any = None
        self.disease_encoder: Any = None
        self._load_ml_artifacts()

    def _load_ml_artifacts(self) -> None:
        models_dir = Path(__file__).resolve().parent.parent / "models"
        risk_model_path = models_dir / "risk_model.pkl"
        disease_model_path = models_dir / "disease_model.pkl"
        risk_encoder_path = models_dir / "risk_encoder.pkl"
        disease_encoder_path = models_dir / "disease_encoder.pkl"

        if not all(
            path.exists()
            for path in [risk_model_path, disease_model_path, risk_encoder_path, disease_encoder_path]
        ):
            return

        try:
            self.risk_model = joblib.load(risk_model_path)
            self.disease_model = joblib.load(disease_model_path)
            self.risk_encoder = joblib.load(risk_encoder_path)
            self.disease_encoder = joblib.load(disease_encoder_path)
            self.models_loaded = True
        except Exception:
            self.models_loaded = False
            self.risk_model = None
            self.disease_model = None
            self.risk_encoder = None
            self.disease_encoder = None

    def _build_forest(self) -> list[dict[str, float | str]]:
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
        return "Low outbreak risk. Conditions are currently less favorable for rapid spread."

    def predict_disease(
        self, temperature: float, humidity: float, aqi: float, risk_level: str
    ) -> tuple[str, str, str]:
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
            feature_name = str(stump["feature"])
            feature_value = {
                "temperature": temperature,
                "humidity": humidity,
                "aqi": aqi,
            }[feature_name]
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

    def _build_feature_vector(self, temperature: float, humidity: float, aqi: float) -> np.ndarray:
        heart_rate = np.clip(78 + (temperature - 37.0) * 8 + (aqi - 100.0) * 0.02, 55.0, 150.0)
        bp_systolic = np.clip(118 + (humidity - 60.0) * 0.22 + (aqi - 100.0) * 0.05, 85.0, 210.0)
        bp_diastolic = np.clip(76 + (humidity - 60.0) * 0.12 + (aqi - 100.0) * 0.03, 55.0, 130.0)
        spo2 = np.clip(98 - max(0.0, aqi - 100.0) * 0.02 - max(0.0, temperature - 37.5) * 0.7, 82.0, 100.0)

        return np.array(
            [[temperature, humidity, aqi, heart_rate, bp_systolic, bp_diastolic, spo2]],
            dtype=float,
        )

    def _predict_with_ml(self, temperature: float, humidity: float, aqi: float) -> ModelPrediction | None:
        if not self.models_loaded:
            return None

        try:
            features = self._build_feature_vector(temperature, humidity, aqi)
            risk_model = self.risk_model
            disease_model = self.disease_model
            risk_encoder = self.risk_encoder
            disease_encoder = self.disease_encoder

            if risk_model is None or disease_model is None or risk_encoder is None or disease_encoder is None:
                return None

            risk_encoded = int(risk_model.predict(features)[0])
            disease_encoded = int(disease_model.predict(features)[0])

            risk_level = str(risk_encoder.inverse_transform([risk_encoded])[0])
            disease = str(disease_encoder.inverse_transform([disease_encoded])[0])

            risk_proba = risk_model.predict_proba(features)[0]
            confidence = float(np.max(risk_proba))

            feature_score = round((temperature * 0.2) + (humidity * 0.4) + (aqi * 0.4), 2)
            recommendation = self._explain(temperature, humidity, aqi, risk_level)
            explanation = (
                f"ML model prediction indicates {risk_level.lower()} risk with likely {disease.lower()} pattern "
                f"for current environmental conditions."
            )
            alert = (
                "Escalate monitoring and prepare response actions."
                if risk_level == "High"
                else "Continue close monitoring of local health trends."
                if risk_level == "Medium"
                else "Maintain routine surveillance and preventive measures."
            )

            return ModelPrediction(
                risk_level=risk_level,
                confidence=confidence,
                feature_score=feature_score,
                recommendation=recommendation,
                disease=disease,
                explanation=explanation,
                alert=alert,
            )
        except Exception:
            return None

    def predict(self, temperature: float, humidity: float, aqi: float) -> ModelPrediction:
        ml_prediction = self._predict_with_ml(temperature, humidity, aqi)
        if ml_prediction is not None:
            return ml_prediction

        low_probability, medium_probability, high_probability = self._score(temperature, humidity, aqi)
        probability_map = {"Low": low_probability, "Medium": medium_probability, "High": high_probability}
        risk_level = max(probability_map.keys(), key=lambda key: probability_map[key])
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