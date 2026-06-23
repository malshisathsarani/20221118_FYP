"""
Quick test script for WhatsApp Business API
Run: python test_whatsapp.py
"""
import requests
import json
from app.core.config import settings

def test_whatsapp():
    """Test WhatsApp API directly"""

    print("=" * 60)
    print("🧪 WHATSAPP BUSINESS API TEST")
    print("=" * 60)

    # Check credentials
    print("\n1️⃣ Checking credentials...")
    print(f"   Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    print(f"   API Version: {settings.WHATSAPP_API_VERSION}")
    print(f"   Access Token: {settings.WHATSAPP_ACCESS_TOKEN[:20]}...")

    if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
        print("   ❌ FAILED: WhatsApp credentials not configured in .env")
        return

    print("   ✅ Credentials loaded")

    # Test connection
    print("\n2️⃣ Testing WhatsApp API connection...")
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Connection successful!")
            print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
            print(f"   Display Number: {data.get('display_phone_number', 'N/A')}")
        else:
            print(f"   ❌ Connection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return

    # Send test message
    print("\n3️⃣ Sending test WhatsApp message...")
    print("   To: Meta test number (15556766037)")

    send_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "15556766037",  # Meta test number
        "type": "text",
        "text": {
            "preview_url": True,
            "body": "🧪 Test Alert from Mental Health Chatbot\n\nThis is a test message to verify WhatsApp integration is working!\n\n✅ If you received this, WhatsApp alerts are working perfectly!"
        }
    }

    try:
        response = requests.post(
            send_url,
            headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id", "N/A")
            print(f"   ✅ Message sent successfully!")
            print(f"   Message ID: {message_id}")
            print(f"\n   📱 Check WhatsApp on +1 555 676 6037 to confirm!")
        else:
            print(f"   ❌ Send failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {json.dumps(error_data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Send error: {e}")
        return

    # Send to mom's number
    print("\n4️⃣ Would you like to send a test to mom's number?")
    print("   (Make sure her number is approved in Meta dashboard first!)")
    mom_number = input("   Enter mom's WhatsApp number (or press Enter to skip): ").strip()

    if mom_number:
        # Clean number
        clean_number = ''.join(filter(str.isdigit, mom_number))
        print(f"\n   Sending to: {clean_number}")

        payload["to"] = clean_number
        payload["text"]["body"] = "🚨 MENTAL HEALTH CRISIS ALERT TEST\n\n👤 User: Malshi\n📊 Risk Level: TEST\n\nThis is a test message. If you received this, crisis alerts will work!\n\n_Sent by Mental Health Chatbot_"

        try:
            response = requests.post(
                send_url,
                headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                message_id = result.get("messages", [{}])[0].get("id", "N/A")
                print(f"   ✅ Message sent to mom successfully!")
                print(f"   Message ID: {message_id}")
                print(f"\n   📱 Check mom's WhatsApp to confirm!")
            else:
                print(f"   ❌ Send failed: {response.status_code}")
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
                if "is not a WhatsApp user" in str(error_data):
                    print("\n   ℹ️  Tip: Make sure the number is added to approved list in Meta dashboard")
        except Exception as e:
            print(f"   ❌ Send error: {e}")

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_whatsapp()
