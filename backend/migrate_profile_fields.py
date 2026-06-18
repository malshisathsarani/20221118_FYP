"""
Database migration script to add profile fields to the users table.
This adds the new columns we created for the profile feature.
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'mental_health.db')

def migrate_database():
    """Add new profile fields to users table"""

    print("=" * 60)
    print("DATABASE MIGRATION: Adding Profile Fields")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check current table structure
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nExisting columns: {existing_columns}")

        # Define new columns to add
        new_columns = {
            'avatar_url': 'TEXT',
            'phone_number': 'TEXT',
            'bio': 'TEXT',
            'notifications_enabled': 'BOOLEAN DEFAULT 1',
            'email_notifications': 'BOOLEAN DEFAULT 1',
            'data_sharing_consent': 'BOOLEAN DEFAULT 0',
            'analytics_consent': 'BOOLEAN DEFAULT 0'
        }

        # Add each column if it doesn't exist
        added_columns = []
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                print(f"\nAdding column: {column_name} ({column_type})")
                cursor.execute(sql)
                added_columns.append(column_name)
            else:
                print(f"\nColumn already exists: {column_name} ✓")

        # Commit changes
        conn.commit()

        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [row[1] for row in cursor.fetchall()]

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"\nColumns added: {len(added_columns)}")
        if added_columns:
            for col in added_columns:
                print(f"  ✓ {col}")

        print(f"\nTotal columns in users table: {len(updated_columns)}")

        # Show current user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Existing users in database: {user_count}")

        if user_count > 0:
            print("\n⚠️  Note: Existing users will have default values for new fields:")
            print("  - avatar_url: NULL")
            print("  - phone_number: NULL")
            print("  - bio: NULL")
            print("  - notifications_enabled: TRUE")
            print("  - email_notifications: TRUE")
            print("  - data_sharing_consent: FALSE")
            print("  - analytics_consent: FALSE")

        print("\n" + "=" * 60)
        print("✅ Database is now ready for the profile feature!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
