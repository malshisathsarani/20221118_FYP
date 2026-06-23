"""
Test WhatsApp message to mom's number using exact app logic
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services.whatsapp_service import WhatsAppService
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_send_to_mom():
    """Test sending crisis alert to mom using the app's WhatsApp service"""

    print("\n" + "="*60)
    print("🧪 TESTING WHATSAPP ALERT TO MOM")
    print("="*60 + "\n")

    # Initialize WhatsApp service (same as app)
    whatsapp = WhatsAppService()

    # Mom's number from database
    mom_phone = "+94 77 048 4806"

    print(f"📱 Original phone: {mom_phone}")

    # Send crisis alert (same as app does)
    result = whatsapp.send_crisis_alert(
        to_number=mom_phone,
        user_name="Malshi (Test)",
        crisis_level="high",
        risk_score=0.85,
        detected_emotion="distressed",
        crisis_reason="TEST: Verifying WhatsApp integration from app",
        location=None
    )

    print("\n" + "="*60)
    print("📊 RESULT:")
    print("="*60)
    print(f"Success: {result.get('success')}")
    print(f"Message ID: {result.get('message_id')}")
    print(f"Error: {result.get('error')}")
    print(f"Error Code: {result.get('error_code')}")
    print("\nFull response:")
    import json
    print(json.dumps(result, indent=2))
    print("="*60 + "\n")

    if result.get('success'):
        print("✅ SUCCESS! Check mom's WhatsApp")
    else:
        print("❌ FAILED! See error above")
        print("\nPossible issues:")
        print("1. Phone number not in approved recipients list")
        print("2. Need to message business number first to open 24hr window")
        print("3. Access token expired")
        print("4. Phone number format issue")

if __name__ == "__main__":
    test_send_to_mom()
