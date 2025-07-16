from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, send_file
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
from sqlalchemy import desc as sa_desc
from functools import wraps
from dotenv import load_dotenv
from markupsafe import Markup
import os
import json
import pytz
import logging
import re
from math import ceil
from fuzzywuzzy import fuzz
import mimetypes
import gc
import pandas as pd
from io import BytesIO

# Custom JSON encoder to handle time objects
class TimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%I:%M %p')
        return super().default(obj)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CSRF protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')  # Use the same key as Flask
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add custom Jinja2 filter for safe JSON parsing
@app.template_filter('parse_json')
def parse_json_filter(value):
    try:
        if not value:
            return []
            
        # If it's already a list or dict, return it
        if isinstance(value, (list, dict)):
            return value
            
        # Try to parse the JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in parse_json filter: {str(e)}")
            # Try to fix the JSON
            try:
                # Remove any invalid characters
                cleaned_data = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
                # Try to parse again
                return json.loads(cleaned_data)
            except Exception as fix_error:
                logger.error(f"Failed to fix JSON in parse_json filter: {str(fix_error)}")
                return []
    except Exception as e:
        logger.error(f"Error in parse_json filter: {str(e)}")
        return []

# Set timezone for India (moved up before usage)
TIMEZONE = pytz.timezone('Asia/Kolkata')

