"""
Check WhatsApp message delivery status
"""
import requests
from app.core.config import settings

# The message ID from the test
MESSAGE_ID = "wamid.HBgLOTQ3NzA0ODQ4MDYVAgARGBI0MTlDNEE4N0IzMTRDOTAzNTUA"

print("🔍 Checking WhatsApp message status...\n")

url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{MESSAGE_ID}"
headers = {
    "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
}

try:
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print("✅ Message found:")
        print(f"   Status: {data}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("📋 TROUBLESHOOTING STEPS:")
print("="*60)
print()
print("1. Add mom's number to approved list:")
print("   - Go to: https://developers.facebook.com/apps")
print("   - Select your app")
print("   - WhatsApp → API Setup")
print("   - Under 'To' field, click 'Manage phone number list'")
print("   - Add: +94770484806")
print("   - Click 'Save'")
print()
print("2. Check if mom's WhatsApp is active:")
print("   - Make sure +94770484806 has WhatsApp installed")
print("   - Make sure the number is correct")
print()
print("3. Check WhatsApp Business restrictions:")
print("   - In development mode, only approved numbers receive messages")
print("   - Meta sends messages but they get filtered out if not approved")
print()
print("4. Verify the number format:")
print("   - Your number: 94770484806")
print("   - Should be: +94 77 048 4806 (Sri Lanka)")
print()
print("="*60)
