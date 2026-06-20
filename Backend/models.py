# models.py - Data models and database query helpers (PostgreSQL / Supabase)

import psycopg2.extras
from database import get_connection
from datetime import datetime, date

def _dict_cursor(conn):
    """Return a cursor that yields rows as dicts."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# ─────────────────────────── USER / AUTH ───────────────────────────

def find_user(username, password):
    """Find user by username and password. Returns dict or None."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = _dict_cursor(conn)
        cur.execute(
            "SELECT id, username, role FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

def create_user(username, password, role='worker'):
    """Insert a new user into the users table."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[MODEL ERROR] create_user: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# ─────────────────────────── WORKERS ───────────────────────────

def create_worker(name, phone, contractor, shift, username, password):
    """Register a new worker (also creates user account)."""
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'worker')",
            (username, password)
        )
        cur.execute(
            """INSERT INTO workers (name, phone, contractor, shift, username, password)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, phone, contractor, shift, username, password)
        )
        conn.commit()
        return True, "Worker registered successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def get_all_workers():
    """Fetch all workers."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = _dict_cursor(conn)
        cur.execute("SELECT id, name, phone, contractor, shift, username, created_at FROM workers")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        cur.close()
        conn.close()

def get_worker_by_username(username):
    """Get worker record by username."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = _dict_cursor(conn)
        cur.execute(
            "SELECT id, name, phone, contractor, shift, username FROM workers WHERE username=%s",
            (username,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

def get_worker_by_id(worker_id):
    """Get worker record by ID."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = _dict_cursor(conn)
        cur.execute(
            "SELECT id, name, phone, contractor, shift, username FROM workers WHERE id=%s",
            (worker_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

# ─────────────────────────── ATTENDANCE ───────────────────────────

def mark_attendance(worker_id, check_in, check_out=None, status='present'):
    """Insert or update today's attendance record for a worker."""
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        today = date.today()
        working_hours = 0.0

        if check_in and check_out:
            fmt = "%H:%M"
            try:
                ci = datetime.strptime(check_in, fmt)
                co = datetime.strptime(check_out, fmt)
                working_hours = round((co - ci).seconds / 3600, 2)
            except Exception:
                working_hours = 0.0

        if check_in and status == 'present':
            try:
                if int(check_in.split(":")[0]) >= 9:
                    status = 'late'
            except Exception:
                pass

        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM attendance WHERE worker_id=%s AND date=%s",
            (worker_id, today)
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                """UPDATE attendance
                   SET check_in=%s, check_out=%s, status=%s, working_hours=%s
                   WHERE worker_id=%s AND date=%s""",
                (check_in, check_out, status, working_hours, worker_id, today)
            )
        else:
            cur.execute(
                """INSERT INTO attendance (worker_id, date, check_in, check_out, status, working_hours)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (worker_id, today, check_in, check_out, status, working_hours)
            )

        conn.commit()
        return True, "Attendance marked successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def get_attendance_history(worker_id, limit=30):
    """Fetch recent attendance records for a worker."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = _dict_cursor(conn)
        cur.execute(
            """SELECT a.*, w.name AS worker_name
               FROM attendance a
               JOIN workers w ON a.worker_id = w.id
               WHERE a.worker_id=%s
               ORDER BY a.date DESC
               LIMIT %s""",
            (worker_id, limit)
        )
        rows = cur.fetchall()
        result = []
        for row in rows:
            r = dict(row)
            r['date'] = str(r['date'])
            r['check_in'] = str(r['check_in']) if r['check_in'] else None
            r['check_out'] = str(r['check_out']) if r['check_out'] else None
            r['created_at'] = str(r['created_at'])
            result.append(r)
        return result
    finally:
        cur.close()
        conn.close()

def get_all_attendance_today():
    """Get today's attendance for all workers."""
    conn = get_connection()
    if not conn:
        return []
    try:
        today = date.today()
        cur = _dict_cursor(conn)
        cur.execute(
            """SELECT a.*, w.name, w.shift
               FROM attendance a
               JOIN workers w ON a.worker_id = w.id
               WHERE a.date=%s
               ORDER BY a.check_in""",
            (today,)
        )
        rows = cur.fetchall()
        result = []
        for row in rows:
            r = dict(row)
            r['date'] = str(r['date'])
            r['check_in'] = str(r['check_in']) if r['check_in'] else None
            r['check_out'] = str(r['check_out']) if r['check_out'] else None
            r['created_at'] = str(r['created_at'])
            result.append(r)
        return result
    finally:
        cur.close()
        conn.close()

def get_attendance_stats():
    """Return summary stats for admin dashboard."""
    conn = get_connection()
    if not conn:
        return {}
    try:
        today = date.today()
        cur = _dict_cursor(conn)

        cur.execute("SELECT COUNT(*) AS total FROM workers")
        total_workers = cur.fetchone()['total']

        cur.execute(
            "SELECT COUNT(*) AS present FROM attendance WHERE date=%s AND status IN ('present','late')",
            (today,)
        )
        today_present = cur.fetchone()['present']

        return {
            "total_workers": total_workers,
            "today_present": today_present,
            "today_absent": total_workers - today_present
        }
    finally:
        cur.close()
        conn.close()

def get_worker_attendance_summary(worker_id):
    """Get attendance percentage and summary for a specific worker."""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = _dict_cursor(conn)

        cur.execute("SELECT COUNT(*) AS total FROM attendance WHERE worker_id=%s", (worker_id,))
        total = cur.fetchone()['total'] or 1

        cur.execute(
            "SELECT COUNT(*) AS present FROM attendance WHERE worker_id=%s AND status IN ('present','late')",
            (worker_id,)
        )
        present = cur.fetchone()['present']

        cur.execute(
            "SELECT COALESCE(SUM(working_hours), 0) AS total_hours FROM attendance WHERE worker_id=%s",
            (worker_id,)
        )
        hours = cur.fetchone()['total_hours']

        return {
            "total_days": total,
            "present_days": present,
            "attendance_percentage": round((present / total) * 100, 1),
            "total_working_hours": float(hours)
        }
    finally:
        cur.close()
        conn.close()
