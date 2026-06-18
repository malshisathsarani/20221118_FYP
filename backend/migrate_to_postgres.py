"""
Script to migrate data from SQLite to PostgreSQL
Run this AFTER setting up PostgreSQL and updating .env
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys

# Old SQLite database
SQLITE_URL = "sqlite:///./mental_health.db"

# New PostgreSQL database (from .env)
from app.core.config import settings
POSTGRES_URL = settings.DATABASE_URL

def migrate_data():
    print("🔄 Starting migration from SQLite to PostgreSQL...")

    # Connect to both databases
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # Create tables in PostgreSQL
    print("📋 Creating tables in PostgreSQL...")
    from app.core.database import Base
    from app.models import user, chat, crisis, feedback, emergency_contact, artwork, game_session

    Base.metadata.create_all(bind=postgres_engine)
    print("✅ Tables created!")

    # Get table names
    sqlite_session = sessionmaker(bind=sqlite_engine)()
    postgres_session = sessionmaker(bind=postgres_engine)()

    try:
        # Get all table names
        tables = Base.metadata.tables.keys()

        for table_name in tables:
            print(f"\n📦 Migrating table: {table_name}")

            # Read from SQLite
            result = sqlite_session.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()

            if not rows:
                print(f"   ⚠️  No data in {table_name}")
                continue

            # Insert into PostgreSQL
            for row in rows:
                row_dict = dict(zip(columns, row))
                placeholders = ", ".join([f":{col}" for col in columns])
                cols = ", ".join(columns)

                insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                postgres_session.execute(text(insert_sql), row_dict)

            postgres_session.commit()
            print(f"   ✅ Migrated {len(rows)} rows")

        print("\n🎉 Migration completed successfully!")
        print("📝 Next steps:")
        print("   1. Test your application with PostgreSQL")
        print("   2. Backup mental_health.db (keep it safe!)")
        print("   3. Update DATABASE_URL in .env permanently")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        postgres_session.rollback()
        sys.exit(1)
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    confirm = input("⚠️  This will copy all data to PostgreSQL. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_data()
    else:
        print("❌ Migration cancelled")
