📚 Digital Notice Board and Timetable Management System
A comprehensive Flask-based web application for educational institutions to efficiently manage notices, timetables, holidays, and student queries through an interactive chatbot interface.

🚀 Features
📢 Notice Management: Upload, categorize, preview & manage notices.

🗓️ Timetable Management: Multi-section uploads with real-time class tracking.

🎉 Holiday Management: Section-specific holiday display & chatbot awareness.

💬 Chatbot Assistant: JavaScript-based chatbot for instant responses.

📄 PDF Viewer: Embedded previews for uploaded notices.

🔐 Admin Dashboard: Secure panel with CRUD capabilities.

⚙️ Tech Stack
Layer	Tools/Libraries
Backend	Flask, SQLAlchemy, Flask-Migrate, bcrypt
Frontend	HTML5, CSS3, JavaScript, Bootstrap 5, Jinja2
Database	SQLite (dev) / PostgreSQL or MySQL (prod)
File Tools	Pandas, OpenPyXL
Security	Flask-WTF, CSRF protection, Rate Limiting

🧭 System Overview
css
Copy
Edit
[User Interface] ⇄ [Flask Server] ⇄ [Database]
        ↑                ↑             ↑
   [Chatbot JS]     [File Processor] [Holiday Logic]
Database Schema includes: Admin, Notice, Timetable, Holiday

🛠️ Installation
Clone Repository
git clone https://github.com/your-repo/notice-board.git && cd notice-board

Setup Virtual Environment

bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate (Windows)
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure Environment
Create a .flaskenv:

ini
Copy
Edit
FLASK_APP=app.py
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret
ADMIN_PASSWORD=your-admin-password
DATABASE_URL=sqlite:///instance/noticeboard.db
Initialize Database

bash
Copy
Edit
python init_db.py
flask db upgrade
Run App

bash
Copy
Edit
flask run
🌐 Deployment (Render/Gunicorn)
Add to requirements.txt:

nginx
Copy
Edit
gunicorn
Create Procfile:

makefile
Copy
Edit
web: gunicorn app:app
Environment Variables (on Render):

FLASK_ENV=production

DATABASE_URL=your_postgres_url

FLASK_SECRET_KEY=your_secret

ADMIN_PASSWORD=your_password

🔒 Security Highlights
bcrypt password hashing

CSRF tokens on all forms

Rate-limited login (5 attempts per 15 mins)

File type validation & secure upload paths

🧪 Testing
test_sections.py: Verifies section display logic

debug_holidays.py: Checks holiday activation

Manual checklist: Notices, Timetables, Chatbot, Security flows

📌 Roadmap
 REST API for mobile apps

 Push/email notifications

 Dark mode & accessibility support

 Raspberry Pi deployment for physical boards

📄 License
This project is licensed under the MIT License.
See LICENSE for more details.

