"""
Create emergency_contacts table in the database
Run this before testing the emergency contacts feature
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import engine, Base
from app.models.emergency_contact import EmergencyContact

def create_table():
    print("Creating emergency_contacts table...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Table created successfully!")

        # Verify by checking tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'emergency_contacts' in tables:
            print("✅ emergency_contacts table exists in database")

            # Show columns
            columns = inspector.get_columns('emergency_contacts')
            print("\nTable columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("❌ emergency_contacts table NOT found")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_table()
