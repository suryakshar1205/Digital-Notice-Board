from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
# For development (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noticeboard.db'

# For production (uncomment and configure one of these)
# PostgreSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/noticeboard')
# MySQL
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://username:password@localhost/noticeboard')

# Additional database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    holiday_name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    affected_sections = db.Column(db.Text)  # JSON string of affected sections, null means all sections

def init_db():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create default admin if it doesn't exist
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            # Use the password from environment variable or a default
            password = os.environ.get('ADMIN_PASSWORD', 'admin123456789')
            admin.password_hash = generate_password_hash(password)
            db.session.add(admin)
            db.session.commit()
            print(f'Created default admin account with username: admin and password: {password}')
            print('Please change the admin password after first login')
        else:
            print('Admin account already exists')

if __name__ == '__main__':
    # Ensure upload directories exist
    os.makedirs('static/uploads/notices', exist_ok=True)
    os.makedirs('static/uploads/timetables', exist_ok=True)
    
    # Initialize database
    init_db()
    print('Database initialized successfully')
