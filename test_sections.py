#!/usr/bin/env python3
"""
Test script to verify section view routes using Flask test client
"""

from app import app, db, Timetable
import json

def test_section_routes():
    with app.app_context():
        with app.test_client() as client:
            # Get available sections from the database
            latest_timetable = Timetable.query.filter_by(is_active=True).order_by(db.desc(Timetable.upload_date)).first()
            
            if not latest_timetable or not latest_timetable.sections:
                print("❌ No active timetable or sections found in database")
                return
            
            try:
                available_sections = json.loads(latest_timetable.sections)
                print(f"📋 Found {len(available_sections)} sections in timetable: {available_sections}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"❌ Error parsing sections: {e}")
                return
            
            # Test each available section
            for section in available_sections:
                print(f"\n=== Testing Section: {section} ===")
                try:
                    response = client.get(f"/section/{section}")
                    print(f"Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_text = response.get_data(as_text=True)
                        
                        # Check if holiday message is present
                        if "holiday-message" in response_text:
                            print(f"✅ Holiday message found for {section}")
                        else:
                            print(f"❌ No holiday message found for {section}")
                        
                        # Check if class content is present
                        if "class-card" in response_text:
                            print(f"✅ Class content found for {section}")
                        else:
                            print(f"❌ No class content found for {section}")
                        
                        # Check if section name is displayed
                        if section in response_text:
                            print(f"✅ Section name '{section}' found in response")
                        else:
                            print(f"❌ Section name '{section}' not found in response")
                            
                    else:
                        print(f"❌ Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print(f"\n🎯 Summary: Tested {len(available_sections)} sections dynamically")

if __name__ == "__main__":
    test_section_routes() 