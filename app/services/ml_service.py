"""
ML Service — HydroCare
Train model dari dataset Daily_Water_Intake.csv menggunakan Random Forest.

Model yang dilatih:
1. Random Forest Regressor  → prediksi Daily Water Intake (liter)
2. Random Forest Classifier → prediksi Hydration Level (Good/Poor)
"""

import os
import logging
import csv
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
    classification_report,
)

logger = logging.getLogger(__name__)

# ───────────────────────── paths ─────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "Daily_Water_Intake.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

# Feature column names (harus konsisten dengan training)
FEATURE_COLS = ["Age", "Gender", "Weight (kg)", "Physical Activity Level", "Weather"]

REGRESSOR_PATH = os.path.join(MODEL_DIR, "water_intake_regressor.joblib")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "hydration_classifier.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.joblib")

# ───────────────── encoding maps ─────────────────────────
GENDER_MAP = {"Male": 1, "Female": 0, "male": 1, "female": 0}
ACTIVITY_MAP = {
    "Low": 0, "Moderate": 1, "High": 2,
    "low": 0, "moderate": 1, "high": 2,
    "light": 0,   # mapping dari frontend HydroCare
    "heavy": 2,
}
WEATHER_MAP = {
    "Cold": 0, "Normal": 1, "Hot": 2,
    "cold": 0, "normal": 1, "hot": 2,
}

# ───────────────── in-memory cache ───────────────────────
_regressor = None
_classifier = None
_metrics = None


def _ensure_model_dir():
    """Pastikan folder model ada."""
    os.makedirs(MODEL_DIR, exist_ok=True)


