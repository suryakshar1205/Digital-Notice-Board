#!/usr/bin/env python3
"""
Debug script to test holiday functionality
"""

from app import app, db, Holiday, get_current_holiday, Timetable
from datetime import datetime
import json

def debug_holidays():
    with app.app_context():
        print("=== Holiday Debug Information ===")
        
        # Get all holidays
        holidays = Holiday.query.all()
        print(f"Total holidays in database: {len(holidays)}")
        
        # Get available sections from the latest timetable
        latest_timetable = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).first()
        available_sections = []
        
        if latest_timetable and latest_timetable.sections:
            try:
                available_sections = json.loads(latest_timetable.sections)
                print(f"📋 Available sections from timetable: {available_sections}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"❌ Error parsing sections: {e}")
        else:
            print("❌ No active timetable or sections found")
        
        for holiday in holidays:
            print(f"\nHoliday: {holiday.holiday_name}")
            print(f"  Start Date: {holiday.start_date}")
            print(f"  End Date: {holiday.end_date}")
            print(f"  Is Active: {holiday.is_active}")
            print(f"  Affected Sections: {holiday.affected_sections}")
            
            if holiday.affected_sections:
                try:
                    sections = json.loads(holiday.affected_sections)
                    print(f"  Parsed Sections: {sections}")
                except Exception as e:
                    print(f"  Error parsing sections: {e}")
            
            # Test section matching for all available sections
            if available_sections:
                print(f"  Testing section matching:")
                for section in available_sections:
                    affects = holiday.affects_section(section)
                    print(f"    Affects {section}: {affects}")
            else:
                print(f"  No sections available to test")
        
        print("\n=== Current Holiday Check ===")
        today = datetime.now().date()
        print(f"Today: {today}")
        
        if available_sections:
            for section in available_sections:
                holiday = get_current_holiday(section)
                if holiday:
                    print(f"Current holiday for {section}: {holiday.holiday_name}")
                else:
                    print(f"No current holiday for {section}")
        else:
            print("No sections available to check")

if __name__ == "__main__":
    debug_holidays() 