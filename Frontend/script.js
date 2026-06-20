// script.js - Shared Utilities for AI Attendance System

// ⚠️ Replace this URL with your actual Render backend URL after deploying
const API_BASE = 'https://ai-attendance-system-0v7b.onrender.com/api';

// ── Storage helpers ──
const Store = {
  set: (k, v) => localStorage.setItem(k, JSON.stringify(v)),
  get: (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  clear: () => localStorage.clear()
};

// ── Auth helpers ──
const Auth = {
  isLoggedIn: () => !!Store.get('user'),
  getUser: () => Store.get('user'),
  logout: async () => {
    try { await api.post('/logout'); } catch {}
    Store.clear();
    window.location.href = 'login.html';
  }
};

// ── API wrapper ──
const api = {
  _fetch: async (method, path, body) => {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include'
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Request failed');
    return data;
  },
  get:  (path)       => api._fetch('GET', path),
  post: (path, body) => api._fetch('POST', path, body),
};

// ── UI helpers ──
function showAlert(el, msg, type = 'danger') {
  if (!el) return;
  el.className = `alert alert-${type} show`;
  el.textContent = msg;
  if (type === 'success') setTimeout(() => el.classList.remove('show'), 4000);
}

function setLoading(btn, loading, text = 'Submit') {
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span class="spinner"></span> Please wait...`
    : text;
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}

function formatTime(timeStr) {
  if (!timeStr) return '-';
  // Handle HH:MM:SS from MySQL
  const parts = timeStr.split(':');
  const h = parseInt(parts[0]);
  const m = parts[1];
  const ampm = h >= 12 ? 'PM' : 'AM';
  return `${h % 12 || 12}:${m} ${ampm}`;
}

function statusBadge(status) {
  const map = {
    present: '<span class="badge badge-success">Present</span>',
    absent:  '<span class="badge badge-danger">Absent</span>',
    late:    '<span class="badge badge-warning">Late</span>',
    half_day:'<span class="badge badge-info">Half Day</span>'
  };
  return map[status] || `<span class="badge badge-secondary">${status}</span>`;
}

function riskBadge(risk) {
  const map = {
    Low:    '<span class="badge badge-success">Low</span>',
    Medium: '<span class="badge badge-warning">Medium</span>',
    High:   '<span class="badge badge-danger">High</span>',
    Unknown:'<span class="badge badge-secondary">Unknown</span>'
  };
  return map[risk] || `<span class="badge badge-secondary">${risk}</span>`;
}

// Animate attendance circle
function drawCircle(svgEl, pct) {
  const radius = 60;
  const circ = 2 * Math.PI * radius;
  const fg = svgEl.querySelector('.fg');
  fg.setAttribute('stroke-dasharray', circ);
  fg.setAttribute('stroke-dashoffset', circ - (pct / 100) * circ);
}

// Render sidebar user info
function renderSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;
  const nameEl = document.getElementById('sidebar-username');
  const roleEl = document.getElementById('sidebar-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (nameEl) nameEl.textContent = user.name || user.username;
  if (roleEl) roleEl.textContent = user.role === 'admin' ? 'Administrator' : 'Worker';
  if (avatarEl) avatarEl.textContent = (user.name || user.username || '?')[0].toUpperCase();
}

// Guard: redirect if not logged in or wrong role
function requireAuth(role) {
  const user = Auth.getUser();
  if (!user) { window.location.href = 'login.html'; return null; }
  if (role && user.role !== role) {
    window.location.href = user.role === 'admin' ? 'admin_dashboard.html' : 'worker_dashboard.html';
    return null;
  }
  return user;
}

// Logout button binding
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', Auth.logout);
  renderSidebarUser();
});
