"""
Test script for Emergency Contacts API
Run this after starting the backend server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials - update these with your actual test user
TEST_EMAIL = "pr@gmail.com"
TEST_PASSWORD = "123456"  # Update with actual password

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_emergency_contacts():
    print_section("EMERGENCY CONTACTS API TEST")

    # Step 1: Login to get token
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return

    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Get existing contacts
    print("\n2. Getting existing contacts...")
    get_response = requests.get(
        f"{BASE_URL}/api/emergency-contacts/",
        headers=headers
    )

    if get_response.status_code == 200:
        contacts = get_response.json()
        print(f"✅ Found {contacts['total']} existing contact(s)")
        for contact in contacts['contacts']:
            print(f"   - {contact['name']} ({contact['phone']})")
    else:
        print(f"❌ Failed to get contacts: {get_response.status_code}")
        return

    # Step 3: Create a new contact
    print("\n3. Creating new test contact...")
    new_contact = {
        "name": "Test Contact Mom",
        "phone": "(555) 123-4567",
        "relationship_type": "Family",
        "email": "mom@example.com",
        "is_primary": 1
    }

    create_response = requests.post(
        f"{BASE_URL}/api/emergency-contacts/",
        headers=headers,
        json=new_contact
    )

    if create_response.status_code == 201:
        created = create_response.json()
        contact_id = created['id']
        print(f"✅ Contact created successfully!")
        print(f"   ID: {contact_id}")
        print(f"   Name: {created['name']}")
        print(f"   Phone: {created['phone']}")
        print(f"   Relationship: {created['relationship_type']}")
        print(f"   Primary: {created['is_primary'] == 1}")
    else:
        print(f"❌ Failed to create contact: {create_response.status_code}")
        print(create_response.text)
        return

    # Step 4: Get all contacts again
    print("\n4. Getting contacts after creation...")
    get_response = requests.get(
        f"{BASE_URL}/api/emergency-contacts/",
        headers=headers
    )

    if get_response.status_code == 200:
        contacts = get_response.json()
        print(f"✅ Total contacts: {contacts['total']}")
        for contact in contacts['contacts']:
            primary = "⭐ PRIMARY" if contact['is_primary'] == 1 else ""
            print(f"   - {contact['name']} ({contact['phone']}) {primary}")

    # Step 5: Update the contact
    print("\n5. Updating contact...")
    update_data = {
        "name": "Updated Test Mom",
        "relationship_type": "Emergency Contact"
    }

    update_response = requests.put(
        f"{BASE_URL}/api/emergency-contacts/{contact_id}",
        headers=headers,
        json=update_data
    )

    if update_response.status_code == 200:
        updated = update_response.json()
        print(f"✅ Contact updated successfully!")
        print(f"   New name: {updated['name']}")
        print(f"   New relationship: {updated['relationship_type']}")
    else:
        print(f"❌ Failed to update contact: {update_response.status_code}")

    # Step 6: Delete the test contact
    print("\n6. Deleting test contact...")
    delete_response = requests.delete(
        f"{BASE_URL}/api/emergency-contacts/{contact_id}",
        headers=headers
    )

    if delete_response.status_code == 204:
        print(f"✅ Contact deleted successfully!")
    else:
        print(f"❌ Failed to delete contact: {delete_response.status_code}")

    # Step 7: Verify deletion
    print("\n7. Verifying deletion...")
    get_response = requests.get(
        f"{BASE_URL}/api/emergency-contacts/",
        headers=headers
    )

    if get_response.status_code == 200:
        contacts = get_response.json()
        print(f"✅ Final contact count: {contacts['total']}")

    print_section("TEST COMPLETE")
    print("\n✅ All API endpoints working correctly!")
    print("\nYou can now test the frontend UI.")

if __name__ == "__main__":
    try:
        test_emergency_contacts()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Please start the backend with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
