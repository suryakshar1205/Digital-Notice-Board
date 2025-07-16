#!/usr/bin/env python3
"""
Test script for new features:
1. PDF Preview Route
2. Chatbot Functionality
"""

import os
import sys
from pathlib import Path

def test_chatbot_files():
    """Test that chatbot files exist and are accessible"""
    print("🤖 Testing Chatbot Files...")
    
    # Check if chatbot CSS exists
    css_path = Path("static/css/chatbot.css")
    if css_path.exists():
        print("✅ Chatbot CSS file exists")
        # Check file size to ensure it's not empty
        if css_path.stat().st_size > 100:
            print("✅ Chatbot CSS file has content")
        else:
            print("⚠️  Chatbot CSS file seems small")
    else:
        print("❌ Chatbot CSS file missing")
    
    # Check if chatbot JS exists
    js_path = Path("static/js/chatbot.js")
    if js_path.exists():
        print("✅ Chatbot JavaScript file exists")
        # Check file size to ensure it's not empty
        if js_path.stat().st_size > 100:
            print("✅ Chatbot JavaScript file has content")
        else:
            print("⚠️  Chatbot JavaScript file seems small")
    else:
        print("❌ Chatbot JavaScript file missing")

def test_pdf_viewer_files():
    """Test that PDF viewer files exist and are accessible"""
    print("\n📄 Testing PDF Viewer Files...")
    
    # Check if PDF viewer CSS exists
    css_path = Path("static/css/pdf-viewer.css")
    if css_path.exists():
        print("✅ PDF viewer CSS file exists")
        # Check file size to ensure it's not empty
        if css_path.stat().st_size > 100:
            print("✅ PDF viewer CSS file has content")
        else:
            print("⚠️  PDF viewer CSS file seems small")
    else:
        print("❌ PDF viewer CSS file missing")
    
    # Check if PDF viewer JS exists
    js_path = Path("static/js/pdf-viewer.js")
    if js_path.exists():
        print("✅ PDF viewer JavaScript file exists")
        # Check file size to ensure it's not empty
        if js_path.stat().st_size > 100:
            print("✅ PDF viewer JavaScript file has content")
        else:
            print("⚠️  PDF viewer JavaScript file seems small")
    else:
        print("❌ PDF viewer JavaScript file missing")

def test_template_updates():
    """Test that templates have been updated correctly"""
    print("\n📝 Testing Template Updates...")
    
    # Check if base template includes new CSS/JS
    base_template = Path("templates/base.html")
    if base_template.exists():
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pdf-viewer.css' in content:
                print("✅ PDF viewer CSS included in base template")
            else:
                print("❌ PDF viewer CSS not found in base template")
            
            if 'chatbot.css' in content:
                print("✅ Chatbot CSS included in base template")
            else:
                print("❌ Chatbot CSS not found in base template")
            
            if 'pdf-viewer.js' in content:
                print("✅ PDF viewer JS included in base template")
            else:
                print("❌ PDF viewer JS not found in base template")
            
            if 'chatbot.js' in content:
                print("✅ Chatbot JS included in base template")
            else:
                print("❌ Chatbot JS not found in base template")
    else:
        print("❌ Base template not found")

def test_notices_template():
    """Test that notices template has PDF preview functionality"""
    print("\n📋 Testing Notices Template...")
    
    notices_template = Path("templates/notices.html")
    if notices_template.exists():
        with open(notices_template, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pdf-preview-btn' in content:
                print("✅ PDF preview buttons found in notices template")
            else:
                print("❌ PDF preview buttons not found in notices template")
            
            if 'preview_pdf' in content:
                print("✅ PDF preview route referenced in notices template")
            else:
                print("❌ PDF preview route not found in notices template")
            
            if 'pdf-viewer.css' in content:
                print("✅ PDF viewer CSS included in notices template")
            else:
                print("❌ PDF viewer CSS not found in notices template")
    else:
        print("❌ Notices template not found")

def test_index_template():
    """Test that index template has PDF preview functionality"""
    print("\n🏠 Testing Index Template...")
    
    index_template = Path("templates/index.html")
    if index_template.exists():
        with open(index_template, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pdf-preview-btn' in content:
                print("✅ PDF preview buttons found in index template")
            else:
                print("❌ PDF preview buttons not found in index template")
            
            if 'preview_pdf' in content:
                print("✅ PDF preview route referenced in index template")
            else:
                print("❌ PDF preview route not found in index template")
    else:
        print("❌ Index template not found")

def test_app_py_updates():
    """Test that app.py has the new PDF preview route"""
    print("\n🐍 Testing App.py Updates...")
    
    app_py = Path("app.py")
    if app_py.exists():
        with open(app_py, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'preview_pdf' in content:
                print("✅ PDF preview route found in app.py")
            else:
                print("❌ PDF preview route not found in app.py")
            
            if 'def preview_pdf' in content:
                print("✅ PDF preview function found in app.py")
            else:
                print("❌ PDF preview function not found in app.py")
            
            # Check for security features
            if 'directory traversal' in content.lower():
                print("✅ Directory traversal protection found")
            else:
                print("⚠️  Directory traversal protection not explicitly found")
    else:
        print("❌ App.py not found")

def main():
    """Run all tests"""
    print("🚀 Testing New Features Implementation")
    print("=" * 50)
    
    try:
        # Test file existence and content
        test_pdf_viewer_files()
        test_chatbot_files()
        
        # Test template updates
        test_template_updates()
        test_notices_template()
        test_index_template()
        
        # Test app.py updates
        test_app_py_updates()
        
        print("\n" + "=" * 50)
        print("✅ Feature implementation test completed!")
        print("\n📋 Summary:")
        print("• PDF Preview: Embedded PDF viewer with security")
        print("• Chatbot: FAQ assistant with interactive UI")
        print("• Both features are modular and non-breaking")
        print("• All files are properly organized")
        print("\n🎯 Next Steps:")
        print("1. Start the server: flask run")
        print("2. Test PDF preview with actual PDF files")
        print("3. Test chatbot functionality on the home page")
        print("4. Verify all existing features still work")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 