# 🚀 Render + Supabase Deployment Guide
## AI Attendance Management System

---

## 📦 Stack Overview

| Layer | Service | Free? |
|---|---|---|
| Backend API | Render Web Service (Python/Flask) | ✅ Yes |
| Frontend | Render Static Site | ✅ Yes |
| Database | Supabase (PostgreSQL) | ✅ Yes (500MB) |

---

## STEP 1 — Set Up Supabase Database

1. Go to [supabase.com](https://supabase.com) → **Sign Up** (free)
2. Click **New Project**
   - Name: `ai-attendance`
   - Set a strong database password (save it!)
   - Choose a region closest to you (e.g. `ap-south-1` for India)
   - Click **Create Project** — wait ~1 minute

3. Get your connection string:
   - Go to **Project Settings** → **Database**
   - Scroll to **Connection string** → select **URI** tab
   - Copy the string — looks like:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres
     ```
   - Replace `[YOUR-PASSWORD]` with your actual password
   - **Save this — you'll need it in Step 3**

> ✅ That's it for Supabase! Tables are auto-created by the app on first startup.

---

## STEP 2 — Push Code to GitHub

```bash
cd AI_Attendance_System

git init
git add .
git commit -m "Initial commit — Render + Supabase deployment"

# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/AI_Attendance_System.git
git branch -M main
git push -u origin main
```

---

## STEP 3 — Deploy Backend on Render

1. Go to [render.com](https://render.com) → **Sign Up / Log In**
2. Click **New** → **Web Service**
3. Connect your GitHub account → select your `AI_Attendance_System` repo
4. Configure:

   | Field | Value |
   |---|---|
   | **Name** | `ai-attendance-backend` |
   | **Root Directory** | `Backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
   | **Plan** | Free |

5. Scroll to **Environment Variables** → add these:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | Your Supabase connection string from Step 1 |
   | `SECRET_KEY` | Any random string (e.g. `myS3cr3tK3y2024!`) |
   | `OPENAI_API_KEY` | Your OpenAI key (or leave blank — app works without it) |
   | `CORS_ORIGINS` | `*` (update later to your frontend URL) |

6. Click **Create Web Service**
   - Build takes ~3-5 minutes
   - Watch the logs — you should see:
     ```
     [DB] Database initialized successfully.
     [DB] Default admin created: username=admin, password=admin123
     ```

7. **Copy your backend URL** — e.g. `https://ai-attendance-backend.onrender.com`

---

## STEP 4 — Update Frontend API URL

Open `Frontend/script.js` and update line 2:

```javascript
// Replace with YOUR actual Render backend URL:
const API_BASE = 'https://ai-attendance-backend.onrender.com/api';
```

Then push the change:
```bash
git add Frontend/script.js
git commit -m "Update API_BASE to production backend URL"
git push
```

---

## STEP 5 — Deploy Frontend on Render

1. Render Dashboard → **New** → **Static Site**
2. Select the same GitHub repo
3. Configure:

   | Field | Value |
   |---|---|
   | **Name** | `ai-attendance-frontend` |
   | **Root Directory** | `Frontend` |
   | **Build Command** | *(leave blank)* |
   | **Publish Directory** | `.` |

4. Click **Create Static Site** — deploys in ~1 minute
5. **Copy your frontend URL** — e.g. `https://ai-attendance-frontend.onrender.com`

---

## STEP 6 — Lock Down CORS (Recommended)

Go to your backend on Render → **Environment** → update:

| Key | Value |
|---|---|
| `CORS_ORIGINS` | `https://ai-attendance-frontend.onrender.com` |

Click **Save Changes** — backend will redeploy automatically.

---

## ✅ You're Live!

| URL | Link |
|---|---|
| Frontend | `https://ai-attendance-frontend.onrender.com` |
| Backend API | `https://ai-attendance-backend.onrender.com/api` |

**Default login:**
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |

⚠️ Change the admin password after first login!

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `connection refused` / DB error | Double-check `DATABASE_URL` — make sure password has no special chars that need URL-encoding |
| Tables not created | Check backend logs in Render for `[DB ERROR]` messages |
| CORS error in browser | Set `CORS_ORIGINS` to your exact frontend URL |
| ML model not found | Make sure `ML/attendance_model.pkl` is committed to git |
| Backend sleeps (free tier) | Use [UptimeRobot](https://uptimerobot.com) — free ping every 5 min |
| `password authentication failed` | In Supabase: Settings → Database → Reset password |

---

## 💡 Supabase Tips

- **View your data:** Supabase dashboard → **Table Editor** — you can see/edit rows visually
- **SQL console:** Supabase → **SQL Editor** — run queries directly
- **Free tier limits:** 500MB storage, 2 projects, pauses after 1 week of inactivity on free plan
- **Prevent pausing:** Visit your Supabase project dashboard at least once a week, or upgrade to Pro ($25/mo)
