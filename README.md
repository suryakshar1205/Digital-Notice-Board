# Notice Board and Timetable Management System

A comprehensive Flask-based web application for educational institutions to manage academic notices, timetables, holidays, and student interactions through an intelligent chatbot interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [Development Guide](#development-guide)
- [Feature Documentation](#feature-documentation)
- [File Structure & Source Code Map](#file-structure--source-code-map)
- [API Reference](#api-reference)
- [Security Considerations](#security-considerations)
- [Deployment Guide](#deployment-guide)
- [Testing & Debugging](#testing--debugging)
- [Future Improvements](#future-improvements)
- [Changelog](#changelog)

## Overview

This system provides a complete digital notice board and timetable management solution with the following core capabilities:

- **Notice Management**: Upload, categorize, and display notices with file attachments
- **Timetable Management**: Multi-section timetable uploads with real-time class tracking
- **Holiday Management**: Section-specific holiday scheduling and display
- **Interactive Chatbot**: AI-powered assistant for student queries
- **PDF Viewer**: Embedded document preview functionality
- **Admin Dashboard**: Comprehensive management interface
- **Dynamic Section Support**: Automatically handles any number of sections

### Key Technologies

- **Backend**: Flask 2.2.5, SQLAlchemy 3.0.2, Flask-Migrate 4.0.4
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
- **Database**: SQLite (dev), PostgreSQL/MySQL (prod)
- **File Processing**: Pandas 2.0.3, OpenPyXL 3.1.2
- **Security**: Flask-WTF, bcrypt, rate limiting

## Features

### 1. Notice Management
**Purpose**: Centralized announcement system with file attachments and categorization

**Pages & Routes**:
- `/notices` - Public notice listing
- `/admin` - Notice management interface
- `/upload_notice` - File upload endpoint
- `/add_notice` - Notice creation endpoint
- `/edit_notice/<id>` - Notice editing
- `/delete_notice/<id>` - Notice deletion
- `/download_notice/<filename>` - File download
- `/preview_pdf/<filename>` - PDF preview

**User Flow**:
1. User visits `/notices` page
2. Views paginated notices with search/filter options
3. Clicks notice to view details
4. Downloads attachments or previews PDFs
5. Receives real-time updates

**Admin Flow**:
1. Login to admin dashboard
2. Navigate to Notice Management section
3. Create notice with title, description, category
4. Upload file attachment (PDF, DOC, DOCX, TXT)
5. Set expiration date (optional)
6. Preview and publish notice
7. Manage existing notices (edit/delete)

### 2. Timetable Management
**Purpose**: Multi-section class schedule management with real-time status tracking

**Pages & Routes**:
- `/timetables` - Public timetable view
- `/section/<section_name>` - Section-specific view
- `/admin` - Timetable management interface
- `/upload_timetable` - Timetable upload endpoint
- `/edit_timetable/<id>` - Timetable editing
- `/delete_timetable/<id>` - Timetable deletion

**User Flow**:
1. User visits `/timetables` or `/section/<section>`
2. Views current and upcoming classes
3. Switches between sections using dropdown
4. Sees real-time class status (current/upcoming)
5. Views holiday messages when applicable

**Admin Flow**:
1. Access admin dashboard
2. Navigate to Timetable Management
3. Upload Excel/CSV file with schedule data
4. System validates format and extracts sections
5. Preview processed data
6. Activate timetable for public viewing
7. Manage multiple timetables

### 3. Holiday Management
**Purpose**: Section-specific holiday scheduling with automatic display logic

**Pages & Routes**:
- `/admin` - Holiday management interface
- `/add_holiday` - Holiday creation endpoint
- `/edit_holiday/<id>` - Holiday editing
- `/delete_holiday/<id>` - Holiday deletion
- `/toggle_holiday/<id>` - Holiday activation/deactivation

**User Flow**:
1. User visits timetable page during holiday
2. Sees holiday message instead of class schedule
3. Chatbot responds to holiday-related queries
4. Holiday status is section-specific

**Admin Flow**:
1. Access admin dashboard
2. Navigate to Holiday Management section
3. Create holiday with name, dates, description
4. Select affected sections (or all sections)
5. Set active/inactive status
6. Edit or delete existing holidays

### 4. Interactive Chatbot
**Purpose**: AI-powered assistant for student queries and information retrieval

**Pages & Routes**:
- Embedded in all pages via JavaScript
- `/` - Main chatbot interface
- AJAX endpoints for response handling

**User Flow**:
1. User clicks floating chatbot icon
2. Chat interface opens in modal
3. User types query (timetable, notices, holidays)
4. System provides contextual responses
5. Chat history maintained during session

**Admin Flow**:
1. No direct admin interface
2. Responses are hardcoded in JavaScript
3. Can be extended with AI integration

### 5. PDF Viewer
**Purpose**: Embedded document preview for notice attachments

**Pages & Routes**:
- `/preview_pdf/<filename>` - PDF preview endpoint
- Modal integration in notice pages

**User Flow**:
1. User clicks PDF attachment in notice
2. PDF opens in embedded viewer modal
3. User can scroll, zoom, and navigate
4. Download option available

**Admin Flow**:
1. Upload PDF files with notices
2. System validates file type and security
3. Files stored securely with access control

### 6. Admin Dashboard
**Purpose**: Centralized management interface for all system features

**Pages & Routes**:
- `/login` - Admin authentication
- `/admin` - Main dashboard
- `/logout` - Session termination

**User Flow**:
1. Admin visits `/login`
2. Enters credentials (rate-limited)
3. Accesses dashboard with all management tools
4. Manages notices, timetables, holidays
5. Views system statistics

**Admin Flow**:
1. Login with secure credentials
2. Navigate between management sections
3. Perform CRUD operations on all entities
4. Monitor system activity
5. Manage file uploads and downloads

### 7. Authentication & Security
**Purpose**: Secure admin access with comprehensive protection

**Pages & Routes**:
- `/login` - Authentication endpoint
- Session management across all admin routes
- Rate limiting and IP blocking

**Security Features**:
- Password hashing with bcrypt
- Session timeout (30 minutes)
- Rate limiting (5 attempts per 15 minutes)
- CSRF protection
- File upload validation
- XSS prevention

## System Architecture

### Component Diagram
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Web Interface  │◄───►│  Flask Server   │◄───►│  Database       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  File Storage   │◄───►│  File Processor │◄───►│  Data Validator │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Database Schema
```sql
-- Core Tables
Admin (id, username, password_hash)
Notice (id, title, description, filename, upload_date, expiration_date, is_active, category, author_id)
Timetable (id, name, filename, upload_date, is_active, schedule_data, sections)
Holiday (id, holiday_name, start_date, end_date, description, created_date, is_active, affected_sections)
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- SQLite (development) or PostgreSQL/MySQL (production)
- 2GB RAM minimum
- 500MB disk space

### 1. Clone Repository
```bash
git clone <repository-url>
cd notice-board-system
```

### 2. Virtual Environment Setup
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Production dependencies
pip install gunicorn psycopg2-binary
```

### 4. Environment Configuration
Create `.flaskenv`:
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=your-secure-random-key-here
ADMIN_PASSWORD=your-secure-admin-password
DATABASE_URL=sqlite:///instance/noticeboard.db
MAX_CONTENT_LENGTH=16777216
```

### 5. Database Initialization
```bash
# Initialize database and create admin user
python init_db.py

# Run migrations (if using Flask-Migrate)
flask db upgrade
```

### 6. Development Server
```bash
flask run
```

Access: http://localhost:5000

## Development Guide

### Project Structure
```
notice-board-system/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── .flaskenv            # Environment variables
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── uploads/        # File storage
├── templates/           # HTML templates
├── migrations/          # Database migrations
└── instance/           # Instance-specific files
```

### Development Workflow
1. **Feature Development**:
   - Create feature branch
   - Implement changes
   - Update tests
   - Create migration if needed
   - Test thoroughly

2. **Database Changes**:
   ```bash
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

3. **Testing**:
   ```bash
   python test_sections.py
   python debug_holidays.py
   ```

## Feature Documentation

### Main Landing Page (`/`)
**Purpose**: Central hub displaying current notices and timetable information

**Database Interactions**:
- Queries `Notice` table for active notices
- Queries `Timetable` table for latest schedule
- Queries `Holiday` table for current holiday status

**Endpoints Called**:
- `/` - Main page rendering
- `/section/<section>` - Section switching
- AJAX calls for real-time updates

**Security**: Public access, no authentication required

### Notices List Page (`/notices`)
**Purpose**: Comprehensive notice browsing with search and filtering

**Database Interactions**:
- Queries `Notice` table with pagination
- Filters by category and date
- Handles file downloads

**Endpoints Called**:
- `/notices` - Notice listing
- `/download_notice/<filename>` - File download
- `/preview_pdf/<filename>` - PDF preview

**Security**: Public access, file validation on downloads

### Timetables Page (`/timetables`)
**Purpose**: Multi-section timetable display with real-time status

**Database Interactions**:
- Queries `Timetable` table for active schedule
- Queries `Holiday` table for section-specific holidays
- Processes schedule data for current/upcoming classes

**Endpoints Called**:
- `/timetables` - Main timetable view
- `/section/<section>` - Section-specific view
- AJAX for section switching

**Security**: Public access, section validation

### Admin Login (`/login`)
**Purpose**: Secure authentication for administrative access

**Database Interactions**:
- Queries `Admin` table for user validation
- Tracks login attempts for rate limiting

**Endpoints Called**:
- `/login` - Authentication endpoint
- Session management

**Security**: Rate limiting, password hashing, session management

### Admin Dashboard (`/admin`)
**Purpose**: Centralized management interface

**Database Interactions**:
- Queries all tables for management operations
- Handles CRUD operations for all entities
- Manages file uploads and system settings

**Endpoints Called**:
- `/admin` - Dashboard rendering
- Various CRUD endpoints for each entity
- File upload/download endpoints

**Security**: Authentication required, CSRF protection, file validation

### Holiday Management Page (Admin Dashboard)
**Purpose**: Section-specific holiday scheduling

**Database Interactions**:
- Queries `Holiday` table for all holidays
- Manages holiday creation, editing, deletion
- Handles section-specific holiday logic

**Endpoints Called**:
- `/add_holiday` - Holiday creation
- `/edit_holiday/<id>` - Holiday editing
- `/delete_holiday/<id>` - Holiday deletion
- `/toggle_holiday/<id>` - Status toggle

**Security**: Admin authentication required, input validation

### Chatbot Interface (Embedded)
**Purpose**: Interactive student assistance

**Database Interactions**:
- Queries timetable and holiday data for responses
- No persistent storage for chat history

**Endpoints Called**:
- JavaScript-based responses
- AJAX calls for dynamic content

**Security**: Public access, input sanitization

### PDF Preview Page (`/preview_pdf/<filename>`)
**Purpose**: Secure PDF document viewing

**Database Interactions**:
- Validates file existence and permissions
- No direct database queries

**Endpoints Called**:
- `/preview_pdf/<filename>` - PDF serving

**Security**: File type validation, path traversal prevention, access control

## File Structure & Source Code Map

### Backend Files
| File | Purpose | Key Functions |
|------|---------|---------------|
| `app.py` | Main Flask application | All routes, models, business logic |
| `init_db.py` | Database initialization | Admin user creation, table setup |
| `requirements.txt` | Dependencies | Python package specifications |

### Frontend Files
| File | Purpose | Key Functions |
|------|---------|---------------|
| `templates/index.html` | Main landing page | Notice display, timetable view |
| `templates/notices.html` | Notice listing | Search, filter, pagination |
| `templates/timetables.html` | Timetable display | Section switching, class status |
| `templates/admin.html` | Admin dashboard | All management interfaces |
| `templates/login.html` | Authentication | Login form, error handling |
| `templates/section_display.html` | Section view | Section-specific timetable |
| `static/css/main.css` | Main styles | Responsive design, themes |
| `static/css/admin.css` | Admin styles | Dashboard layout, forms |
| `static/js/main.js` | Main JavaScript | Chatbot, real-time updates |
| `static/js/admin.js` | Admin JavaScript | Form handling, AJAX calls |

### Database Files
| File | Purpose | Key Functions |
|------|---------|---------------|
| `migrations/` | Database migrations | Schema changes, data migrations |
| `instance/noticeboard.db` | SQLite database | Development data storage |

### Test Files
| File | Purpose | Key Functions |
|------|---------|---------------|
| `test_sections.py` | Section testing | Dynamic section validation |
| `debug_holidays.py` | Holiday debugging | Holiday logic verification |

## API Reference

### Notice Endpoints
```http
GET /notices - List all notices
POST /upload_notice - Upload notice with file
POST /add_notice - Create notice
GET /edit_notice/<id> - Edit notice form
POST /edit_notice/<id> - Update notice
POST /delete_notice/<id> - Delete notice
GET /download_notice/<filename> - Download file
GET /preview_pdf/<filename> - Preview PDF
```

### Timetable Endpoints
```http
GET /timetables - Display timetables
GET /section/<section> - Section-specific view
POST /upload_timetable - Upload timetable
POST /edit_timetable/<id> - Edit timetable
POST /delete_timetable/<id> - Delete timetable
```

### Holiday Endpoints
```http
POST /add_holiday - Create holiday
GET /edit_holiday/<id> - Edit holiday form
POST /edit_holiday/<id> - Update holiday
POST /delete_holiday/<id> - Delete holiday
POST /toggle_holiday/<id> - Toggle status
```

### Admin Endpoints
```http
GET /login - Login form
POST /login - Authenticate
GET /admin - Dashboard
GET /logout - Logout
```

## Security Considerations

### Authentication & Authorization
- **Password Security**: bcrypt hashing with salt
- **Session Management**: 30-minute timeout, secure cookies
- **Rate Limiting**: 5 login attempts per 15 minutes
- **CSRF Protection**: Flask-WTF integration

### File Security
- **Upload Validation**: MIME type checking, size limits (16MB)
- **Path Traversal Prevention**: Secure filename handling
- **Access Control**: File permissions and validation
- **Virus Scanning**: Integration ready for production

### Data Protection
- **Input Validation**: Comprehensive sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Prevention**: Template escaping, CSP headers
- **HTTPS Enforcement**: Production requirement

### Monitoring & Logging
- **Activity Logging**: User actions and system events
- **Error Tracking**: Comprehensive error handling
- **Security Auditing**: Login attempts and file access
- **Performance Monitoring**: Response times and resource usage

## Deployment Guide

### Production Environment Setup

#### 1. Server Requirements
- Ubuntu 20.04+ / CentOS 8+
- Python 3.8+
- PostgreSQL 12+ / MySQL 8.0+
- Nginx
- SSL certificate

#### 2. Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE noticeboard;
CREATE USER noticeboard_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE noticeboard TO noticeboard_user;
\q
```

#### 3. Application Setup
```bash
# Clone and setup
git clone <repository-url>
cd notice-board-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Environment configuration
cat > .flaskenv << EOF
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=your-production-secret-key
ADMIN_PASSWORD=your-secure-admin-password
DATABASE_URL=postgresql://noticeboard_user:secure_password@localhost/noticeboard
SESSION_COOKIE_SECURE=True
EOF

# Initialize database
python init_db.py
```

#### 4. Gunicorn Configuration
Create `/etc/systemd/system/noticeboard.service`:
```ini
[Unit]
Description=Notice Board Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/notice-board-system
Environment="PATH=/path/to/notice-board-system/venv/bin"
ExecStart=/path/to/notice-board-system/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. Nginx Configuration
Create `/etc/nginx/sites-available/noticeboard`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/notice-board-system/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /path/to/notice-board-system/static/uploads;
        internal;
    }
}
```

#### 6. Start Services
```bash
# Enable and start services
sudo systemctl enable noticeboard
sudo systemctl start noticeboard
sudo ln -s /etc/nginx/sites-available/noticeboard /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Backup Strategy

#### Database Backup
```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump noticeboard > $BACKUP_DIR/noticeboard_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

#### File Backup
```bash
# File backup script
#!/bin/bash
BACKUP_DIR="/backups/files"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /path/to/notice-board-system/static/uploads/
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Monitoring Setup
```bash
# Log rotation
sudo nano /etc/logrotate.d/noticeboard

/path/to/notice-board-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 www-data www-data
}
```

## Testing & Debugging

### Automated Testing
```bash
# Run section tests
python test_sections.py

# Debug holiday functionality
python debug_holidays.py

# Expected output examples:
# ✅ Holiday message found for 3-IDP
# ✅ Class content found for 3-REG
# 🎯 Summary: Tested 2 sections dynamically
```

### Manual Testing Checklist
- [ ] Notice creation and display
- [ ] File upload and download
- [ ] PDF preview functionality
- [ ] Timetable upload and section switching
- [ ] Holiday creation and display
- [ ] Chatbot responses
- [ ] Admin authentication and dashboard
- [ ] Section-specific holiday logic
- [ ] File validation and security

### Debug Tools
- **Flask Debug Mode**: Detailed error pages
- **Database Inspection**: SQLite browser or psql
- **Log Analysis**: Application and server logs
- **Network Monitoring**: Browser developer tools

## Future Improvements

### Security Enhancements
- [ ] **Two-Factor Authentication**: TOTP integration for admin accounts
- [ ] **API Rate Limiting**: Comprehensive rate limiting for all endpoints
- [ ] **Content Security Policy**: Strict CSP headers implementation
- [ ] **File Virus Scanning**: Integration with ClamAV or similar
- [ ] **Audit Logging**: Comprehensive audit trail for all actions
- [ ] **Input Sanitization**: Enhanced input validation and sanitization

### Performance Optimization
- [ ] **Caching Layer**: Redis integration for session and data caching
- [ ] **Database Optimization**: Query optimization and indexing
- [ ] **CDN Integration**: Static file delivery via CDN
- [ ] **Image Optimization**: Automatic image compression and resizing
- [ ] **Lazy Loading**: Implement lazy loading for large datasets
- [ ] **Background Tasks**: Celery integration for file processing

### UI/UX Improvements
- [ ] **Progressive Web App**: PWA features for mobile experience
- [ ] **Dark Mode**: Toggle between light and dark themes
- [ ] **Accessibility**: WCAG 2.1 AA compliance
- [ ] **Mobile Optimization**: Enhanced mobile interface
- [ ] **Real-time Updates**: WebSocket integration for live updates
- [ ] **Advanced Search**: Full-text search with filters

### Feature Extensions
- [ ] **Push Notifications**: Browser and mobile push notifications
- [ ] **Calendar Integration**: Google Calendar/Outlook integration
- [ ] **Email Notifications**: Automated email alerts for notices
- [ ] **Multi-language Support**: Internationalization (i18n)
- [ ] **Advanced Analytics**: User behavior and system usage analytics
- [ ] **API Development**: RESTful API for third-party integrations
- [ ] **Bulk Operations**: Batch upload and management features
- [ ] **Advanced Reporting**: Custom report generation
- [ ] **User Roles**: Multiple admin roles with different permissions
- [ ] **Backup Automation**: Automated backup scheduling and monitoring

### Technical Debt
- [ ] **Code Refactoring**: Modular architecture with blueprints
- [ ] **Testing Coverage**: Comprehensive unit and integration tests
- [ ] **Documentation**: API documentation with Swagger/OpenAPI
- [ ] **Configuration Management**: Environment-specific configurations
- [ ] **Error Handling**: Centralized error handling and logging
- [ ] **Database Migrations**: Automated migration testing and rollback

## Changelog

### Version 2.0.0 (Current)
**Major Features Added**:
- ✅ Holiday Management System
- ✅ Dynamic Section Support
- ✅ Interactive Chatbot
- ✅ PDF Viewer Integration
- ✅ Enhanced Admin Dashboard
- ✅ Comprehensive Testing Scripts

**Technical Improvements**:
- ✅ Flask-Migrate integration
- ✅ Enhanced security features
- ✅ Improved file handling
- ✅ Better error handling
- ✅ Comprehensive logging

### Version 1.5.0
**Features Added**:
- ✅ Multi-section timetable support
- ✅ File attachment system
- ✅ Admin authentication
- ✅ Basic notice management

### Version 1.0.0
**Initial Release**:
- ✅ Basic notice board functionality
- ✅ Simple timetable display
- ✅ Admin interface
- ✅ File upload capabilities

---

## Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Database backups, log rotation
- **Weekly**: Security updates, performance monitoring
- **Monthly**: System health checks, backup verification
- **Quarterly**: Security audits, performance optimization

### Contact Information
- **Email**: support@example.com
- **Issue Tracker**: GitHub Issues
- **Documentation**: Project Wiki
- **Security**: security@example.com

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*This README provides a comprehensive guide for developers to understand, deploy, and maintain the Notice Board and Timetable Management System. For additional support or questions, please refer to the contact information above.* 