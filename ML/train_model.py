# train_model.py - ML Model Training Script
# Run this to train and save the attendance prediction model
# Usage: python train_model.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# ─────────────── CONFIGURATION ───────────────
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'attendance_model.pkl')

# Label mapping: 0 = High Absence Risk, 1 = Irregular Attendance, 2 = Regular Worker
LABEL_NAMES = {0: 'High Absence Risk', 1: 'Irregular Attendance', 2: 'Regular Worker'}

def load_and_preprocess():
    """Load dataset and prepare features/target."""
    print("[STEP 1] Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"  Loaded {len(df)} records with columns: {list(df.columns)}")
    print(f"\n  Label distribution:\n{df['label'].value_counts().to_string()}\n")

    # Feature columns
    feature_cols = [
        'attendance_percentage',
        'num_absences',
        'num_late',
        'shift_encoded',
        'weekend_attendance',
        'avg_working_hours'
    ]

    X = df[feature_cols].values
    y = df['label'].values

    return X, y, feature_cols

def train(X, y):
    """Train Random Forest model."""
    print("[STEP 2] Splitting data (80% train / 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train size: {len(X_train)}, Test size: {len(X_test)}")

    print("\n[STEP 3] Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=2,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    print("  Training complete.")

    return model, X_test, y_test

def evaluate(model, X_test, y_test, feature_cols):
    """Evaluate model performance."""
    print("\n[STEP 4] Evaluating model...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Accuracy: {acc * 100:.2f}%")

    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred,
                                 target_names=[LABEL_NAMES[i] for i in sorted(LABEL_NAMES)]))

    print("  Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  {cm}")

    print("\n  Feature Importances:")
    for feat, imp in sorted(zip(feature_cols, model.feature_importances_),
                            key=lambda x: -x[1]):
        bar = "█" * int(imp * 30)
        print(f"    {feat:<30} {imp:.4f}  {bar}")

    return acc

def save_model(model):
    """Save trained model to disk."""
    print(f"\n[STEP 5] Saving model to: {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    print("  Model saved successfully.")

def demo_predict(model, feature_cols):
    """Run a quick demo prediction."""
    print("\n[DEMO] Sample Predictions:")
    samples = [
        {"name": "Ramesh Kumar", "features": [92, 2, 3, 0, 4, 8.2]},
        {"name": "Suresh Singh", "features": [65, 11, 6, 1, 1, 6.9]},
        {"name": "Raju Bhai",    "features": [38, 19, 2, 2, 0, 5.8]},
    ]
    for s in samples:
        pred = model.predict([s['features']])[0]
        proba = model.predict_proba([s['features']])[0]
        score = s['features'][0]
        risk = "Low" if score >= 85 else ("Medium" if score >= 65 else "High")
        print(f"  Worker: {s['name']:<20} → {LABEL_NAMES[pred]:<25} | Score: {score}% | Risk: {risk}")

if __name__ == '__main__':
    print("=" * 60)
    print("  AI Attendance System - ML Model Training")
    print("=" * 60)
    X, y, feature_cols = load_and_preprocess()
    model, X_test, y_test = train(X, y)
    acc = evaluate(model, X_test, y_test, feature_cols)
    save_model(model)
    demo_predict(model, feature_cols)
    print("\n" + "=" * 60)
    print(f"  Training complete! Accuracy: {acc*100:.1f}%")
    print(f"  Model saved at: {MODEL_PATH}")
    print("=" * 60)
