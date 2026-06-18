"""
Test script to verify the profile API implementation.
This tests the backend without running the server.
"""

import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.profile_service import ProfileService
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.schemas.profile import ProfileUpdate, PreferencesUpdate, PrivacySettingsUpdate

def test_profile_feature():
    """Test the complete profile feature"""
    db: Session = SessionLocal()

    try:
        print("=" * 60)
        print("PROFILE FEATURE TEST")
        print("=" * 60)

        # 1. Create a test user
        print("\n1. Creating test user...")
        auth_service = AuthService(db)

        try:
            user = auth_service.register(UserCreate(
                email="testprofile@example.com",
                username="testprofile",
                password="password123",
                full_name="Test Profile User"
            ))
            print(f"✓ User created: {user.email}")
        except Exception as e:
            print(f"Note: User might already exist: {e}")
            # Get existing user
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)
            user = user_repo.get_by_email("testprofile@example.com")

        # 2. Get profile
        print("\n2. Getting user profile...")
        profile_service = ProfileService(db)
        profile = profile_service.get_user_profile(user.id)

        print(f"✓ Profile loaded:")
        print(f"  - ID: {profile.id}")
        print(f"  - Email: {profile.email}")
        print(f"  - Username: {profile.username}")
        print(f"  - Full Name: {profile.full_name}")
        print(f"  - Notifications: {profile.notifications_enabled}")
        print(f"  - Email Notifications: {profile.email_notifications}")
        print(f"  - Data Sharing: {profile.data_sharing_consent}")
        print(f"  - Analytics: {profile.analytics_consent}")

        # 3. Update profile info
        print("\n3. Updating profile information...")
        updated_profile = profile_service.update_profile(
            user.id,
            ProfileUpdate(
                full_name="Updated Test User",
                phone_number="+1234567890",
                bio="This is a test bio for profile feature"
            )
        )
        print(f"✓ Profile updated:")
        print(f"  - Full Name: {updated_profile.full_name}")
        print(f"  - Phone: {updated_profile.phone_number}")
        print(f"  - Bio: {updated_profile.bio}")

        # 4. Update preferences
        print("\n4. Updating notification preferences...")
        updated_profile = profile_service.update_preferences(
            user.id,
            PreferencesUpdate(
                notifications_enabled=False,
                email_notifications=True
            )
        )
        print(f"✓ Preferences updated:")
        print(f"  - Notifications: {updated_profile.notifications_enabled}")
        print(f"  - Email Notifications: {updated_profile.email_notifications}")

        # 5. Update privacy settings
        print("\n5. Updating privacy settings...")
        updated_profile = profile_service.update_privacy_settings(
            user.id,
            PrivacySettingsUpdate(
                data_sharing_consent=True,
                analytics_consent=False
            )
        )
        print(f"✓ Privacy settings updated:")
        print(f"  - Data Sharing: {updated_profile.data_sharing_consent}")
        print(f"  - Analytics: {updated_profile.analytics_consent}")

        # 6. Get initials
        print("\n6. Getting user initials...")
        initials = profile_service.get_profile_initials(updated_profile)
        print(f"✓ Initials: {initials}")

        # 7. Verify all changes persisted
        print("\n7. Verifying data persistence...")
        final_profile = profile_service.get_user_profile(user.id)

        assert final_profile.full_name == "Updated Test User", "Full name not persisted"
        assert final_profile.phone_number == "+1234567890", "Phone not persisted"
        assert final_profile.notifications_enabled == False, "Notifications pref not persisted"
        assert final_profile.data_sharing_consent == True, "Privacy setting not persisted"

        print("✓ All data persisted correctly!")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)

        print("\n📋 SUMMARY:")
        print("- User Model: ✓ Extended with profile fields")
        print("- Profile Schemas: ✓ All schemas working")
        print("- Profile Repository: ✓ Database operations successful")
        print("- Profile Service: ✓ Business logic working")
        print("- Data Persistence: ✓ All changes saved to database")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

    return True

if __name__ == "__main__":
    success = test_profile_feature()
    sys.exit(0 if success else 1)
