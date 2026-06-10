# Emergency Contacts Feature - Testing Guide

## Prerequisites
- Backend server running on `http://localhost:8000`
- Frontend Flutter app running
- A test user account (email: pr@gmail.com)

---

## Step 1: Create Database Table

Run this command to create the emergency_contacts table:

```bash
cd backend
./venv/Scripts/python.exe create_emergency_table.py
```

Expected output:
```
Creating emergency_contacts table...
✅ Table created successfully!
✅ emergency_contacts table exists in database

Table columns:
  - id: INTEGER
  - user_id: INTEGER
  - name: VARCHAR
  - phone: VARCHAR
  - relationship_type: VARCHAR
  - email: VARCHAR
  - is_primary: INTEGER
  - created_at: DATETIME
  - updated_at: DATETIME
```

---

## Step 2: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## Step 3: Test Backend API (Optional but Recommended)

In a new terminal, run the test script:

```bash
cd backend
./venv/Scripts/python.exe test_emergency_contacts.py
```

This will test all API endpoints:
- ✅ Login
- ✅ Get contacts (empty initially)
- ✅ Create contact
- ✅ Update contact
- ✅ Delete contact

---

## Step 4: Test Frontend UI

### A. Navigate to Crisis Page

1. Open your Flutter app at `http://localhost:53965`
2. Login with test credentials
3. Navigate to the Crisis page (URL: `http://localhost:53965/#/crisis`)

### B. Test Adding a Contact

1. Scroll down to "Your Contacts" section
2. Click the **"Add Contact"** button (top right of the section)
3. Fill in the dialog form:
   - **Name**: Mom
   - **Phone Number**: (555) 123-4567
   - **Relationship**: Family
   - **Email**: mom@example.com (optional)
   - ✅ Check "Set as Primary Contact"
4. Click **"Add Contact"**

**Expected Result:**
- Success message: "Contact added successfully"
- Contact appears in "Your Contacts" list
- "PRIMARY" badge shown next to the name
- Contact shows: Name, Relationship, Phone number
- "Call" button and delete icon (trash) visible

### C. Test Calling a Contact

1. Click the **"Call"** button on a contact
2. Confirm dialog appears: "Call Mom at (555) 123-4567?"
3. Click **"Call"** to initiate (will open phone dialer)
   - Or click **"Cancel"** to close dialog

### D. Test Adding Multiple Contacts

Add 2-3 more contacts to verify:
- All contacts appear in the list
- Only one can have "PRIMARY" badge
- Contacts are sorted (Primary first, then by creation date)

Example contacts:
- **Dr. Smith** | (555) 234-5678 | Therapist
- **John (Brother)** | (555) 345-6789 | Family
- **Crisis Counselor** | (555) 456-7890 | Professional

### E. Test Deleting a Contact

1. Click the **trash icon** (delete button) on a contact
2. Confirmation dialog appears: "Are you sure you want to delete [Name]?"
3. Click **"Delete"**

**Expected Result:**
- Success message: "Contact deleted"
- Contact removed from the list
- List updates immediately

### F. Test Empty State

1. Delete all contacts
2. Verify empty state appears:
   - Icon: Contacts outline
   - Text: "No contacts yet"
   - Description: "Add trusted contacts for quick access during a crisis"
   - Button: "Add Your First Contact"

---

## Step 5: Verify Database Persistence

### Test 1: Reload Page
1. Add 2-3 contacts
2. Refresh the browser (F5)
3. Verify contacts are still there ✅

### Test 2: Logout and Login
1. Add contacts
2. Logout
3. Login again
4. Navigate to Crisis page
5. Verify contacts are loaded ✅

### Test 3: Different User
1. Create a new test user
2. Login with new user
3. Navigate to Crisis page
4. Verify it shows empty (contacts are user-specific) ✅

---

## Expected UI Layout

```
┌─────────────────────────────────────────┐
│  🔴 You matter                          │
│  If you're in crisis, please reach     │
│  out. Help is available 24/7.          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  📞 Get help now - Call 988             │
└─────────────────────────────────────────┘

Emergency Resources
┌─────────────────────────────────────────┐
│ National Crisis Hotline     [Call] 📞   │
│ 988                                     │
└─────────────────────────────────────────┘

Your Contacts              [+ Add Contact]
┌─────────────────────────────────────────┐
│ Mom ⭐ PRIMARY            [Call] 📞  🗑  │
│ Family                                  │
│ (555) 123-4567                         │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Dr. Smith                [Call] 📞  🗑  │
│ Therapist                               │
│ (555) 234-5678                         │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Issue: "Error loading contacts"
**Solution:**
- Check backend is running (`http://localhost:8000/health`)
- Check browser console for errors (F12 → Console)
- Verify token is valid (try logout/login)

### Issue: "Failed to create contact: 401"
**Solution:**
- Token expired, logout and login again
- Check Authorization header in browser network tab (F12 → Network)

### Issue: "Failed to create contact: 500"
**Solution:**
- Check backend logs for error details
- Verify database table was created
- Run `create_emergency_table.py` again

### Issue: Contacts not appearing
**Solution:**
- Check browser console for errors
- Check Network tab (F12) - look for 200 response from GET request
- Verify backend logs show successful request

### Issue: "Table not found" error
**Solution:**
- Run: `python create_emergency_table.py`
- Or restart backend (it auto-creates tables on startup)

---

## API Endpoints Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/emergency-contacts/` | Get all user contacts |
| POST | `/api/emergency-contacts/` | Create new contact |
| GET | `/api/emergency-contacts/{id}` | Get specific contact |
| PUT | `/api/emergency-contacts/{id}` | Update contact |
| DELETE | `/api/emergency-contacts/{id}` | Delete contact |
| PATCH | `/api/emergency-contacts/{id}/set-primary` | Set as primary |

All endpoints require `Authorization: Bearer {token}` header.

---

## Success Criteria ✅

- [✅] Table created in database
- [✅] Backend API responds correctly
- [✅] "Add Contact" button visible
- [✅] Dialog form works properly
- [✅] Contacts are saved to database
- [✅] Contacts appear in the list
- [✅] Primary badge shows correctly
- [✅] Call button works
- [✅] Delete button works
- [✅] Empty state appears when no contacts
- [✅] Contacts persist after reload
- [✅] Loading spinner shows while fetching

---

## Done! 🎉

Your emergency contacts feature is now fully functional!

Users can:
- Add trusted contacts for quick access during crisis
- Set a primary emergency contact
- Call contacts directly from the crisis page
- Manage (edit/delete) their contacts
- See empty state with helpful message when no contacts exist
