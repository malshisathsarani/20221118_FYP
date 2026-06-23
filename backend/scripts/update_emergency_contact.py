"""
Clean up emergency contact phone numbers - remove spaces and special characters
"""
import sqlite3

print("🔧 Emergency Contact Phone Number Cleanup")
print("="*60)

# Connect to database
conn = sqlite3.connect('mental_health.db')
cursor = conn.cursor()

# Show current contacts
cursor.execute('SELECT id, user_id, name, phone FROM emergency_contacts')
contacts = cursor.fetchall()

print("\n📋 BEFORE - Current Emergency Contacts:")
for contact in contacts:
    print(f"   User {contact[1]} | ID: {contact[0]} | Name: {contact[2]} | Phone: {contact[3]}")

print("\n🧹 Cleaning phone numbers...")

# Clean all phone numbers
updated_count = 0
for contact in contacts:
    contact_id = contact[0]
    old_phone = contact[3]

    # Remove +, spaces, hyphens, parentheses
    clean_phone = old_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    if clean_phone != old_phone:
        cursor.execute(
            'UPDATE emergency_contacts SET phone = ? WHERE id = ?',
            (clean_phone, contact_id)
        )
        print(f"   ✓ Updated: {old_phone} → {clean_phone}")
        updated_count += 1
    else:
        print(f"   ✓ Already clean: {clean_phone}")

conn.commit()

# Show updated contacts
cursor.execute('SELECT id, user_id, name, phone FROM emergency_contacts')
contacts = cursor.fetchall()

print("\n📋 AFTER - Updated Emergency Contacts:")
for contact in contacts:
    print(f"   User {contact[1]} | ID: {contact[0]} | Name: {contact[2]} | Phone: {contact[3]}")

conn.close()

print("\n" + "="*60)
print(f"✅ Cleanup complete! Updated {updated_count} phone number(s)")
print("="*60)

print("\n⚠️  IMPORTANT: 24-Hour Messaging Window")
print("="*60)
print("WhatsApp Business API requires a 24-hour messaging window.")
print("For the app to send messages to mom, she needs to:")
print()
print("1. Find your WhatsApp Business number in Meta dashboard")
print("2. Send ANY message from her WhatsApp to that number")
print("   (Can just say 'Hi' or 'Test')")
print("3. Once she sends a message, your app can send alerts for 24 hours")
print("4. Each time she replies, the 24-hour window resets")
print()
print("Alternatively, use pre-approved Message Templates (no window needed)")
print("="*60)
