# routes.py - Flask API Route Definitions

from flask import Blueprint, request, jsonify, session
import joblib
import os
import pandas as pd
import numpy as np
from config import Config
from models import (
    find_user, create_user, create_worker, get_all_workers,
    get_worker_by_username, get_worker_by_id,
    mark_attendance, get_attendance_history, get_all_attendance_today,
    get_attendance_stats, get_worker_attendance_summary
)

api = Blueprint('api', __name__)

# Load ML model once at startup
_model = None
def load_model():
    global _model
    if _model is None and os.path.exists(Config.MODEL_PATH):
        try:
            _model = joblib.load(Config.MODEL_PATH)
            print("[ML] Model loaded successfully.")
        except Exception as e:
            print(f"[ML] Could not load model: {e}")
    return _model


# ═══════════════════════ AUTH ROUTES ═══════════════════════

@api.route('/login', methods=['POST'])
def login():
    """Authenticate user and return role + basic info."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = find_user(username, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    session['user'] = user
    response_data = {"success": True, "role": user['role'], "username": username}

    # Attach worker ID if role is worker
    if user['role'] == 'worker':
        worker = get_worker_by_username(username)
        if worker:
            response_data['worker_id'] = worker['id']
            response_data['name'] = worker['name']

    return jsonify(response_data), 200


@api.route('/register', methods=['POST'])
def register():
    """Register a new worker (admin can also call this)."""
    data = request.get_json()
    required = ['name', 'phone', 'contractor', 'shift', 'username', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "message": f"Field '{field}' is required"}), 400

    success, message = create_worker(
        data['name'], data['phone'], data['contractor'],
        data['shift'], data['username'], data['password']
    )
    status = 201 if success else 400
    return jsonify({"success": success, "message": message}), status


@api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"}), 200


# ═══════════════════════ WORKER ROUTES ═══════════════════════

@api.route('/workers', methods=['GET'])
def get_workers():
    """Admin: Get all workers."""
    workers = get_all_workers()
    return jsonify({"success": True, "workers": workers}), 200


@api.route('/worker/<int:worker_id>', methods=['GET'])
def get_worker(worker_id):
    """Get a single worker profile."""
    worker = get_worker_by_id(worker_id)
    if not worker:
        return jsonify({"success": False, "message": "Worker not found"}), 404
    return jsonify({"success": True, "worker": worker}), 200


# ═══════════════════════ ATTENDANCE ROUTES ═══════════════════════

@api.route('/mark_attendance', methods=['POST'])
def mark():
    """Mark attendance for a worker."""
    data = request.get_json()
    worker_id = data.get('worker_id')
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    status = data.get('status', 'present')

    if not worker_id:
        return jsonify({"success": False, "message": "worker_id is required"}), 400

    success, message = mark_attendance(worker_id, check_in, check_out, status)
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@api.route('/attendance_history', methods=['GET'])
def attendance_history():
    """Admin: Get today's full attendance list."""
    records = get_all_attendance_today()
    return jsonify({"success": True, "records": records}), 200


@api.route('/worker_attendance/<int:worker_id>', methods=['GET'])
def worker_attendance(worker_id):
    """Get attendance history for a specific worker."""
    records = get_attendance_history(worker_id)
    summary = get_worker_attendance_summary(worker_id)
    return jsonify({"success": True, "records": records, "summary": summary}), 200


@api.route('/dashboard_stats', methods=['GET'])
def dashboard_stats():
    """Admin: Dashboard summary numbers."""
    stats = get_attendance_stats()
    return jsonify({"success": True, "stats": stats}), 200


# ═══════════════════════ ML PREDICTION ROUTE ═══════════════════════

@api.route('/predict/<int:worker_id>', methods=['GET'])
def predict(worker_id):
    """
    Predict attendance behavior for a worker using the trained ML model.
    Returns: category label, score, risk level.
    """
    model = load_model()
    if not model:
        return jsonify({"success": False, "message": "ML model not loaded. Please train the model first."}), 503

    # Build feature vector from worker's attendance history
    records = get_attendance_history(worker_id, limit=30)
    summary = get_worker_attendance_summary(worker_id)
    worker = get_worker_by_id(worker_id)

    if not worker:
        return jsonify({"success": False, "message": "Worker not found"}), 404

    if len(records) == 0:
        return jsonify({
            "success": True,
            "worker_name": worker['name'],
            "prediction": "Insufficient Data",
            "attendance_score": 0,
            "risk_level": "Unknown"
        }), 200

    # Feature engineering from records
    total = len(records)
    present = sum(1 for r in records if r['status'] in ('present', 'late'))
    absent = sum(1 for r in records if r['status'] == 'absent')
    late = sum(1 for r in records if r['status'] == 'late')
    attendance_pct = (present / total * 100) if total > 0 else 0

    # Shift encoding
    shift_map = {'morning': 0, 'afternoon': 1, 'night': 2}
    shift_enc = shift_map.get(worker.get('shift', 'morning'), 0)

    # Weekly pattern: count days per weekday
    from collections import Counter
    weekday_counts = Counter()
    for r in records:
        try:
            wd = pd.to_datetime(r['date']).weekday()
            weekday_counts[wd] += 1
        except Exception:
            pass
    weekend_days = weekday_counts.get(5, 0) + weekday_counts.get(6, 0)

    # Average working hours
    avg_hours = summary.get('total_working_hours', 0) / max(present, 1)

    features = np.array([[
        attendance_pct,   # attendance_percentage
        absent,           # num_absences
        late,             # num_late
        shift_enc,        # shift_encoded
        weekend_days,     # weekend_attendance
        avg_hours         # avg_working_hours
    ]])

    try:
        prediction_idx = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        labels = ['High Absence Risk', 'Irregular Attendance', 'Regular Worker']
        label = labels[prediction_idx] if prediction_idx < len(labels) else str(prediction_idx)

        score = round(attendance_pct, 1)
        risk = "Low" if score >= 85 else ("Medium" if score >= 65 else "High")

        return jsonify({
            "success": True,
            "worker_name": worker['name'],
            "prediction": label,
            "attendance_score": score,
            "risk_level": risk,
            "probabilities": {l: round(float(p) * 100, 1) for l, p in zip(labels, proba)}
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Prediction error: {str(e)}"}), 500


# ═══════════════════════ GENAI INSIGHT ROUTE ═══════════════════════

@api.route('/generate_insight', methods=['GET'])
def generate_insight():
    """Generate AI-powered attendance insight report."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'GenAI'))
    from insight_generator import generate_workforce_insight

    workers = get_all_workers()
    all_records = get_all_attendance_today()
    stats = get_attendance_stats()

    insight = generate_workforce_insight(workers, all_records, stats)
    return jsonify({"success": True, "insight": insight}), 200
