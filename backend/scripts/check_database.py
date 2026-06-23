"""
Database checker script for Mental Health Chatbot
Usage: python check_database.py
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.chat import Chat
from app.models.crisis import CrisisEvent
from app.models.feedback import Feedback


def check_database():
    """Check all tables in the database"""
    db = SessionLocal()

    try:
        print("\n" + "="*60)
        print("📊 MENTAL HEALTH CHATBOT - DATABASE STATUS")
        print("="*60)

        # Check Users
        users = db.query(User).all()
        print(f"\n👥 USERS TABLE: {len(users)} records")
        print("-" * 60)
        for user in users:
            print(f"  ID: {user.id} | Email: {user.email} | Username: {user.username}")
            print(f"  Active: {user.is_active} | Verified: {user.is_verified}")
            print(f"  Created: {user.created_at}")
            print("-" * 60)

        # Check Chats
        chats = db.query(Chat).all()
        print(f"\n💬 CHATS TABLE: {len(chats)} records")
        if chats:
            print("-" * 60)
            for chat in chats[:5]:  # Show first 5
                print(f"  ID: {chat.id} | User: {chat.user_id} | Session: {chat.session_id}")
                print(f"  Message: {chat.message[:50]}...")
                print(f"  Emotion: {chat.detected_emotion} (confidence: {chat.emotion_confidence})")
                print(f"  Crisis Score: {chat.crisis_score}")
                print("-" * 60)

        # Check Crisis Events
        crisis_events = db.query(CrisisEvent).all()
        print(f"\n🚨 CRISIS EVENTS TABLE: {len(crisis_events)} records")
        if crisis_events:
            print("-" * 60)
            for event in crisis_events:
                print(f"  ID: {event.id} | User: {event.user_id}")
                print(f"  Severity: {event.severity} | Score: {event.crisis_score}")
                print(f"  Resolved: {event.resolved}")
                print("-" * 60)

        # Check Feedback
        feedbacks = db.query(Feedback).all()
        print(f"\n⭐ FEEDBACK TABLE: {len(feedbacks)} records")

        print("\n" + "="*60)
        print("✅ Database check complete!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
    finally:
        db.close()


if __name__ == "__main__":
    check_database()