def _load_data_csv():
    X_list, y_intake_list, y_hydration_list = [], [], []
    with open(DATA_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                age = float(row['Age'])
                gender = GENDER_MAP.get(row['Gender'])
                weight = float(row['Weight (kg)'])
                activity = ACTIVITY_MAP.get(row['Physical Activity Level'])
                weather = WEATHER_MAP.get(row['Weather'])
                intake = float(row['Daily Water Intake (liters)'])
                hydration = 1 if row['Hydration Level'] == 'Good' else 0
                
                if None in (gender, activity, weather):
                    continue
                
                X_list.append([age, gender, weight, activity, weather])
                y_intake_list.append(intake)
                y_hydration_list.append(hydration)
            except (KeyError, ValueError):
                continue
    return np.array(X_list), np.array(y_intake_list), np.array(y_hydration_list)


def train_models(force: bool = False) -> dict:
    """
    Latih 2 model dari dataset CSV.
    Jika sudah ada model tersimpan dan force=False, skip training.
    Returns dict berisi metrics.
    """
    global _regressor, _classifier, _metrics

    # Cek apakah model sudah ada
    if not force and os.path.exists(REGRESSOR_PATH) and os.path.exists(CLASSIFIER_PATH):
        logger.info("✅ Model sudah ada, skip training. Gunakan force=True untuk retrain.")
        _load_models()
        return _metrics or {}

    _ensure_model_dir()

    # ──────── Load & preprocess ──────────
    logger.info(f"📂 Loading dataset dari {DATA_PATH}...")
    X, y_intake, y_hydration = _load_data_csv()
    logger.info(f"   Dataset shape: {X.shape}")

    # Split data (80/20)
    X_train, X_test, y_intake_train, y_intake_test = train_test_split(
        X, y_intake, test_size=0.2, random_state=42
    )
    _, _, y_hydration_train, y_hydration_test = train_test_split(
        X, y_hydration, test_size=0.2, random_state=42
    )

    # ──────── Train Regressor ──────────
    logger.info("🏋️ Training Water Intake Regressor...")
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    regressor.fit(X_train, y_intake_train)

    # Evaluate regressor
    y_pred_intake = regressor.predict(X_test)
    r2 = r2_score(y_intake_test, y_pred_intake)
    mae = mean_absolute_error(y_intake_test, y_pred_intake)
    rmse = np.sqrt(mean_squared_error(y_intake_test, y_pred_intake))

    logger.info(f"   R² Score:  {r2:.4f}")
    logger.info(f"   MAE:       {mae:.4f} liters")
    logger.info(f"   RMSE:      {rmse:.4f} liters")

    # ──────── Train Classifier ──────────
    logger.info("🏋️ Training Hydration Level Classifier...")
    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    classifier.fit(X_train, y_hydration_train)

    # Evaluate classifier
    y_pred_hydration = classifier.predict(X_test)
    accuracy = accuracy_score(y_hydration_test, y_pred_hydration)
    report = classification_report(
        y_hydration_test, y_pred_hydration,
        target_names=["Poor", "Good"],
        output_dict=True,
    )

    logger.info(f"   Accuracy:  {accuracy:.4f}")

    # ──────── Feature importances ──────────
    feature_importance = dict(zip(FEATURE_COLS, regressor.feature_importances_.tolist()))

    # ──────── Save models ──────────
    joblib.dump(regressor, REGRESSOR_PATH)
    joblib.dump(classifier, CLASSIFIER_PATH)

    metrics = {
        "regressor": {
            "r2_score": round(r2, 4),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
        },
        "classifier": {
            "accuracy": round(accuracy, 4),
            "classification_report": report,
        },
        "feature_importance": feature_importance,
        "dataset_info": {
            "total_rows": len(df),
            "train_rows": len(X_train),
            "test_rows": len(X_test),
        },
    }
    joblib.dump(metrics, METRICS_PATH)

    # Cache di memory
    _regressor = regressor
    _classifier = classifier
    _metrics = metrics

    logger.info("✅ Training selesai! Model tersimpan.")
    return metrics


def _load_models():
    """Load model dari disk ke memory."""
    global _regressor, _classifier, _metrics

    if _regressor is None and os.path.exists(REGRESSOR_PATH):
        _regressor = joblib.load(REGRESSOR_PATH)
        logger.info("📦 Regressor loaded from disk.")

    if _classifier is None and os.path.exists(CLASSIFIER_PATH):
        _classifier = joblib.load(CLASSIFIER_PATH)
        logger.info("📦 Classifier loaded from disk.")

    if _metrics is None and os.path.exists(METRICS_PATH):
        _metrics = joblib.load(METRICS_PATH)


def predict_water_intake(
    age: int,
    gender: str,
    weight_kg: float,
    activity: str,
    weather: str,
) -> float:
    """
    Prediksi kebutuhan air harian (liter).
    """
    global _regressor
    _load_models()

    if _regressor is None:
        raise RuntimeError("Model belum di-train! Jalankan /api/ml/retrain terlebih dahulu.")

    gender_enc = GENDER_MAP.get(gender, GENDER_MAP.get(gender.capitalize(), 0))
    activity_enc = ACTIVITY_MAP.get(activity, ACTIVITY_MAP.get(activity.capitalize(), 1))
    weather_enc = WEATHER_MAP.get(weather, WEATHER_MAP.get(weather.capitalize(), 1))

    # Gunakan 2D array native untuk menghindari pandas dependency
    features = [[age, gender_enc, weight_kg, activity_enc, weather_enc]]
    prediction = _regressor.predict(features)[0]

    # Clamp antara 1.0 dan 6.0 liter (batas wajar)
    prediction = max(1.0, min(6.0, prediction))
    return round(prediction, 2)


def predict_hydration_level(
    age: int,
    gender: str,
    weight_kg: float,
    activity: str,
    weather: str,
) -> dict:
    """
    Prediksi level hidrasi (Good/Poor) beserta probabilitas.
    """
    global _classifier
    _load_models()

    if _classifier is None:
        raise RuntimeError("Model belum di-train! Jalankan /api/ml/retrain terlebih dahulu.")

    gender_enc = GENDER_MAP.get(gender, GENDER_MAP.get(gender.capitalize(), 0))
    activity_enc = ACTIVITY_MAP.get(activity, ACTIVITY_MAP.get(activity.capitalize(), 1))
    weather_enc = WEATHER_MAP.get(weather, WEATHER_MAP.get(weather.capitalize(), 1))

    # Gunakan 2D array native untuk menghindari pandas dependency
    features = [[age, gender_enc, weight_kg, activity_enc, weather_enc]]
    prediction = _classifier.predict(features)[0]
    probabilities = _classifier.predict_proba(features)[0]

    level = "Good" if prediction == 1 else "Poor"
    return {
        "level": level,
        "confidence": round(float(max(probabilities)) * 100, 1),
        "probabilities": {
            "Poor": round(float(probabilities[0]) * 100, 1),
            "Good": round(float(probabilities[1]) * 100, 1),
        },
    }


def get_model_info() -> dict:
    """Ambil informasi model & metrics."""
    global _metrics
    _load_models()

    models_exist = os.path.exists(REGRESSOR_PATH) and os.path.exists(CLASSIFIER_PATH)

    return {
        "models_trained": models_exist,
        "regressor_path": REGRESSOR_PATH if models_exist else None,
        "classifier_path": CLASSIFIER_PATH if models_exist else None,
        "dataset_path": DATA_PATH,
        "dataset_exists": os.path.exists(DATA_PATH),
        "metrics": _metrics or {},
    }
