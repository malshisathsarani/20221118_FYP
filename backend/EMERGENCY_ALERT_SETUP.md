# Emergency Alert System Setup Guide

## Overview
The emergency alert system sends SMS and voice call alerts to emergency contacts when a crisis is detected.

## Step 1: Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a **free trial account**
3. Verify your phone number
4. You'll receive **$15 in free trial credits**

## Step 2: Get Twilio Credentials

After signing up:

1. Go to Twilio Console: https://console.twilio.com/
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Click "Get a Trial Number" to get a free Twilio phone number

## Step 3: Add Credentials to .env File

Add these lines to `backend/.env`:

```env
# Twilio Emergency Alert Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number (include +country code)

# API URL (for voice call callbacks)
API_URL=http://localhost:8000
```

**Example:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
API_URL=http://localhost:8000
```

## Step 4: Install Twilio Package

```bash
cd backend
pip install twilio==9.0.0
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Step 5: Test the Setup

### Test Twilio Connection (API)

```bash
# Start the backend server
cd backend
uvicorn app.main:app --reload
```

Then test the endpoint:
```bash
curl -X GET "http://localhost:8000/api/emergency-alert/test-twilio" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test from Frontend

The emergency dialog will automatically appear when:
- Risk level is **HIGH** or **CRITICAL**
- User has emergency contacts configured

## Step 6: Add Emergency Contacts

Users must add emergency contacts before alerts can be sent:

1. Open the app
2. Go to Settings → Emergency Contacts
3. Add at least one contact with:
   - Name
   - Phone number (with country code, e.g., +15551234567)
   - Relationship

## How It Works

### Crisis Detection Flow

1. **User sends message** with crisis indicators
2. **ML models analyze** text + voice (if available)
3. **Risk assessment** determines crisis level
4. **If HIGH/CRITICAL risk:**
   - Emergency dialog appears with 30-second countdown
   - User can:
     - **Cancel** - Stops the alert
     - **Send Now** - Sends immediately
     - **Wait** - Alert auto-sends after 30 seconds

### What Gets Sent

**SMS Alert includes:**
- User's name
- Risk level (CRITICAL, HIGH, etc.)
- Risk score percentage
- Detected emotional state
- GPS location (if available)
- Google Maps link
- Timestamp

**Voice Call (for CRITICAL only):**
- Automated message explaining the emergency
- Asks contact to check on the user immediately

## Twilio Free Trial Limitations

- **$15 free credits** (enough for ~500 SMS or ~15 minutes of calls)
- Can only send to **verified phone numbers** during trial
- To verify a number:
  1. Go to Twilio Console → Phone Numbers → Verified Caller IDs
  2. Add the emergency contact's phone number
  3. They'll receive a verification code

## Upgrading from Trial

To remove limitations:
1. Add payment method to Twilio account
2. Upgrade to paid account (pay-as-you-go)
3. Pricing:
   - SMS: ~$0.0075 per message
   - Voice calls: ~$0.013 per minute

## Testing Tips

### Test with Your Own Number

1. Verify your own phone number in Twilio
2. Add yourself as an emergency contact
3. Trigger a crisis detection:
   - Send message: "I want to end it all"
   - System will detect high risk
   - Emergency dialog appears
   - You'll receive SMS/call

### Test Crisis Triggers

High-risk phrases that trigger alerts:
- "I want to die"
- "suicide"
- "kill myself"
- "end it all"
- "no point in living"
- "can't go on"

## Troubleshooting

### Error: "Twilio client not initialized"
- Check your `.env` file has correct credentials
- Restart the backend server

### Error: "Failed to send SMS"
- Verify the phone number format includes country code: `+15551234567`
- During trial, verify the recipient's number in Twilio Console

### Error: "HTTP 408 Timeout"
- Check your internet connection
- Twilio services might be slow - this is normal

### SMS Not Received
- Check recipient's phone number is correct
- During trial, number must be verified in Twilio
- Check Twilio Console → Logs for delivery status

## API Endpoints

### Send Emergency Alert
```
POST /api/emergency-alert/send
Authorization: Bearer <token>

Body:
{
  "contact_id": 1,
  "risk_level": "critical",
  "risk_score": 0.95,
  "detected_emotion": "severe distress",
  "crisis_reason": "Multiple crisis indicators detected",
  "latitude": 6.9271,
  "longitude": 79.8612,
  "send_sms": true,
  "make_call": false
}
```

### Get Emergency Contacts
```
GET /api/emergency-alert/contacts
Authorization: Bearer <token>
```

### Test Twilio Connection
```
GET /api/emergency-alert/test-twilio
Authorization: Bearer <token>
```

## Production Deployment

For production:

1. **Use environment variables** (not .env file)
2. **Set API_URL** to your production domain:
   ```env
   API_URL=https://yourdomain.com
   ```
3. **Upgrade Twilio account** to paid
4. **Monitor Twilio usage** in console
5. **Set up monitoring** for failed alerts

## Privacy & Security

- Emergency contacts are **encrypted** in database
- Phone numbers are **never logged** in plain text
- Alerts are sent over **Twilio's secure infrastructure**
- GPS coordinates are only sent when crisis detected
- User can **cancel** alerts before sending

## Support

- Twilio Support: https://support.twilio.com/
- Documentation: https://www.twilio.com/docs/sms
- Status Page: https://status.twilio.com/

---

**🚨 Important:** This is a **life-saving feature**. Test thoroughly before deploying to production!