def make_timezone_aware(dt):
    """Convert naive datetime to timezone-aware datetime"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return TIMEZONE.localize(dt)
    return dt

def is_notice_expired(notice, current_time=None):
    """Safely check if a notice is expired"""
    if not notice.expiration_date:
        return False
    
    if current_time is None:
        current_time = datetime.now(TIMEZONE)
    
    # Make both dates timezone-aware
    expiration_date = make_timezone_aware(notice.expiration_date)
    current_time = make_timezone_aware(current_time)
    
    return expiration_date < current_time

# Add context processor to make current_year available in all templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now(TIMEZONE).year}

# Security configurations with environment variables
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)

# Use strong secret key from environment variable
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)

# Use environment variable for admin credentials
DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', os.urandom(16).hex())
if 'ADMIN_PASSWORD' in os.environ and len(os.environ['ADMIN_PASSWORD']) < 12:
    raise ValueError("Admin password must be at least 12 characters when provided")

# Enhanced session security
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',  # Changed from Lax to Strict
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True  # Reset timeout on each request
)

# File upload security enhancements
def validate_file_content(file_stream, allowed_extensions):
    """Enhanced file content validation using mimetypes"""
    try:
        # Get the original filename from the file stream
        filename = file_stream.filename
        if not filename:
            return False
            
        # Guess the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            return False
        
        mime_mappings = {
            'text/csv': ['csv'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['xlsx'],
            'application/vnd.ms-excel': ['xls'],
            'application/pdf': ['pdf'],
            'text/plain': ['txt'],
            'application/msword': ['doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/gif': ['gif']
        }
        
        for mime_pattern, extensions in mime_mappings.items():
            if mime_type.startswith(mime_pattern) and any(ext in allowed_extensions for ext in extensions):
                return True
        
        return False
    except Exception as e:
        logging.error(f"Error validating file content: {str(e)}", exc_info=True)
        return False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noticeboard.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size



# Ensure upload directories exist
NOTICES_UPLOAD_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'notices')
TIMETABLES_UPLOAD_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'timetables')
os.makedirs(NOTICES_UPLOAD_PATH, exist_ok=True)
os.makedirs(TIMETABLES_UPLOAD_PATH, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'notice': {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'},
    'timetable': {'xlsx', 'xls', 'csv'}  # Added CSV support
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Notice(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(200), nullable=False)
    description: str | None = db.Column(db.Text)
    filename: str | None = db.Column(db.String(200))
    photo_filename: str | None = db.Column(db.String(200))  # New field for photos
    upload_date: datetime = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE))
    expiration_date: datetime | None = db.Column(db.DateTime)
    is_active: bool = db.Column(db.Boolean, default=True)
    category: str | None = db.Column(db.String(50))
    author_id: int | None = db.Column(db.Integer, db.ForeignKey('admin.id'))
    author = db.relationship('Admin', backref='notices')
    
    def is_expired(self, current_time=None):
        """Check if notice is expired using safe timezone comparison"""
        return is_notice_expired(self, current_time)

class Timetable(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(200), nullable=False)
    filename: str | None = db.Column(db.String(200))
    upload_date: datetime = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE))
    is_active: bool = db.Column(db.Boolean, default=True)
    schedule_data: str | None = db.Column(db.Text)  # JSON string of processed schedule with sections
    sections: str | None = db.Column(db.Text)  # JSON string of available sections

class Holiday(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    holiday_name: str = db.Column(db.String(200), nullable=False)
    start_date: datetime = db.Column(db.Date, nullable=False)
    end_date: datetime = db.Column(db.Date, nullable=False)
    description: str | None = db.Column(db.Text)
    created_date: datetime = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE))
    is_active: bool = db.Column(db.Boolean, default=True)
    affected_sections: str | None = db.Column(db.Text)  # JSON string of affected sections, null means all sections

    def is_current_holiday(self):
        """Check if current date falls within this holiday period"""
        today = datetime.now(TIMEZONE).date()
        return self.start_date <= today <= self.end_date
    
    def affects_section(self, section_name):
        """Check if this holiday affects a specific section"""
        logger.info(f"Checking if holiday '{self.holiday_name}' affects section '{section_name}'")
        logger.info(f"Holiday affected_sections: '{self.affected_sections}'")
        
        if not self.affected_sections:
            logger.info(f"No specific sections set, affecting all sections")
            return True  # If no sections specified, affects all sections
        
        try:
            sections = json.loads(self.affected_sections)
            logger.info(f"Parsed sections: {sections}")
            logger.info(f"Section name to check: '{section_name}'")
            logger.info(f"Section name type: {type(section_name)}")
            
            # Check for exact match first
            if section_name in sections:
                logger.info(f"Exact match found for section '{section_name}'")
                return True
            
            # Check for case-insensitive match
            section_name_lower = section_name.lower() if section_name else ""
            sections_lower = [s.lower() for s in sections if s]
            
            if section_name_lower in sections_lower:
                logger.info(f"Case-insensitive match found for section '{section_name}'")
                return True
            
            logger.info(f"No match found for section '{section_name}'")
            return False
            
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing affected_sections JSON: {str(e)}")
            return True  # If JSON parsing fails, assume it affects all sections

def get_current_holiday(section_name=None):
    """Get the current holiday if any, optionally filtered by section"""
    today = datetime.now(TIMEZONE).date()
    logger.info(f"Checking for holidays on {today} for section: '{section_name}'")
    
    current_holidays = Holiday.query.filter(
        Holiday.is_active == True,
        Holiday.start_date <= today,
        Holiday.end_date >= today
    ).all()
    
    logger.info(f"Found {len(current_holidays)} active holidays for today")
    
    if not current_holidays:
        logger.info("No active holidays found")
        return None
    
    # If no section specified, return the first holiday (affects all sections)
    if not section_name:
        logger.info(f"No section specified, returning first holiday: {current_holidays[0].holiday_name}")
        return current_holidays[0]
    
    # Check for holidays that affect the specific section
    for holiday in current_holidays:
        logger.info(f"Checking holiday: {holiday.holiday_name}")
        if holiday.affects_section(section_name):
            logger.info(f"Holiday '{holiday.holiday_name}' affects section '{section_name}'")
            return holiday
        else:
            logger.info(f"Holiday '{holiday.holiday_name}' does NOT affect section '{section_name}'")
    
    logger.info(f"No holidays found that affect section '{section_name}'")
    return None

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

# Enhanced pattern detection
DAY_PATTERNS = [
    r'(day|week|mon(day)?|tue(sday)?|wed(nesday)?|thu(rsday)?|fri(day)?|sat(urday)?|sun(day)?)',
    r'(m|t|w|th|f|s|su)\.?'
]
TIME_PATTERNS = [
    r'(time|period|hour|schedule|slot|from|to)',
    r'(start|end)\s*time',
    r'\d{1,2}[:\.]\d{2}\s*(?:[ap]m)?'
]
SUBJECT_PATTERNS = [
    r'(subject|course|class|paper|lecture|topic|module)',
    r'(title|name|description)',
    r'[a-z]{3,}'
]
ROOM_PATTERNS = [
    r'(room|hall|venue|location|place|lab|theater|block|building)',
    r'(room|venue)\s*no',
    r'[a-z\d]+\s*(?:lab|room|hall)'
]

def detect_column_type(df, column_index):
    """Enhanced column type detection using fuzzy matching"""
    col_data = df.iloc[:, column_index].astype(str).str.lower()
    header = str(df.columns[column_index]).lower() if hasattr(df, 'columns') else ""
    
    # Check header with fuzzy matching
    for pattern_list, col_type in [
        (DAY_PATTERNS, 'day'),
        (TIME_PATTERNS, 'time'),
        (SUBJECT_PATTERNS, 'subject'),
        (ROOM_PATTERNS, 'room')
    ]:
        for pattern in pattern_list:
            match = re.search(pattern, header, re.IGNORECASE)
            if match and fuzz.partial_ratio(match.group(0), header) > 80:
                return col_type
    
    # Count matches in data with improved pattern matching
    pattern_counts = {
        'day': sum(1 for val in col_data if any(re.search(pattern, val, re.IGNORECASE) for pattern in DAY_PATTERNS)),
        'time': sum(1 for val in col_data if any(re.search(pattern, val, re.IGNORECASE) for pattern in TIME_PATTERNS)),
        'subject': sum(1 for val in col_data if any(re.search(pattern, val, re.IGNORECASE) for pattern in SUBJECT_PATTERNS)),
        'room': sum(1 for val in col_data if any(re.search(pattern, val, re.IGNORECASE) for pattern in ROOM_PATTERNS))
    }
    
    max_count = max(pattern_counts.values())
    if max_count == 0:
        return 'unknown'
    
    return max(pattern_counts.items(), key=lambda x: x[1])[0]

def parse_time(time_str):
    """Enhanced time parsing with range support"""
    if not time_str or pd.isna(time_str):
        return None
    
    time_str = str(time_str).strip().upper().replace('  ', ' ')
    if not time_str or time_str.lower() in ['nan', 'null', 'none', 'n/a']:
        return None
    
    # Try to extract time range
    time_range_match = re.search(
        r'(\d{1,2}[:\.]?\d{0,2}(?:\s*[ap]m)?)[\s-]*[-]?\s*(\d{1,2}[:\.]?\d{0,2}(?:\s*[ap]m)?)',
        time_str,
        re.IGNORECASE
    )
    if time_range_match:
        start_time_str = time_range_match.group(1)
        end_time_str = time_range_match.group(2)
        start_time = _parse_single_time(start_time_str)
        end_time = _parse_single_time(end_time_str)
        if start_time and end_time:
            return (start_time, end_time)
    
    return _parse_single_time(time_str)

def _parse_single_time(time_str):
    """Helper function for parsing individual time values"""
    # Clean up the time string by removing leading/trailing spaces and dashes
    time_str = time_str.strip()
    if time_str.startswith('-'):
        time_str = time_str[1:].strip()
    
    time_patterns = [
        '%H:%M', '%H.%M', '%H:%M:%S', '%H.%M.%S',
        '%I:%M %p', '%I:%M%p', '%I.%M %p', '%I %p', '%I:%M:%S %p',
        '%Hh%M', '%H:%M hrs', '%H hrs', '%H%M', '%I%M%p', '%I:%M', '%I.%M'
    ]
    
    for fmt in time_patterns:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    
    try:
        if isinstance(time_str, (int, float)) or time_str.replace('.', '', 1).isdigit():
            time_value = float(time_str)
            if 0 <= time_value < 1:
                hours = int(time_value * 24)
                minutes = int((time_value * 24 * 60) % 60)
                return time(hours, minutes)
            elif 0 <= time_value <= 24:
                hours = int(time_value)
                minutes = int((time_value - hours) * 60)
                return time(hours % 24, minutes)
    except (ValueError, TypeError):
        pass
    
    return None

def normalize_day(day_str):
    """Normalize day names with improved logging"""
    if not day_str or pd.isna(day_str):
        return None
        
    day_str = str(day_str).strip().lower()
    logger.debug(f"Normalizing day: {day_str}")
    
    if not day_str or day_str.lower() in ['nan', 'null', 'none', 'n/a']:
        return None
    
    day_mapping = {
        'mon': 'Monday', 'm': 'Monday', '1': 'Monday', 'monday': 'Monday',
        'tue': 'Tuesday', 'tues': 'Tuesday', 't': 'Tuesday', '2': 'Tuesday', 'tuesday': 'Tuesday',
        'wed': 'Wednesday', 'w': 'Wednesday', '3': 'Wednesday', 'wednesday': 'Wednesday',
        'thu': 'Thursday', 'thur': 'Thursday', 'thurs': 'Thursday', 'th': 'Thursday', '4': 'Thursday', 'thursday': 'Thursday',
        'fri': 'Friday', 'f': 'Friday', '5': 'Friday', 'friday': 'Friday',
        'sat': 'Saturday', 's': 'Saturday', '6': 'Saturday', 'saturday': 'Saturday',
        'sun': 'Sunday', 'su': 'Sunday', '0': 'Sunday', '7': 'Sunday', 'sunday': 'Sunday'
    }
    
    if day_str in day_mapping:
        normalized = day_mapping[day_str]
        logger.debug(f"Normalized {day_str} to {normalized} (direct match)")
        return normalized
    
    for abbr, full_day in day_mapping.items():
        if day_str.startswith(abbr) or abbr in day_str:
            logger.debug(f"Normalized {day_str} to {full_day} (partial match)")
            return full_day
    
    try:
        day_num = int(float(day_str))
        if 0 <= day_num <= 7:
            days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            normalized = days_of_week[day_num % 7]
            logger.debug(f"Normalized {day_str} to {normalized} (numeric)")
            return normalized
    except (ValueError, TypeError):
        pass
    
    logger.debug(f"Could not normalize day: {day_str}")
    return None

def process_timetable(file_path):
    """Process the timetable file and return the schedule data."""
    try:
        logger.info(f"Starting to process timetable file: {file_path}")
        
        # Read the file based on its type
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Processing file with extension: {file_ext}")
        
        if file_ext == '.csv':
            logger.info("Reading CSV file")
            df = pd.read_csv(file_path)
            # For CSV, treat as a single sheet with default section
            schedule = process_single_sheet(df, "Default")
            return json.dumps({"Default": schedule}), json.dumps(["Default"])
            
        elif file_ext in ['.xlsx', '.xls']:
            logger.info("Reading Excel file")
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            logger.info(f"Found sheets: {sheets}")
            
            if not sheets:
                logger.error("No sheets found in Excel file")
                raise ValueError("No sheets found in Excel file")
            
            # Process each sheet
            all_schedules = {}
            sections = []
            
            for sheet in sheets:
                logger.info(f"Processing sheet: {sheet}")
                df = pd.read_excel(file_path, sheet_name=sheet)
                logger.info(f"Sheet shape: {df.shape}")
                logger.info(f"Sheet columns: {df.columns.tolist()}")
                
                # Extract section from sheet name if possible
                section = sheet.strip()
                sections.append(section)
                
                # Process the schedule for this sheet
                schedule = process_single_sheet(df, section)
                if schedule:  # Only add if there's valid data
                    all_schedules[section] = schedule
            
            if not all_schedules:
                logger.error("No valid schedule entries could be created from any sheet")
                raise ValueError("No valid schedule entries could be created from any sheet")
            
            logger.info(f"Successfully processed {len(all_schedules)} sections")
            return json.dumps(all_schedules), json.dumps(sections)
            
        else:
            logger.error(f"Unsupported file type: {file_ext}")
            raise ValueError("Unsupported file type")
        
    except Exception as e:
        logger.error(f"Error processing timetable: {str(e)}", exc_info=True)
        raise ValueError(f"Error processing timetable: {str(e)}")

def process_single_sheet(df: pd.DataFrame, section_name: str) -> list:
    """Process a single sheet of the timetable and return the schedule for that section"""
    schedule = []
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Standardize column names and log them
    df.columns = [col.strip().lower() for col in df.columns]
    logger.info(f"Available columns in sheet for section {section_name}: {df.columns.tolist()}")
    
    # Map expected columns with more flexible matching
    column_mapping = {}
    # Prioritize exact match for PROFESSOR/FACULTY NAME
    faculty_patterns = ['PROFESSOR/FACULTY NAME']  # First try exact match
    faculty_fallback_patterns = ['professor/faculty name', 'professor', 'faculty name', 'faculty', 'teacher', 'instructor', 'professor/faculty']
    
    column_patterns = [
        ('day', ['day', 'weekday', 'day of week']),
        ('start', ['start', 'begin', 'from', 'start time', 'begin time']),
        ('end', ['end', 'finish', 'to', 'end time', 'finish time']),
        ('subject', ['subject', 'course', 'class', 'paper', 'lecture']),
        ('room', ['room', 'venue', 'location', 'hall', 'classroom']),
        ('faculty', faculty_patterns)
    ]
    
    # Log all column names for debugging
    logger.info("Available columns in Excel:")
    for col in df.columns:
        logger.info(f"Column found: '{col}'")
    
    # First try exact match for faculty column
    faculty_col = None
    for col in df.columns:
        logger.info(f"Checking column: '{col}' for faculty match")
        if col == 'PROFESSOR/FACULTY NAME':
            faculty_col = col
            logger.info(f"Found exact match for PROFESSOR/FACULTY NAME column: '{col}'")
            break
    
    # If no exact match found, try case-insensitive match
    if not faculty_col:
        for col in df.columns:
            if 'professor/faculty name' in col.lower():
                faculty_col = col
                logger.info(f"Found case-insensitive match for faculty column: '{col}'")
                break
    
    # If still no match, try other patterns
    if not faculty_col:
        faculty_patterns = ['professor', 'faculty', 'teacher', 'instructor']
        for col in df.columns:
            if any(pattern in col.lower() for pattern in faculty_patterns):
                faculty_col = col
                logger.info(f"Found faculty column using pattern match: '{col}'")
                break
    
    if faculty_col:
        column_mapping['faculty'] = faculty_col
        logger.info(f"Set faculty column mapping to: '{faculty_col}'")
    else:
        logger.warning("No faculty column found in the Excel file")
    
    # Process other columns
    for col_type, patterns in column_patterns:
        if col_type != 'faculty':  # Skip faculty as we handled it separately
            matches = []
            for col in df.columns:
                if any(pattern in col.lower() for pattern in patterns):
                    matches.append(col)
                    logger.info(f"Matched {col_type} column: '{col}' using patterns: {patterns}")
            
            if matches:
                column_mapping[col_type] = matches[0]
            else:
                logger.warning(f"No column found matching {col_type} patterns")
                if col_type not in ['faculty']:
                    return []
    
    logger.info(f"Final column mapping: {column_mapping}")
    
    # Process each row
    for idx, row in df.iterrows():
        try:
            # Get and normalize day
            day = normalize_day(str(row[column_mapping['day']]))
            if not day:
                continue
            
            # Process start and end times
            start_time = row[column_mapping['start']]
            end_time = row[column_mapping['end']]
            
            # Handle faculty information with detailed logging
            faculty = 'Not assigned'
            if 'faculty' in column_mapping:
                try:
                    faculty_col = column_mapping['faculty']
                    faculty_val = row[faculty_col]
                    logger.info(f"Row {idx} - Processing faculty value:")
                    logger.info(f"  Column: '{faculty_col}'")
                    logger.info(f"  Raw value: '{faculty_val}'")
                    logger.info(f"  Type: {type(faculty_val)}")
                    
                    # Convert to string and clean
                    if pd.notna(faculty_val):
                        faculty = str(faculty_val).strip()
                        logger.info(f"  Cleaned value: '{faculty}'")
                        
                        # Check for invalid values
                        invalid_values = ['nan', 'none', 'null', 'n/a', 'not assigned', '', '-', 'na']
                        if not faculty or faculty.lower() in invalid_values:
                            faculty = 'Not assigned'
                            logger.info(f"  Value considered invalid, set to: '{faculty}'")
                        else:
                            logger.info(f"  Valid faculty name found: '{faculty}'")
                    else:
                        logger.info("  Value is NaN, set to: 'Not assigned'")
                        faculty = 'Not assigned'
                except Exception as e:
                    logger.error(f"Row {idx} - Error processing faculty: {str(e)}", exc_info=True)
                    faculty = 'Not assigned'
            
            # Convert times to string format
            try:
                if hasattr(start_time, 'strftime'):
                    start_time_str = start_time.strftime('%I:%M %p')
                else:
                    start_time_str = pd.to_datetime(start_time).strftime('%I:%M %p')
            except:
                start_time_str = str(start_time)
            
            try:
                if hasattr(end_time, 'strftime'):
                    end_time_str = end_time.strftime('%I:%M %p')
                else:
                    end_time_str = pd.to_datetime(end_time).strftime('%I:%M %p')
            except:
                end_time_str = str(end_time)
            
            # Remove leading zeros
            start_time_str = start_time_str.lstrip('0')
            end_time_str = end_time_str.lstrip('0')
            
            # Format the time range
            time_str = f"{start_time_str} - {end_time_str}"
            
            # Get subject and room
            subject = str(row[column_mapping['subject']]).strip()
            room = str(row[column_mapping['room']]).strip()
            
            if not subject:  # Skip if no subject
                continue
            
            entry = {
                'day': day,
                'time': time_str,
                'subject': subject,
                'room': room,
                'faculty': faculty,
                'section': section_name,
                'start_time': start_time_str,
                'end_time': end_time_str
            }
            logger.info(f"Created entry: {entry}")
            schedule.append(entry)
            
        except Exception as e:
            logger.error(f"Error processing row {idx} in section {section_name}: {str(e)}", exc_info=True)
            continue
    
    # Sort schedule by day and start time
    def sort_key(entry):
        day_idx = days_order.index(entry['day']) if entry['day'] in days_order else 999
        try:
            time_obj = datetime.strptime(entry['start_time'], '%I:%M %p').time()
        except:
            time_obj = time(0, 0)  # Default to midnight if time parsing fails
        return (day_idx, time_obj)
    
    schedule.sort(key=sort_key)
    
    # Remove the extra time fields before returning
    for entry in schedule:
        entry.pop('start_time', None)
        entry.pop('end_time', None)
    
    logger.info(f"Final schedule for section {section_name}: {schedule}")
    return schedule

def get_section_classes(schedule_data, section=None):
    """Get classes for a specific section or all sections if none specified"""
    if not schedule_data:
        logger.error("No schedule data provided")
        return [], []
    
    try:
        # Parse the schedule data
        schedule = json.loads(schedule_data)
        logger.info(f"Processing schedule data for sections: {list(schedule.keys())}")
        
        now = datetime.now(TIMEZONE)
        current_day = now.strftime('%A')
        current_time = now.time()
        
        logger.info(f"Current day: {current_day}, Current time: {current_time.strftime('%I:%M %p')}")
        
        # Initialize lists for all sections
        current_classes = []
        upcoming_classes = []
        
        # Process each section's schedule
        for section_name, section_schedule in schedule.items():
            if section and section_name != section:
                continue
                
            logger.info(f"Processing section: {section_name}")
            section_current = []
            section_upcoming = []
            
            # Process each class in the section
            for cls in section_schedule:
                try:
                    if cls['day'] != current_day:
                        continue
                        
                    time_range = cls['time'].split(' - ')
                    if len(time_range) != 2:
                        logger.error(f"Invalid time range format for class: {cls}")
                        continue
                        
                    start_time_str = time_range[0].strip()
                    end_time_str = time_range[1].strip()
                    
                    # Parse times
                    try:
                        start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
                        end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                    except ValueError as e:
                        logger.error(f"Error parsing time for class in section {section_name}: {str(e)}")
                        continue
                    
                    # Calculate minutes for current time and class times
                    now_minutes = current_time.hour * 60 + current_time.minute
                    start_minutes = start_time.hour * 60 + start_time.minute
                    end_minutes = end_time.hour * 60 + end_time.minute
                    
                    # Create base class info
                    class_info = {
                        'subject': cls['subject'],
                        'day': current_day,
                        'time': cls['time'],
                        'room': cls['room'],
                        'section': section_name,
                        'faculty': cls.get('faculty', 'Not assigned')
                    }
                    
                    # Class is current if it's ongoing
                    if start_minutes <= now_minutes < end_minutes:
                        time_remaining = end_minutes - now_minutes
                        total_duration = end_minutes - start_minutes
                        
                        section_current.append({
                            **class_info,
                            'status': 'ongoing',
                            'time_remaining': time_remaining * 60,
                            'total_duration': total_duration * 60,
                            'time_remaining_str': (
                                f"{time_remaining} minutes" if time_remaining < 60
                                else f"{time_remaining / 60:.1f} hours"
                            )
                        })
                        
                    # Class is upcoming if it's later today
                    elif start_minutes > now_minutes:
                        time_until = start_minutes - now_minutes
                        section_upcoming.append({
                            **class_info,
                            'status': 'upcoming',
                            'time_until': time_until * 60,
                            'time_until_str': (
                                f"{time_until} minutes" if time_until < 60
                                else f"{time_until / 60:.1f} hours"
                            )
                        })
                    
                except Exception as e:
                    logger.error(f"Error processing class in section {section_name}: {str(e)}", exc_info=True)
                    continue
            
            # Add no-classes placeholder if needed
            if not section_current:
                section_current.append({
                    'subject': 'No Current Classes',
                    'day': current_day,
                    'time': 'N/A',
                    'room': 'N/A',
                    'section': section_name,
                    'faculty': 'Not assigned',
                    'status': 'no-classes'
                })
            
            if not section_upcoming:
                section_upcoming.append({
                    'subject': 'No Upcoming Classes',
                    'day': current_day,
                    'time': 'N/A',
                    'room': 'N/A',
                    'section': section_name,
                    'faculty': 'Not assigned',
                    'status': 'no-classes'
                })
            
            # Add section classes to main lists
            current_classes.extend(section_current)
            upcoming_classes.extend(section_upcoming)
        
        # Sort classes by section and time
        current_classes.sort(key=lambda x: (x['section'], x.get('time', '')))
        upcoming_classes.sort(key=lambda x: (x['section'], x.get('time', '')))
        
        return current_classes, upcoming_classes
        
    except Exception as e:
        logger.error(f"Error in get_section_classes: {str(e)}", exc_info=True)
        return [], []

@app.route('/section/<section_name>')
def section_view(section_name):
    latest_timetable = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).first()
    
    # Check for current holiday
    current_holiday = get_current_holiday(section_name)
    
    current_classes = []
    upcoming_classes = []
    sections = []
    
    if latest_timetable and not current_holiday:
        try:
            current_classes, upcoming_classes = get_section_classes(latest_timetable.schedule_data, section_name)
            sections = json.loads(latest_timetable.sections) if latest_timetable.sections else []
        except Exception as e:
            logger.error(f"Error processing classes: {str(e)}", exc_info=True)
    else:
        logger.warning("No active timetable found" if not latest_timetable else "Holiday detected - no classes to show")

    return render_template('section_display.html',
                         current_classes=current_classes,
                         upcoming_classes=upcoming_classes,
                         sections=sections,
                         current_section=section_name,
                         current_holiday=current_holiday)

@app.route('/')
def index():
    notices = Notice.query.filter_by(is_active=True).order_by(db.desc(Notice.upload_date)).all()
    latest_timetable = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).first()
    
    current_classes = []
    upcoming_classes = []
    sections = []
    current_section = None
    
    # Get all sections first
    if latest_timetable:
        sections = json.loads(latest_timetable.sections) if latest_timetable.sections else []
        current_section = sections[0] if sections else None
    
    # Check for current holiday for the current section
    current_holiday = get_current_holiday(current_section)
    
    if latest_timetable and not current_holiday:
        logger.info(f"Found active timetable: {latest_timetable.name}")
        logger.info(f"Raw schedule data: {latest_timetable.schedule_data}")
        
        try:
            # If there are sections, show the first one by default
            if sections:
                current_classes, upcoming_classes = get_section_classes(latest_timetable.schedule_data, sections[0])
            else:
                current_classes, upcoming_classes = get_section_classes(latest_timetable.schedule_data)
                
            # Use the custom encoder for logging
            logger.info(f"Current classes: {json.dumps(current_classes, indent=2, cls=TimeJSONEncoder)}")
            logger.info(f"Upcoming classes: {json.dumps(upcoming_classes, indent=2, cls=TimeJSONEncoder)}")
        except Exception as e:
            logger.error(f"Error processing classes: {str(e)}", exc_info=True)
    else:
        logger.warning("No active timetable found" if not latest_timetable else "Holiday detected - no classes to show")

    now = datetime.now(TIMEZONE)
    logger.info(f"Current time: {now.strftime('%A %I:%M %p')}")

    return render_template('index.html', 
                         notices=notices, 
                         current_classes=current_classes, 
                         upcoming_classes=upcoming_classes,
                         sections=sections,
                         current_section=current_section,
                         now=now,
                         current_holiday=current_holiday)

# Login attempt tracking for rate limiting
login_attempts = {}

def is_rate_limited(ip):
    current_time = datetime.now()
    if ip in login_attempts:
        attempts = login_attempts[ip]
        # Remove attempts older than 15 minutes
        attempts = [time for time in attempts if (current_time - time).seconds < 900]
        login_attempts[ip] = attempts
        return len(attempts) >= 5
    return False

def add_login_attempt(ip):
    current_time = datetime.now()
    if ip in login_attempts:
        login_attempts[ip].append(current_time)
    else:
        login_attempts[ip] = [current_time]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if is_rate_limited(request.remote_addr):
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('login.html'), 429

        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        
        add_login_attempt(request.remote_addr)
        
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

def validate_file_size(file):
    """Validate file size before upload"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= app.config['MAX_CONTENT_LENGTH']

