"""
Database migration script to add game tracking tables.
Run this after updating the models.
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'mental_health.db')

def migrate_database():
    """Add game tracking tables"""

    print("=" * 60)
    print("DATABASE MIGRATION: Adding Game Tracking Tables")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_sessions'")
        if cursor.fetchone():
            print("\n✓ game_sessions table already exists")
        else:
            print("\n Creating game_sessions table...")
            cursor.execute("""
                CREATE TABLE game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    game_name TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    pre_mood INTEGER,
                    post_mood INTEGER,
                    mood_improvement REAL,
                    effectiveness_rating INTEGER,
                    notes TEXT,
                    device TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("✓ game_sessions table created")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_achievements'")
        if cursor.fetchone():
            print("✓ user_achievements table already exists")
        else:
            print("\nCreating user_achievements table...")
            cursor.execute("""
                CREATE TABLE user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    achievement_description TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    progress INTEGER DEFAULT 0,
                    target INTEGER,
                    icon TEXT,
                    category TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("✓ user_achievements table created")

        # Commit changes
        conn.commit()

        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nGame tracking system is now ready!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
