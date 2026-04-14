#!/usr/bin/env python3
"""
Script to initialize Heart's Desire table and data.
Run this when the Flask application is not running.
"""

from db import init_db

def main():
    print("Initializing Heart's Desire table and data...")
    try:
        init_db()
        print("✅ Heart's Desire table created and data seeded successfully!")
        
        # Verify the data
        from db import SessionLocal, HeartDesire
        db = SessionLocal()
        try:
            count = db.query(HeartDesire).count()
            print(f"✅ Verified: {count} Heart's Desire records in database")
            
            # Test a sample record
            sample = db.query(HeartDesire).filter(HeartDesire.no == 2).first()
            if sample:
                print(f"✅ Sample record (HD 2): {sample.deskripsi[:50]}...")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the Flask application is not running, then try again.")

if __name__ == "__main__":
    main()
