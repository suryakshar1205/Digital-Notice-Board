# 🖥️ Digital Notice Board and Timetable Management System

A complete Flask-based web application for educational institutions to manage **academic notices, timetables, holidays**, and student queries through an **interactive chatbot interface**.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [Development Workflow](#development-workflow)
- [File Structure](#file-structure)
- [API Reference](#api-reference)
- [Security Considerations](#security-considerations)
- [Deployment Guide](#deployment-guide)
- [Testing & Debugging](#testing--debugging)
- [Future Improvements](#future-improvements)
- [Changelog](#changelog)
- [License](#license)

---

## 📌 Overview

The system offers:

- 📢 Notice Management with categorization and attachments  
- 🗓️ Timetable Uploads with real-time class tracking  
- 🎉 Holiday Scheduling with section-wise views  
- 🤖 Chatbot Assistant for student interaction  
- 📄 PDF Viewer for inline previews  
- 🔐 Admin Dashboard for total control  

Built with modern tech:

- **Backend**: Flask 2.2.5, SQLAlchemy, Flask-Migrate  
- **Frontend**: HTML5, CSS3, Bootstrap 5, JS  
- **Database**: SQLite / PostgreSQL  
- **Security**: Flask-WTF, bcrypt, CSRF, rate limiting  

---

## ✨ Features

### 1. Notice Management

- Create, edit, preview, and delete notices
- Attach PDF/DOC/TXT files
- Preview documents inline

### 2. Timetable Management

- Upload Excel/CSV for multi-section class schedules
- Real-time "Current/Upcoming" class tracking
- Section-specific views

### 3. Holiday Management

- Create, activate/deactivate holidays
- Section-specific display
- Chatbot auto-detects holidays

### 4. Chatbot Assistant

- Handles queries on notices, holidays, and classes
- Works using JavaScript + keyword matching

### 5. Admin Dashboard

- Full CRUD for notices, timetables, and holidays
- Session-based login authentication
- File upload/download preview with validation

---

## 🧠 System Architecture

[User Interface] ⇄ [Flask Server] ⇄ [Database]
↑ ↑ ↑
[Chatbot JS] [File Processor] [Holiday Logic]

yaml
Copy
Edit

---

## ⚙️ Installation & Setup

### 🔧 Prerequisites

- Python 3.8+
- pip
- SQLite (dev) / PostgreSQL or MySQL (prod)

### 🏗️ Steps

```bash
# 1. Clone Repository
git clone https://github.com/<your-username>/Digital-Notice-Board.git
cd Digital-Notice-Board

# 2. Setup Virtual Environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate (Windows)

# 3. Install Requirements
pip install -r requirements.txt

# 4. Initialize Database
python init_db.py
flask db upgrade

# 5. Run Server
flask run
🛠️ Development Workflow
bash
Copy
Edit
# Migrate DB
flask db migrate -m "Add feature"
flask db upgrade

# Run Tests
python test_sections.py
python debug_holidays.py
📁 File Structure
bash
Copy
Edit
📦 Digital-Notice-Board/
├── app.py              # Main Flask App
├── init_db.py          # DB Initialization Script
├── static/             # CSS, JS, Uploads
├── templates/          # Jinja2 HTML Templates
├── migrations/         # Flask-Migrate Files
├── instance/           # SQLite DB
└── test/               # Unit Testing Scripts
🔌 API Reference
Endpoint	Description
/login	Admin authentication
/admin	Dashboard
/notices	View notices
/upload_notice	Upload notice file
/preview_pdf/<filename>	View PDF
/upload_timetable	Upload timetable
/add_holiday	Add holiday

🔐 Security Considerations
Password Hashing (bcrypt)

CSRF Protection

Rate Limiting (Login)

Session Timeout (30 mins)

File Validation (only .pdf, .docx, .txt etc.)

XSS & SQL Injection protection (via ORM and Flask-WTF)

🌍 Deployment Guide (Render or VPS)
Add to requirements.txt:

nginx
Copy
Edit
gunicorn
Create a Procfile:

makefile
Copy
Edit
web: gunicorn app:app
Push to GitHub and connect to Render or Railway

Set environment variables like:

ini
Copy
Edit
FLASK_ENV=production
FLASK_SECRET_KEY=...
DATABASE_URL=...
🧪 Testing & Debugging
Type	Script
Sections	test_sections.py
Holidays	debug_holidays.py
Manual UI	Notice Upload, Timetable Preview, Chatbot Queries
