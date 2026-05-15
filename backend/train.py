"""
Model training script for Sanjeevani AI.
Trains Risk and Disease prediction models using XGBoost.
"""

import csv
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

try:
    from xgboost import XGBClassifier
    use_xgboost = True
except ImportError:
    from sklearn.ensemble import RandomForestClassifier
    use_xgboost = False


def load_data(csv_path: str = "data.csv"):
    """Load dataset from CSV."""
    csv_file = Path(__file__).parent / csv_path
    
    if not csv_file.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_file}. Run data.py first.")
    
    X, y_risk, y_disease = [], [], []
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append([
                float(row["temperature"]),
                float(row["humidity"]),
                float(row["aqi"]),
                float(row["heart_rate"]),
                float(row["bp_systolic"]),
                float(row["bp_diastolic"]),
                float(row["spo2"]),
            ])
            y_risk.append(row["risk"])
            y_disease.append(row["disease"])
    
    return np.array(X), np.array(y_risk), np.array(y_disease)


def train_models():
    """Train both risk and disease prediction models."""
    print("=" * 60)
    print("SANJEEVANI AI - MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # Load data
    print("\n[1] Loading dataset...")
    X, y_risk, y_disease = load_data()
    print(f"✓ Loaded {len(X)} samples with {X.shape[1]} features")
    
    # Encode labels
    print("\n[2] Encoding labels...")
    risk_encoder = LabelEncoder()
    disease_encoder = LabelEncoder()
    y_risk_encoded = risk_encoder.fit_transform(y_risk)
    y_disease_encoded = disease_encoder.fit_transform(y_disease)
    print(f"✓ Risk classes: {risk_encoder.classes_}")
    print(f"✓ Disease classes: {disease_encoder.classes_}")
    
    # Train-test split
    print("\n[3] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_risk_train, y_risk_test, y_disease_train, y_disease_test = train_test_split(
        X, y_risk_encoded, y_disease_encoded, test_size=0.2, random_state=42
    )
    print(f"✓ Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Train risk model
    print("\n[4] Training Risk Prediction Model...")
    if use_xgboost:
        risk_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, verbosity=0)
        print("  Using: XGBoost")
    else:
        risk_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        print("  Using: Random Forest (XGBoost not available)")
    
    risk_model.fit(X_train, y_risk_train)
    risk_pred_train = risk_model.predict(X_train)
    risk_pred_test = risk_model.predict(X_test)
    
    risk_train_acc = accuracy_score(y_risk_train, risk_pred_train)
    risk_test_acc = accuracy_score(y_risk_test, risk_pred_test)
    
    print(f"  Train Accuracy: {risk_train_acc:.4f}")
    print(f"  Test Accuracy:  {risk_test_acc:.4f}")
    print(f"\n  Confusion Matrix (Test):\n{confusion_matrix(y_risk_test, risk_pred_test)}")
    print(f"\n  Classification Report (Test):\n{classification_report(y_risk_test, risk_pred_test, target_names=risk_encoder.classes_)}")
    
    # Train disease model
    print("\n[5] Training Disease Classification Model...")
    if use_xgboost:
        disease_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, verbosity=0)
    else:
        disease_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    
    disease_model.fit(X_train, y_disease_train)
    disease_pred_train = disease_model.predict(X_train)
    disease_pred_test = disease_model.predict(X_test)
    
    disease_train_acc = accuracy_score(y_disease_train, disease_pred_train)
    disease_test_acc = accuracy_score(y_disease_test, disease_pred_test)
    
    print(f"  Train Accuracy: {disease_train_acc:.4f}")
    print(f"  Test Accuracy:  {disease_test_acc:.4f}")
    print(f"\n  Confusion Matrix (Test):\n{confusion_matrix(y_disease_test, disease_pred_test)}")
    print(f"\n  Classification Report (Test):\n{classification_report(y_disease_test, disease_pred_test, target_names=disease_encoder.classes_)}")
    
    # Save models
    print("\n[6] Saving trained models...")
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    joblib.dump(risk_model, models_dir / "risk_model.pkl")
    joblib.dump(disease_model, models_dir / "disease_model.pkl")
    joblib.dump(risk_encoder, models_dir / "risk_encoder.pkl")
    joblib.dump(disease_encoder, models_dir / "disease_encoder.pkl")
    
    print(f"✓ Risk model saved to {models_dir / 'risk_model.pkl'}")
    print(f"✓ Disease model saved to {models_dir / 'disease_model.pkl'}")
    print(f"✓ Encoders saved")
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE")
    print("=" * 60)
    
    return {
        "risk_model": risk_model,
        "disease_model": disease_model,
        "risk_encoder": risk_encoder,
        "disease_encoder": disease_encoder,
        "metrics": {
            "risk_train_acc": risk_train_acc,
            "risk_test_acc": risk_test_acc,
            "disease_train_acc": disease_train_acc,
            "disease_test_acc": disease_test_acc,
        }
    }


if __name__ == "__main__":
    train_models()
