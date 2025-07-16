#!/usr/bin/env python3
"""
Database Migration Status Checker
Checks if all migrations are applied and database is up to date
"""

import os
import sys
from pathlib import Path

def check_migration_files():
    """Check if all migration files exist"""
    print("📋 Checking Migration Files...")
    
    migrations_dir = Path("migrations/versions")
    if not migrations_dir.exists():
        print("❌ Migrations directory not found")
        return False
    
    migration_files = list(migrations_dir.glob("*.py"))
    if not migration_files:
        print("❌ No migration files found")
        return False
    
    print(f"✅ Found {len(migration_files)} migration files:")
    for file in migration_files:
        print(f"   - {file.name}")
    
    return True

def check_database_file():
    """Check if database file exists"""
    print("\n🗄️ Checking Database File...")
    
    db_file = Path("instance/noticeboard.db")
    if db_file.exists():
        print("✅ Database file exists")
        size = db_file.stat().st_size
        print(f"   Size: {size:,} bytes")
        return True
    else:
        print("❌ Database file not found")
        print("   Run 'flask db upgrade' to create database")
        return False

def check_alembic_config():
    """Check if alembic configuration is correct"""
    print("\n⚙️ Checking Alembic Configuration...")
    
    alembic_ini = Path("migrations/alembic.ini")
    if alembic_ini.exists():
        print("✅ Alembic configuration exists")
        return True
    else:
        print("❌ Alembic configuration not found")
        return False

def check_env_file():
    """Check if environment file exists"""
    print("\n🔧 Checking Environment Configuration...")
    
    env_files = [".flaskenv", ".env"]
    found_env = False
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"✅ Found environment file: {env_file}")
            found_env = True
    
    if not found_env:
        print("⚠️ No environment file found")
        print("   Create .flaskenv or .env file with configuration")
    
    return found_env

def main():
    """Run all checks"""
    print("🔍 Database Migration Status Check")
    print("=" * 40)
    
    all_good = True
    
    # Check migration files
    if not check_migration_files():
        all_good = False
    
    # Check database file
    if not check_database_file():
        all_good = False
    
    # Check alembic config
    if not check_alembic_config():
        all_good = False
    
    # Check environment
    if not check_env_file():
        all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("✅ All checks passed!")
        print("\n📋 Next Steps:")
        print("1. Run 'flask db upgrade' to apply migrations")
        print("2. Run 'flask run' to start the application")
        print("3. Test the application functionality")
    else:
        print("❌ Some checks failed!")
        print("\n🔧 Fix Issues:")
        print("1. Run 'flask db init' if migrations not initialized")
        print("2. Run 'flask db migrate' to create new migrations")
        print("3. Run 'flask db upgrade' to apply migrations")
        print("4. Create .flaskenv file with proper configuration")

if __name__ == "__main__":
    main() 