@app.route('/upload_notice', methods=['POST'])
@login_required
def upload_notice():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin'))
    
    if not validate_file_size(file):
        flash('File size exceeds maximum limit (16MB)', 'error')
        return redirect(url_for('admin'))
    
    if file.filename and allowed_file(file.filename, 'notice'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(NOTICES_UPLOAD_PATH, filename)
        file.save(file_path)
        
        notice = Notice()
        notice.title = str(request.form['title'])
        notice.description = str(request.form['description']) if request.form['description'] else None
        notice.filename = str(filename)
        notice.author_id = session.get('admin_id')
        notice.is_active = True
        db.session.add(notice)
        db.session.commit()
        flash('Notice uploaded successfully!', 'success')
    else:
        flash('File type not allowed', 'error')
        return redirect(url_for('admin'))
    
    return redirect(url_for('admin'))

@app.route('/add_notice', methods=['POST'])
@login_required
def add_notice():
    title = request.form['title']
    description = request.form['description']
    category = request.form.get('category')
    expiration_date = request.form.get('expiration_date')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('admin'))
        
    notice = Notice()
    notice.title = title
    notice.description = description if description else None
    notice.category = category if category else None
    notice.author_id = session.get('admin_id', None)
    
    # Handle file upload
    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        if file.filename and allowed_file(file.filename, 'notice'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(NOTICES_UPLOAD_PATH, filename)
            file.save(file_path)
            notice.filename = filename
    
    # Handle photo upload
    if 'photo' in request.files and request.files['photo'].filename:
        photo = request.files['photo']
        if photo.filename and allowed_file(photo.filename, 'notice'):
            photo_filename = secure_filename(photo.filename)
            photo_path = os.path.join(NOTICES_UPLOAD_PATH, photo_filename)
            photo.save(photo_path)
            notice.photo_filename = photo_filename
    
    if expiration_date:
        try:
            # Parse the datetime and make it timezone-aware
            naive_dt = datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M')
            notice.expiration_date = TIMEZONE.localize(naive_dt)
        except ValueError:
            flash('Invalid expiration date format', 'error')
            return redirect(url_for('admin'))
    
    db.session.add(notice)
    db.session.commit()
    
    flash('Notice added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/add_class', methods=['POST'])
@login_required
def add_class():
    subject = request.form['subject']
    room = request.form['room']
    time_str = request.form['time']
    
    try:
        time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
        class_time = time_obj.strftime('%I:%M %p')
        
        # Add to timetable
        timetable = Timetable.query.order_by(db.desc(Timetable.upload_date)).first()
        if timetable:
            schedule = json.loads(timetable.schedule_data)
            schedule.append({
                'day': time_obj.strftime('%A'),
                'time': class_time,
                'subject': subject,
                'room': room
            })
            timetable.schedule_data = json.dumps(schedule)
            db.session.commit()
        
        flash('Class added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding class: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin')
@login_required
def admin():
    notices = Notice.query.order_by(db.desc(Notice.upload_date)).all()
    timetables = Timetable.query.order_by(db.desc(Timetable.upload_date)).all()
    holidays = Holiday.query.order_by(Holiday.start_date).all()
    
    # Get current holiday count
    current_holiday = get_current_holiday()
    current_holiday_count = 1 if current_holiday else 0
    
    # Get available sections dynamically from the latest Excel file
    available_sections = get_dynamic_sections_from_excel()

    return render_template('admin.html', 
                         notices=notices, 
                         timetables=timetables, 
                         holidays=holidays,
                         current_holiday_count=current_holiday_count,
                         available_sections=available_sections)

@app.route('/delete_notice/<int:id>', methods=['POST'])
@login_required
def delete_notice(id):
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_timetable/<int:id>', methods=['POST'])
@login_required
def delete_timetable(id):
    timetable = Timetable.query.get_or_404(id)
    db.session.delete(timetable)
    db.session.commit()
    flash('Timetable deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/download_notice/<filename>')
def download_notice(filename):
    return send_from_directory(NOTICES_UPLOAD_PATH, filename)

@app.route('/preview_pdf/<filename>')
def preview_pdf(filename):
    """
    Preview PDF files in the browser with proper headers for PDF.js compatibility.
    Only allows PDF files from the notices directory for security.
    """
    try:
        # Security: Only allow PDF files
        if not filename.lower().endswith('.pdf'):
            logger.warning(f"Attempted to preview non-PDF file: {filename}")
            return "Invalid file type", 400
        
        # Security: Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"Attempted directory traversal: {filename}")
            return "Invalid filename", 400
        
        file_path = os.path.join(NOTICES_UPLOAD_PATH, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"PDF file not found: {file_path}")
            return "File not found", 404
        
        # Security: Ensure file is actually in the notices directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(NOTICES_UPLOAD_PATH)):
            logger.warning(f"Attempted to access file outside notices directory: {file_path}")
            return "Access denied", 403
        
        # Serve PDF with proper headers for browser viewing
        response = send_from_directory(NOTICES_UPLOAD_PATH, filename)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename="' + filename + '"'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
        
    except Exception as e:
        logger.error(f"Error previewing PDF {filename}: {str(e)}")
        return "Error loading PDF", 500

def validate_timetable_file(file_path):
    """Validate the format and content of the timetable file."""
    try:
        logger.info(f"Starting validation of timetable file: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise ValueError("File not found")
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"File extension: {file_ext}")
        
        # Read the file based on its type
        if file_ext == '.csv':
            logger.info("Reading CSV file")
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            logger.info("Reading Excel file")
            df = pd.read_excel(file_path)
        else:
            logger.error(f"Unsupported file type: {file_ext}")
            raise ValueError("Unsupported file type")
        
        logger.info(f"File read successfully. Shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        # Check if DataFrame is empty
        if df.empty:
            logger.error("DataFrame is empty")
            raise ValueError("The file is empty")
        
        # Define column patterns for flexible matching
        column_patterns = {
            'subject': ['subject', 'course', 'class', 'paper', 'lecture'],
            'time': ['time', 'period', 'slot', 'schedule'],
            'room': ['room', 'venue', 'location', 'hall', 'classroom']
        }
        
        # Check for required columns using flexible matching
        missing_columns = []
        found_columns = {}
        
        # First, normalize all column names to lowercase
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Check each required column type
        for col_type, patterns in column_patterns.items():
            found = False
            for col in df.columns:
                if any(pattern in col for pattern in patterns):
                    found_columns[col_type] = col
                    found = True
                    break
            if not found:
                missing_columns.append(col_type)
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for required time and subject information
        time_pattern = r'\d{1,2}[:\.]\d{2}\s*(?:AM|PM)?'
        subject_pattern = r'[A-Za-z]+\s*\d*'
        
        # Check if there are any valid time entries
        time_col = found_columns['time']
        time_entries = df[time_col].astype(str).str.contains(time_pattern, regex=True)
        if not time_entries.any():
            logger.error("No valid time entries found")
            raise ValueError("No valid time entries found in the Time column")
        
        # Check if there are any valid subject entries
        subject_col = found_columns['subject']
        subject_entries = df[subject_col].astype(str).str.contains(subject_pattern, regex=True)
        if not subject_entries.any():
            logger.error("No valid subject entries found")
            raise ValueError("No valid subject entries found in the Subject column")
        
        logger.info("Timetable validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error validating timetable: {str(e)}", exc_info=True)
        raise ValueError(f"Error validating timetable: {str(e)}")

def validate_schedule_data(schedule_data):
    """Ensure schedule data is valid JSON before storing in database"""
    try:
        if not schedule_data:
            return "[]"
        # Try to parse and re-serialize to ensure valid JSON
        parsed = json.loads(schedule_data)
        return json.dumps(parsed)
    except (json.JSONDecodeError, TypeError):
        return "[]"

@app.route('/upload_timetable', methods=['POST'])
@login_required
def upload_timetable():
    file_path = None
    try:
        logger.info("Starting timetable upload process")
        
        if 'file' not in request.files:
            logger.error("No file part in the request")
            flash('No file selected', 'error')
            return redirect(url_for('admin'))
        
        file = request.files['file']
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.error("Empty filename")
            flash('No file selected', 'error')
            return redirect(url_for('admin'))
        
        if not validate_file_size(file):
            logger.error(f"File size exceeds limit: {file.filename}")
            flash('File size exceeds maximum limit (16MB)', 'error')
            return redirect(url_for('admin'))
        
        if file.filename and allowed_file(file.filename, 'timetable'):
            logger.info(f"File type allowed: {file.filename}")
            # Create a secure filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(TIMETABLES_UPLOAD_PATH, filename)
            logger.info(f"File will be saved to: {file_path}")
            
            # Save the file
            file.save(file_path)
            logger.info(f"File saved to {file_path}")
            
            # Verify the file exists after saving
            if not os.path.exists(file_path):
                logger.error(f"File not found after saving: {file_path}")
                flash('Error saving file. Please try again.', 'error')
                return redirect(url_for('admin'))
            
            # Validate timetable format before processing
            try:
                logger.info("Starting timetable validation")
                if not validate_timetable_file(file_path):
                    logger.error("Timetable validation failed")
                    flash('Invalid timetable format', 'error')
                    return redirect(url_for('admin'))
                logger.info("Timetable format validated successfully")
            except Exception as e:
                logger.error(f"Error validating timetable: {str(e)}", exc_info=True)
                flash(f'Error validating timetable: {str(e)}', 'error')
                return redirect(url_for('admin'))
            
            # Process the timetable
            try:
                logger.info("Starting timetable processing")
                schedule_data, sections = process_timetable(file_path)
                logger.info(f"Processed schedule data: {schedule_data}")
                
                # Validate that the schedule data is valid JSON
                try:
                    json.loads(schedule_data)
                    logger.info("Schedule data is valid JSON")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in schedule data: {str(e)}")
                    flash(f'Error processing timetable: Invalid JSON data', 'error')
                    return redirect(url_for('admin'))
                
            except Exception as e:
                logger.error(f"Error processing timetable: {str(e)}", exc_info=True)
                flash(f'Error processing timetable: {str(e)}', 'error')
                return redirect(url_for('admin'))
            
            # Create and save the timetable record
            timetable = Timetable()
            timetable.name = str(request.form.get('name', 'Timetable'))
            timetable.filename = str(filename)
            timetable.schedule_data = validate_schedule_data(schedule_data)
            timetable.sections = validate_schedule_data(sections)
            timetable.is_active = True
            
            # Deactivate other timetables
            Timetable.query.update({'is_active': False})
            
            db.session.add(timetable)
            db.session.commit()
            logger.info("Timetable saved to database successfully")
            
            flash('Timetable uploaded successfully!', 'success')
            
        else:
            logger.error(f"File type not allowed: {file.filename}")
            flash('File type not allowed. Please upload an Excel or CSV file.', 'error')
        
        return redirect(url_for('admin'))
        
    except Exception as e:
        logger.error(f"Error uploading timetable: {str(e)}", exc_info=True)
        flash(f'Error uploading timetable: {str(e)}', 'error')
        return redirect(url_for('admin'))
        
    finally:
        # Clean up the file if it exists and there was an error
        if file_path and os.path.exists(file_path):
            try:
                # Make sure no pandas resources are holding the file
                gc.collect()
                # Add a small delay to ensure file handles are released
                import time
                time.sleep(0.1)
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {str(e)}")
                # Try again after a longer delay
                try:
                    time.sleep(1)
                    os.remove(file_path)
                    logger.info(f"Successfully cleaned up file on second attempt: {file_path}")
                except Exception as e2:
                    logger.error(f"Failed to clean up file after retry {file_path}: {str(e2)}")

NOTICES_PER_PAGE = 9  # Show 9 notices per page in grid layout

@app.route('/notices')
def notices():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    # Base query
    query = Notice.query.filter_by(is_active=True)
    
    # Apply category filter if specified
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    # Get total count for pagination
    total_notices = query.count()
    total_pages = ceil(total_notices / NOTICES_PER_PAGE)
    
    # Get notices for current page
    notices = query.order_by(db.desc(Notice.upload_date))\
        .offset((page - 1) * NOTICES_PER_PAGE)\
        .limit(NOTICES_PER_PAGE)\
        .all()
    
    # Get all unique categories for the filter dropdown
    categories = db.session.query(Notice.category)\
        .filter(Notice.category.isnot(None))\
        .distinct()\
        .all()
    categories = [cat[0] for cat in categories]
    
    # Get current time for expiration comparison
    now = datetime.now(TIMEZONE)
    
    return render_template('notices.html', 
                         notices=notices, 
                         current_page=page,
                         total_pages=total_pages,
                         categories=categories,
                         selected_category=category,
                         now=now)

@app.route('/timetables')
def timetables():
    try:
        all_timetables = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).all()
        logger.info(f"Found {len(all_timetables)} active timetables")
        
        # Debug log each timetable's data
        for timetable in all_timetables:
            logger.info(f"Timetable ID: {timetable.id}, Name: {timetable.name}")
            logger.info(f"Raw schedule data: {timetable.schedule_data}")
            try:
                parsed_data = json.loads(timetable.schedule_data) if timetable.schedule_data else []
                logger.info(f"Parsed schedule data: {json.dumps(parsed_data, indent=2)}")
                logger.info(f"Number of classes: {len(parsed_data)}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing schedule data for timetable {timetable.id}: {str(e)}")
        
        return render_template('timetables.html', timetables=all_timetables)
    except Exception as e:
        logger.error(f"Error in timetables route: {str(e)}", exc_info=True)
        flash("Error loading timetables", "error")
        return render_template('timetables.html', timetables=[])

def init_db():
    """Initialize database - only creates tables if they don't exist"""
    with app.app_context():
        # Only create tables if they don't exist
        db.create_all()
        
        # Create default admin if it doesn't exist
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            logger.info(f'Created default admin account. Password: {DEFAULT_ADMIN_PASSWORD}')
            logger.warning('Please change the admin password after first login')
        else:
            logger.info('Admin account already exists - no changes made')

def cleanup_expired_notices():
    """Clean up expired notices and their associated files"""
    now = datetime.now(TIMEZONE)
    # Get all active notices with expiration dates
    notices_with_expiration = Notice.query.filter(
        (Notice.expiration_date.isnot(None)) & 
        (Notice.is_active == True)
    ).all()
    
    expired_notices = []
    for notice in notices_with_expiration:
        if notice.is_expired(now):
            expired_notices.append(notice)
    
    for notice in expired_notices:
        notice.is_active = False
        if notice.filename:
            try:
                file_path = os.path.join(NOTICES_UPLOAD_PATH, notice.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file for notice {notice.id}: {str(e)}")
    
    if expired_notices:
        db.session.commit()
        logger.info(f"Cleaned up {len(expired_notices)} expired notices")

def fix_timetable_data():
    """Check and fix any timetables with invalid JSON data"""
    try:
        timetables = Timetable.query.all()
        fixed_count = 0
        
        for timetable in timetables:
            if timetable.schedule_data:
                validated_data = validate_schedule_data(timetable.schedule_data)
                if validated_data != timetable.schedule_data:
                    timetable.schedule_data = validated_data
                    fixed_count += 1
                    logger.info(f"Fixed invalid JSON in timetable {timetable.id}")
        
        if fixed_count > 0:
            db.session.commit()
            logger.info(f"Fixed {fixed_count} timetables with invalid JSON data")
            return True
        return False
    except Exception as e:
        logger.error(f"Error fixing timetable data: {str(e)}", exc_info=True)
        return False

@app.before_request
def before_request():
    cleanup_expired_notices()
    # Check for and fix any timetables with invalid JSON data
    fix_timetable_data()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Roll back db session in case of error
    return render_template('error.html', error_code=500, message="Internal server error"), 500

@app.errorhandler(413)
def file_too_large(error):
    return render_template('error.html', error_code=413, message="File too large (max 16MB)"), 413

@app.route('/static/example_timetable.xlsx')
def download_example_timetable():
    """Generate and serve an example timetable Excel file"""
    try:
        # Create a BytesIO object to store the Excel file
        output = BytesIO()
        
        # Create a Pandas Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Create example data for Section A
            section_a_data = {
                'Day': ['Monday', 'Monday', 'Tuesday', 'Tuesday', 'Wednesday', 'Wednesday'],
                'Start Time': ['9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM'],
                'End Time': ['10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM'],
                'Subject': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History'],
                'Room': ['Room 101', 'Room 102', 'Room 103', 'Room 104', 'Room 105', 'Room 106'],
                'Professor/Faculty Name': ['Dr. Smith', 'Prof. Johnson', 'Dr. Williams', 'Prof. Brown', 'Dr. Davis', 'Prof. Miller']
            }
            df_section_a = pd.DataFrame(section_a_data)
            df_section_a.to_excel(writer, sheet_name='Section A', index=False)
            
            # Create example data for Section B
            section_b_data = {
                'Day': ['Monday', 'Monday', 'Tuesday', 'Tuesday', 'Wednesday', 'Wednesday'],
                'Start Time': ['9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM'],
                'End Time': ['10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM'],
                'Subject': ['Physics', 'Mathematics', 'Biology', 'Chemistry', 'History', 'English'],
                'Room': ['Room 201', 'Room 202', 'Room 203', 'Room 204', 'Room 205', 'Room 206'],
                'Professor/Faculty Name': ['Prof. Wilson', 'Dr. Anderson', 'Prof. Taylor', 'Dr. Thomas', 'Prof. Moore', 'Dr. Jackson']
            }
            df_section_b = pd.DataFrame(section_b_data)
            df_section_b.to_excel(writer, sheet_name='Section B', index=False)
            
            # Create example data for Section C
            section_c_data = {
                'Day': ['Monday', 'Monday', 'Tuesday', 'Tuesday', 'Wednesday', 'Wednesday'],
                'Start Time': ['9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM', '9:00 AM', '11:00 AM'],
                'End Time': ['10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM', '10:00 AM', '12:00 PM'],
                'Subject': ['Chemistry', 'Biology', 'Mathematics', 'Physics', 'English', 'History'],
                'Room': ['Room 301', 'Room 302', 'Room 303', 'Room 304', 'Room 305', 'Room 306'],
                'Professor/Faculty Name': ['Dr. White', 'Prof. Harris', 'Dr. Martin', 'Prof. Thompson', 'Dr. Garcia', 'Prof. Martinez']
            }
            df_section_c = pd.DataFrame(section_c_data)
            df_section_c.to_excel(writer, sheet_name='Section C', index=False)
        
        # Prepare the response
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='example_timetable.xlsx'
        )
    except Exception as e:
        logger.error(f"Error generating example timetable: {str(e)}", exc_info=True)
        flash('Error generating example timetable', 'error')
        return redirect(url_for('admin'))

@app.route('/edit_notice/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_notice(id):
    notice = Notice.query.get_or_404(id)
    
    if request.method == 'POST':
        notice.title = request.form['title']
        notice.description = request.form['description']
        notice.category = request.form.get('category')
        
        # Handle file upload
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if file.filename and allowed_file(file.filename, 'notice'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(NOTICES_UPLOAD_PATH, filename)
                file.save(file_path)
                notice.filename = filename
        
        # Handle photo upload/removal
        if 'remove_photo' in request.form and request.form['remove_photo'] == 'true':
            # Remove the existing photo file if it exists
            if notice.photo_filename:
                try:
                    photo_path = os.path.join(NOTICES_UPLOAD_PATH, notice.photo_filename)
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                except Exception as e:
                    logger.error(f"Error removing photo file: {str(e)}")
            notice.photo_filename = None
        elif 'photo' in request.files and request.files['photo'].filename:
            photo = request.files['photo']
            if photo.filename and allowed_file(photo.filename, 'notice'):
                # Remove the existing photo file if it exists
                if notice.photo_filename:
                    try:
                        old_photo_path = os.path.join(NOTICES_UPLOAD_PATH, notice.photo_filename)
                        if os.path.exists(old_photo_path):
                            os.remove(old_photo_path)
                    except Exception as e:
                        logger.error(f"Error removing old photo file: {str(e)}")
                
                # Save the new photo
                photo_filename = secure_filename(photo.filename)
                photo_path = os.path.join(NOTICES_UPLOAD_PATH, photo_filename)
                photo.save(photo_path)
                notice.photo_filename = photo_filename
        
        # Handle expiration date
        expiration_date = request.form.get('expiration_date')
        if expiration_date:
            try:
                # Parse the datetime and make it timezone-aware
                naive_dt = datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M')
                notice.expiration_date = TIMEZONE.localize(naive_dt)
            except ValueError:
                flash('Invalid expiration date format', 'error')
                return redirect(url_for('edit_notice', id=id))
        
        db.session.commit()
        flash('Notice updated successfully!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('edit_notice.html', notice=notice)

@app.route('/edit_timetable/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_timetable(id):
    timetable = Timetable.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update basic information
            timetable.name = request.form.get('name', timetable.name)
            
            # Handle file upload
            if 'file' in request.files and request.files['file'].filename:
                file = request.files['file']
                if file.filename and allowed_file(file.filename, 'timetable'):
                    # Remove old file if exists
                    if timetable.filename:
                        try:
                            old_file_path = os.path.join(TIMETABLES_UPLOAD_PATH, timetable.filename)
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                        except Exception as e:
                            logger.error(f"Error removing old timetable file: {str(e)}")
                    
                    # Save new file
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(TIMETABLES_UPLOAD_PATH, filename)
                    file.save(file_path)
                    
                    # Process the new timetable
                    schedule_data, sections = process_timetable(file_path)
                    timetable.filename = filename
                    timetable.schedule_data = validate_schedule_data(schedule_data)
                    timetable.sections = validate_schedule_data(sections)
            
            db.session.commit()
            flash('Timetable updated successfully!', 'success')
            return redirect(url_for('admin'))
            
        except Exception as e:
            logger.error(f"Error updating timetable: {str(e)}", exc_info=True)
            flash(f'Error updating timetable: {str(e)}', 'error')
            return redirect(url_for('edit_timetable', id=id))
    
    return render_template('edit_timetable.html', timetable=timetable)

# Holiday Management Routes
@app.route('/add_holiday', methods=['POST'])
@login_required
def add_holiday():
    try:
        holiday_name = request.form['holiday_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        description = request.form.get('description', '')
        affected_sections = request.form.getlist('affected_sections')  # Get list of selected sections
        
        if not holiday_name or not start_date or not end_date:
            flash('Holiday name, start date, and end date are required', 'error')
            return redirect(url_for('admin'))
        
        # Convert string dates to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_dt > end_dt:
            flash('Start date cannot be after end date', 'error')
            return redirect(url_for('admin'))
        
        holiday = Holiday()
        holiday.holiday_name = holiday_name
        holiday.start_date = start_dt
        holiday.end_date = end_dt
        holiday.description = description if description else None
        holiday.is_active = True
        
        # Handle affected sections
        if affected_sections:
            # Check if "ALL_CLASSES" is selected
            if "ALL_CLASSES" in affected_sections:
                holiday.affected_sections = None  # Affects all sections
            else:
                holiday.affected_sections = json.dumps(affected_sections)
        else:
            holiday.affected_sections = None  # Affects all sections
        
        db.session.add(holiday)
        db.session.commit()
        
        flash('Holiday added successfully!', 'success')
    except Exception as e:
        logger.error(f"Error adding holiday: {str(e)}", exc_info=True)
        flash(f'Error adding holiday: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/edit_holiday/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    
    # Get available sections dynamically from the latest Excel file
    available_sections = get_dynamic_sections_from_excel()
    
    if request.method == 'POST':
        try:
            holiday.holiday_name = request.form['holiday_name']
            holiday.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            holiday.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            holiday.description = request.form.get('description', '')
            affected_sections = request.form.getlist('affected_sections')
            
            if holiday.start_date > holiday.end_date:
                flash('Start date cannot be after end date', 'error')
                return redirect(url_for('edit_holiday', id=id))
            
            # Handle affected sections
            if affected_sections:
                # Check if "ALL_CLASSES" is selected
                if "ALL_CLASSES" in affected_sections:
                    holiday.affected_sections = None  # Affects all sections
                else:
                    holiday.affected_sections = json.dumps(affected_sections)
            else:
                holiday.affected_sections = None  # Affects all sections
            
            db.session.commit()
            flash('Holiday updated successfully!', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            logger.error(f"Error updating holiday: {str(e)}", exc_info=True)
            flash(f'Error updating holiday: {str(e)}', 'error')
            return redirect(url_for('edit_holiday', id=id))
    
    return render_template('edit_holiday.html', holiday=holiday, available_sections=available_sections)

@app.route('/delete_holiday/<int:id>', methods=['POST'])
@login_required
def delete_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    db.session.delete(holiday)
    db.session.commit()
    flash('Holiday deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/toggle_holiday/<int:id>', methods=['POST'])
@login_required
def toggle_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    holiday.is_active = not holiday.is_active
    db.session.commit()
    status = 'activated' if holiday.is_active else 'deactivated'
    flash(f'Holiday {status} successfully', 'success')
    return redirect(url_for('admin'))

def get_dynamic_sections_from_excel():
    """Dynamically read sections from the latest Excel timetable file"""
    try:
        # Get the latest active timetable
        latest_timetable = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).first()
        
        if not latest_timetable or not latest_timetable.filename:
            logger.warning("No active timetable found for dynamic section reading")
            return []
        
        # Construct the file path
        file_path = os.path.join(TIMETABLES_UPLOAD_PATH, latest_timetable.filename)
        
        if not os.path.exists(file_path):
            logger.error(f"Timetable file not found: {file_path}")
            return []
        
        # Read sections from the Excel file
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            # For CSV, return a default section
            return ["Default"]
        elif file_ext in ['.xlsx', '.xls']:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            
            if not sheets:
                logger.error("No sheets found in Excel file")
                return []
            
            # Return sheet names as sections
            sections = [sheet.strip() for sheet in sheets if sheet.strip()]
            logger.info(f"Dynamic sections found: {sections}")
            return sections
        else:
            logger.error(f"Unsupported file type for dynamic section reading: {file_ext}")
            return []
            
    except Exception as e:
        logger.error(f"Error reading dynamic sections from Excel: {str(e)}", exc_info=True)
        return []

if __name__ == '__main__':
    # Only initialize database if it doesn't exist
    # This prevents data loss on app restart
    with app.app_context():
        # Check if database exists by trying to query a table
        try:
            # Try to access the database to see if it exists
            Admin.query.first()
            logger.info("Database already exists - skipping initialization")
        except Exception as e:
            # Database doesn't exist or is corrupted, initialize it
            logger.info("Database not found or corrupted - initializing...")
            init_db()
    
    app.run(debug=True)