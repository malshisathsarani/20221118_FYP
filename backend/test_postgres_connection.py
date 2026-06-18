"""
Test PostgreSQL connection
Run this with: python test_postgres_connection.py
"""

try:
    from app.core.database import engine
    from sqlalchemy import text

    print("🔍 Testing PostgreSQL connection...")
    print("=" * 50)

    # Try to connect
    conn = engine.connect()

    # Get PostgreSQL version
    result = conn.execute(text('SELECT version()'))
    version = result.fetchone()[0]

    print("✅ SUCCESS! PostgreSQL is connected!")
    print(f"📊 Database: PostgreSQL")
    print(f"🔢 Version: {version[:80]}")

    # Check if tables exist
    result = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """))

    tables = [row[0] for row in result.fetchall()]

    if tables:
        print(f"\n📋 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
    else:
        print("\n⚠️  No tables found yet")
        print("💡 Tables will be created when you start the app")

    conn.close()

    print("\n" + "=" * 50)
    print("🎉 PostgreSQL migration successful!")
    print("\nNext steps:")
    print("1. Start backend: python -m uvicorn app.main:app --reload")
    print("2. Tables will be auto-created")
    print("3. Optional: Run migrate_to_postgres.py to copy old data")

except ImportError as e:
    print("❌ ERROR: Missing package")
    print(f"   {e}")
    print("\n💡 Solution: Install psycopg2-binary")
    print("   pip install psycopg2-binary")

except Exception as e:
    print("❌ ERROR: Connection failed")
    print(f"   {e}")
    print("\n💡 Check:")
    print("   1. DATABASE_URL in .env is correct")
    print("   2. Supabase project is running")
    print("   3. Password is correct in connection string")
