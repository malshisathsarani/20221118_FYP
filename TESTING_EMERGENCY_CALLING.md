# Testing Emergency Calling System

## Quick Test Guide

### Step 1: Install Dependencies

**Frontend:**
```bash
cd frontend
flutter pub get
```

**Backend:**
```bash
cd backend
pip install twilio
# Or install all:
pip install -r requirements.txt
```

### Step 2: Add Twilio Credentials (Optional for initial test)

If you want to actually send SMS, add to `backend/.env`:

```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+your_number
```

**Don't have Twilio yet?** The dialog will still show! You just won't send real SMS.

### Step 3: Add an Emergency Contact

1. Run the app
2. Login as user: `pr@gmail.com`
3. Go to Settings → Emergency Contacts
4. Add a contact:
   - Name: Test Contact
   - Phone: +1234567890 (any format for testing)
   - Relationship: Friend

### Step 4: Trigger Crisis

Send any of these messages:
- "I want to die"
- "I want to end it all"
- "I'm thinking about suicide"
- "No point in living"
- "Kill myself"

### Step 5: Watch for Emergency Dialog

✅ **What should happen:**

1. **Message sends** - Crisis is detected
2. **Red crisis banner appears** at top
3. **Emergency dialog pops up** automatically with:
   - ⚠️ "CRISIS ALERT DETECTED"
   - Risk score and level
   - 30-second countdown timer
   - Emergency contact dropdown
   - "CANCEL" and "SEND NOW" buttons

4. **Countdown starts** at 30 seconds
   - You can cancel
   - You can send now
   - Or wait - it auto-sends at 0

5. **When sent** (if Twilio configured):
   - SMS goes to emergency contact
   - Success message shows
   - Dialog closes

### What You Should See in Logs

**Backend logs:**
```
INFO:     127.0.0.1:xxxxx - "POST /api/chat/.../message HTTP/1.1" 201 Created
crisis_score: 0.6345
is_crisis: 1  <-- Crisis detected!
```

**Expected crisis scores:**
- "I want to die" → ~0.63-0.75 (HIGH)
- "Kill myself" → ~0.75-0.90 (CRITICAL)
- "No hope" → ~0.45-0.60 (MODERATE)

## Troubleshooting

### ❌ Dialog doesn't appear

**Check 1:** Is crisis score high enough?
```
# In logs, look for:
crisis_score: 0.6345  # Should be > 0.45 for is_crisis=1
is_crisis: 1  # Should be 1, not 0
```

**Check 2:** Do you have emergency contacts?
- Go to Settings → Emergency Contacts
- Add at least one contact

**Check 3:** Frontend errors?
```bash
# In Flutter console, look for:
Error showing emergency dialog: ...
```

### ❌ Countdown doesn't work

The countdown should:
- Start at 30 seconds
- Decrease every second
- Show "Auto-sending in X seconds"

If not working, check browser console for errors.

### ❌ SMS doesn't send

**Without Twilio credentials:**
- Dialog will show ✅
- Countdown will work ✅
- But SMS won't actually send ❌
- You'll see error: "Twilio client not initialized"

**With Twilio (trial):**
- Need to verify recipient phone number first
- Go to Twilio Console → Verified Caller IDs
- Add the emergency contact's number
- They'll get verification code

## Test Checklist

- [ ] Crisis detected when typing "I want to die"
- [ ] Emergency dialog appears automatically
- [ ] Countdown starts at 30 seconds
- [ ] Can select different emergency contacts
- [ ] "Cancel" button stops the countdown
- [ ] "Send Now" button sends immediately
- [ ] Auto-sends after countdown reaches 0
- [ ] GPS location included (if permissions granted)
- [ ] Success message shows after sending

## Debug Mode

To see more detailed logs, check:

**Backend console:**
- Crisis detection results
- Risk scores
- Twilio API calls

**Flutter console:**
- Dialog opening
- Location requests
- API calls to emergency-alert endpoint

**Browser DevTools (if web):**
- Network tab → Check `/api/emergency-alert/send`
- Console → Look for JavaScript errors

## Next Steps

Once basic test works:

1. **Set up real Twilio** (see EMERGENCY_ALERT_SETUP.md)
2. **Test with real phone number**
3. **Verify SMS actually arrives**
4. **Test voice call** (for critical only)
5. **Test GPS location** in SMS

---

**🚨 Remember:** This is a life-saving feature. Test thoroughly!
