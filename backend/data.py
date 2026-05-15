"""
Dataset generation script for Sanjeevani AI.
Creates 10,000+ rows of synthetic medical data with realistic ranges.
"""

import csv
import numpy as np
from pathlib import Path


def generate_dataset(n_samples: int = 10000, random_seed: int = 42) -> None:
    """Generate synthetic medical dataset and save to data.csv."""
    np.random.seed(random_seed)

    data = []

    for _ in range(n_samples):
        temperature = np.random.uniform(20, 40)
        humidity = np.random.uniform(40, 90)
        aqi = np.random.uniform(50, 300)
        heart_rate = np.random.uniform(60, 120)
        bp_systolic = np.random.uniform(90, 180)
        bp_diastolic = np.random.uniform(60, 120)
        spo2 = np.random.uniform(85, 100)

        high_humidity = humidity > 70
        high_aqi = aqi > 120
        low_temp = temperature < 22

        if high_humidity and high_aqi:
            risk = "High"
            disease = "Dengue"
        elif high_aqi:
            risk = "Medium" if aqi > 150 else "Low"
            disease = "Respiratory"
        elif low_temp and heart_rate > 100:
            risk = "Medium"
            disease = "Flu"
        elif temperature > 38 and spo2 < 92:
            risk = "High"
            disease = "Respiratory"
        else:
            risk = "Low"
            disease = "Normal"

        data.append({
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "aqi": round(aqi, 2),
            "heart_rate": round(heart_rate, 2),
            "bp_systolic": round(bp_systolic, 2),
            "bp_diastolic": round(bp_diastolic, 2),
            "spo2": round(spo2, 2),
            "risk": risk,
            "disease": disease,
        })

    csv_path = Path(__file__).parent / "data.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "temperature",
                "humidity",
                "aqi",
                "heart_rate",
                "bp_systolic",
                "bp_diastolic",
                "spo2",
                "risk",
                "disease",
            ],
        )
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ Dataset created: {csv_path}")
    print(f"  Total rows: {n_samples}")
    print(f"  Risk distribution: {sum(1 for d in data if d['risk'] == 'Low')} Low, {sum(1 for d in data if d['risk'] == 'Medium')} Medium, {sum(1 for d in data if d['risk'] == 'High')} High")
    print(f"  Disease distribution: {sum(1 for d in data if d['disease'] == 'Normal')} Normal, {sum(1 for d in data if d['disease'] == 'Dengue')} Dengue, {sum(1 for d in data if d['disease'] == 'Flu')} Flu, {sum(1 for d in data if d['disease'] == 'Respiratory')} Respiratory")


if __name__ == "__main__":
    generate_dataset()
"""
Generate synthetic medical dataset for Sanjeevani AI model training.
Creates 10,000+ realistic healthcare records with features and labels.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
N_SAMPLES = 10000

print("🔄 Generating synthetic medical dataset...")

# Generate features with realistic ranges
data = {
    "temperature": np.random.uniform(20, 40, N_SAMPLES),  # Celsius
    "humidity": np.random.uniform(40, 90, N_SAMPLES),  # Percentage
    "aqi": np.random.uniform(50, 300, N_SAMPLES),  # Air Quality Index
    "heart_rate": np.random.uniform(60, 120, N_SAMPLES),  # BPM
    "bp_systolic": np.random.uniform(90, 180, N_SAMPLES),  # mmHg
    "bp_diastolic": np.random.uniform(60, 120, N_SAMPLES),  # mmHg
    "spo2": np.random.uniform(85, 100, N_SAMPLES),  # Oxygen saturation %
}

df = pd.DataFrame(data)

# Generate labels using medical logic rules
def assign_risk_and_disease(row):
    """Assign risk level and disease based on vital signs and environmental factors."""
    score = 0
    disease = "Normal"

    # Temperature-based scoring
    if row["temperature"] >= 38.5:
        score += 2
    elif row["temperature"] >= 37.5:
        score += 1

    # SpO2-based scoring
    if row["spo2"] < 92:
        score += 3
    elif row["spo2"] < 95:
        score += 2

    # Heart rate-based scoring
    if row["heart_rate"] > 120:
        score += 2
    elif row["heart_rate"] > 100:
        score += 1

    # Blood pressure-based scoring
    if row["bp_systolic"] > 180 or row["bp_diastolic"] > 120:
        score += 3
    elif row["bp_systolic"] > 140 or row["bp_diastolic"] > 90:
        score += 1

    # Environmental factors for disease prediction
    if row["humidity"] >= 75 and row["aqi"] >= 120:
        disease = "Dengue"
    elif row["aqi"] >= 140:
        disease = "Respiratory"
    elif row["temperature"] <= 20:
        disease = "Flu"
    else:
        disease = "Normal"

    # Risk assignment based on score
    if score >= 7:
        risk = "High"
    elif score >= 4:
        risk = "Medium"
    else:
        risk = "Low"

    return risk, disease

# Apply labeling function
print("📋 Assigning risk and disease labels...")
df[["risk", "disease"]] = df.apply(lambda row: pd.Series(assign_risk_and_disease(row)), axis=1)

# Convert categorical columns to numeric for model training
risk_mapping = {"Low": 0, "Medium": 1, "High": 2}
disease_mapping = {"Normal": 0, "Dengue": 1, "Respiratory": 2, "Flu": 3}

df["risk_encoded"] = df["risk"].map(risk_mapping)
df["disease_encoded"] = df["disease"].map(disease_mapping)

# Save dataset
output_path = Path(__file__).parent / "data.csv"
df.to_csv(output_path, index=False)

print(f"\n✅ Dataset created successfully!")
print(f"📁 Saved to: {output_path}")
print(f"📊 Rows: {len(df)}")
print(f"📈 Columns: {list(df.columns)}")
print(f"\nRisk distribution:\n{df['risk'].value_counts()}")
print(f"\nDisease distribution:\n{df['disease'].value_counts()}")
print(f"\nFeature ranges:")
print(df.describe())
