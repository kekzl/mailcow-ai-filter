#!/usr/bin/env python3
"""Quick IMAP connection test"""

import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('MAIL_SERVER')
username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')

print(f"Testing IMAP connection to {server}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)} ({len(password)} chars)")
print()

try:
    print("Connecting to IMAP...")
    conn = imaplib.IMAP4_SSL(server, 993)
    print("✅ SSL connection established")

    print(f"Logging in as {username}...")
    conn.login(username, password)
    print("✅ Authentication successful!")

    print("\nFetching folders...")
    status, folders = conn.list()
    if status == 'OK':
        print(f"✅ Found {len(folders)} folders:")
        for folder in folders[:10]:  # Show first 10
            print(f"  - {folder.decode()}")

    conn.logout()
    print("\n✅ All tests passed!")

except imaplib.IMAP4.error as e:
    print(f"\n❌ IMAP Error: {e}")
    print("\nPossible solutions:")
    print("1. Check your password is correct")
    print("2. Try logging in via webmail first")
    print("3. Check if you need an app-specific password")
    print("4. Verify IMAP is enabled for your account")

except Exception as e:
    print(f"\n❌ Error: {e}")
