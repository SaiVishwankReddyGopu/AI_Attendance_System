-- ============================================================
-- AI Attendance Management System - Database Setup Script
-- Run: mysql -u root -p < database_setup.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- Users table (authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('worker', 'admin') NOT NULL DEFAULT 'worker',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workers table (profiles)
CREATE TABLE IF NOT EXISTS workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    contractor VARCHAR(150),
    shift ENUM('morning', 'afternoon', 'night') DEFAULT 'morning',
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    date DATE NOT NULL,
    check_in TIME,
    check_out TIME,
    status ENUM('present', 'absent', 'late', 'half_day') DEFAULT 'present',
    working_hours DECIMAL(4,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- Default admin account
INSERT IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

-- Sample workers for testing
INSERT IGNORE INTO users (username, password, role) VALUES
    ('ramesh123', 'pass123', 'worker'),
    ('suresh456', 'pass123', 'worker'),
    ('priya789',  'pass123', 'worker');

INSERT IGNORE INTO workers (name, phone, contractor, shift, username, password) VALUES
    ('Ramesh Kumar',  '9876543210', 'ABC Contractors', 'morning',   'ramesh123', 'pass123'),
    ('Suresh Singh',  '9876543211', 'XYZ Builders',    'afternoon', 'suresh456', 'pass123'),
    ('Priya Devi',    '9876543212', 'ABC Contractors', 'morning',   'priya789',  'pass123');

-- Sample attendance records
INSERT IGNORE INTO attendance (worker_id, date, check_in, check_out, status, working_hours) VALUES
    (1, CURDATE() - INTERVAL 1 DAY, '07:55', '16:05', 'present', 8.2),
    (1, CURDATE() - INTERVAL 2 DAY, '08:02', '16:00', 'present', 7.9),
    (1, CURDATE() - INTERVAL 3 DAY, '09:15', '16:00', 'late',    6.8),
    (2, CURDATE() - INTERVAL 1 DAY, '14:00', '22:05', 'present', 8.1),
    (2, CURDATE() - INTERVAL 2 DAY, '14:30', '22:00', 'late',    7.5),
    (3, CURDATE() - INTERVAL 1 DAY, '07:50', '16:00', 'present', 8.2),
    (3, CURDATE() - INTERVAL 2 DAY, NULL,    NULL,    'absent',  0.0);

SELECT 'Database setup complete!' AS status;
SELECT 'Default Admin: username=admin, password=admin123' AS info;
