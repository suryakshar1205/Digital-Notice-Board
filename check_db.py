from app import app, db, Notice

with app.app_context():
    # Query all notices (don't create tables - just check existing data)
    notices = Notice.query.all()
    
    print(f"Total notices: {len(notices)}")
    for notice in notices:
        print(f"\nNotice ID: {notice.id}")
        print(f"Title: {notice.title}")
        print(f"Description: {notice.description}")
        print(f"Upload Date: {notice.upload_date}")
        print(f"Expiration Date: {notice.expiration_date}")
        print(f"Active: {notice.is_active}")
        print(f"Category: {notice.category}") 