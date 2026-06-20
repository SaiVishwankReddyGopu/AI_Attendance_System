# 🏭 AI-Enhanced Attendance Management System for Blue Collar Workers

A full-stack web application that manages attendance of blue-collar workers using **Machine Learning** (Random Forest Classifier) and **Generative AI** (OpenAI GPT) for attendance prediction and workforce insights.

---

## 🚀 Features

- **Authentication** – Role-based login (Worker / Admin) with registration
- **Attendance Management** – Daily check-in/check-out, working hour calculation, shift tracking
- **Worker Dashboard** – Profile, attendance %, history table, working hours
- **Admin Dashboard** – Stats cards, all workers, attendance log, mark attendance
- **ML Predictions** – Random Forest classifies workers as: Regular / Irregular / High Absence Risk
- **AI Insights** – GPT-powered natural language workforce report generation
- **Responsive UI** – Works on desktop and mobile

---

## 🗂️ Project Structure

```
AI_Attendance_System/
├── Frontend/
│   ├── index.html              # Landing page
│   ├── login.html              # Login & Register
│   ├── worker_dashboard.html   # Worker portal
│   ├── admin_dashboard.html    # Admin portal
│   ├── attendance.html         # Attendance module
│   ├── style.css               # All styles
│   └── script.js               # Shared JS utilities
├── Backend/
│   ├── app.py                  # Flask entry point
│   ├── config.py               # Configuration
│   ├── database.py             # MySQL connection + init
│   ├── models.py               # DB query helpers
│   ├── routes.py               # API endpoints
│   └── requirements.txt        # Python dependencies
├── ML/
│   ├── train_model.py          # Train Random Forest
│   ├── dataset.csv             # Sample training data
│   ├── attendance_model.pkl    # Saved model (after training)
│   └── attendance_model.ipynb  # Jupyter notebook
├── GenAI/
│   └── insight_generator.py   # GPT insight generator
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Node.js (optional, for serving frontend)

---

### 1️⃣ MySQL Database Setup

Open MySQL and run:

```sql
-- Create database (auto-created by app, but you can also run this)
CREATE DATABASE IF NOT EXISTS attendance_db;

-- Or import the SQL script:
-- mysql -u root -p < database_setup.sql
```

Update your credentials in `Backend/config.py`:

```python
DB_HOST     = 'localhost'
DB_USER     = 'root'
DB_PASSWORD = 'your_mysql_password'
DB_NAME     = 'attendance_db'
OPENAI_API_KEY = 'your-openai-api-key'   # Optional for AI reports
```

---

### 2️⃣ Backend Setup

```bash
cd Backend

# Install dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

The backend starts at **http://localhost:5000**

On first run, it automatically:
- Creates the `attendance_db` database
- Creates all tables (users, workers, attendance)
- Adds default admin: `username=admin`, `password=admin123`

---

### 3️⃣ ML Model Training

```bash
cd ML

# Train the Random Forest model (takes ~5 seconds)
python train_model.py

# This creates attendance_model.pkl
```

Expected output:
```
Accuracy: ~91%
Model saved as attendance_model.pkl
```

---

### 4️⃣ Frontend

Open directly in browser — **no build step needed**:

```
Frontend/index.html   → double-click to open
```

Or serve with Python:

```bash
cd Frontend
python -m http.server 8080
# Open: http://localhost:8080
```

---

## 🔑 Default Login

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | admin123 |

Register workers via the **Login → Register Worker** tab or **Admin → Add Worker**.

---

## 🌐 API Endpoints

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | `/api/login`                    | Authenticate user        |
| POST   | `/api/register`                 | Register new worker      |
| GET    | `/api/workers`                  | Get all workers          |
| GET    | `/api/worker/<id>`              | Get worker profile       |
| POST   | `/api/mark_attendance`          | Mark attendance          |
| GET    | `/api/attendance_history`       | Today's attendance       |
| GET    | `/api/worker_attendance/<id>`   | Worker's history         |
| GET    | `/api/dashboard_stats`          | Admin stats              |
| GET    | `/api/predict/<worker_id>`      | ML prediction            |
| GET    | `/api/generate_insight`         | AI report                |

---

## 🤖 ML Model Details

- **Algorithm**: Random Forest Classifier (100 trees)
- **Features**: attendance %, absences, late count, shift, weekend attendance, avg hours
- **Labels**: Regular Worker, Irregular Attendance, High Absence Risk
- **Accuracy**: ~91.7%

---

## ✨ GenAI Integration

Set your OpenAI API key in `config.py`. If not set, a rule-based fallback report is generated automatically — **no API key required for basic functionality**.

---

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | HTML, CSS, JavaScript, Chart.js   |
| Backend    | Python, Flask, Flask-CORS         |
| Database   | MySQL                             |
| ML         | Scikit-learn (Random Forest)      |
| GenAI      | OpenAI GPT-3.5-turbo              |
