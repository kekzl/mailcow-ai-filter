#!/usr/bin/env python3
"""
Upload Sieve filter to MailCow via API.

This script uploads the generated Sieve filter to your MailCow server
using the MailCow REST API.
"""

import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found.")
    print("Install it with: pip install requests")
    sys.exit(1)


def load_config():
    """Load configuration from config.yml."""
    try:
        import yaml

        config_file = Path(__file__).parent / 'config' / 'config.yml'
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        return None


def upload_filter(
    mailcow_url: str,
    api_key: str,
    username: str,
    script_data: str,
    filter_type: str = "prefilter",
    active: bool = True,
    verify_ssl: bool = True
):
    """Upload Sieve filter via MailCow API.

    Args:
        mailcow_url: MailCow server URL (e.g., https://mail.example.com)
        api_key: API key from MailCow admin panel
        username: Email address/mailbox username
        script_data: Sieve script content
        filter_type: 'prefilter' or 'postfilter'
        active: Whether to activate the filter immediately
        verify_ssl: Verify SSL certificate

    Returns:
        True if successful, False otherwise
    """
    url = f"{mailcow_url}/api/v1/add/filter"

    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }

    payload = {
        "username": username,
        "filter_type": filter_type,
        "script_desc": "AI-Generated Email Filter",
        "script_data": script_data,
        "active": "1" if active else "0"
    }

    try:
        print(f"📡 Uploading filter to {mailcow_url}...")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=verify_ssl,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                # MailCow API typically returns array with result objects
                first_result = result[0]
                if first_result.get('type') == 'success':
                    print(f"✅ {first_result.get('msg', 'Filter uploaded successfully!')}")
                    return True
                else:
                    print(f"❌ Error: {first_result.get('msg', 'Unknown error')}")
                    return False
            else:
                print(f"✅ Filter uploaded successfully!")
                return True
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Try running with --no-verify-ssl if using self-signed certificate")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Upload Sieve filter to MailCow via API'
    )
    parser.add_argument(
        '--mailcow-url',
        help='MailCow URL (e.g., https://mail.example.com)',
        default=None
    )
    parser.add_argument(
        '--api-key',
        help='MailCow API key',
        default=None
    )
    parser.add_argument(
        '--username',
        help='Email address/mailbox username',
        default=None
    )
    parser.add_argument(
        '--sieve-file',
        help='Path to Sieve filter file',
        default='output/generated.sieve'
    )
    parser.add_argument(
        '--filter-type',
        help='Filter type (prefilter or postfilter)',
        choices=['prefilter', 'postfilter'],
        default='prefilter'
    )
    parser.add_argument(
        '--no-verify-ssl',
        help='Disable SSL certificate verification',
        action='store_true'
    )
    parser.add_argument(
        '--inactive',
        help='Upload as inactive (disabled) filter',
        action='store_true'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("MailCow Sieve Filter Upload via API")
    print("=" * 70)
    print()

    # Load configuration
    config = load_config()

    # Get MailCow URL
    mailcow_url = args.mailcow_url
    if not mailcow_url:
        if config:
            # Try to infer from IMAP server
            imap_server = config.get('imap', {}).get('server', '')
            if imap_server:
                # Assume MailCow is on the same domain
                mailcow_url = f"https://{imap_server}"
                print(f"ℹ️  Using MailCow URL from config: {mailcow_url}")

        if not mailcow_url:
            mailcow_url = input("MailCow URL (e.g., https://mail.example.com): ")

    # Remove trailing slash
    mailcow_url = mailcow_url.rstrip('/')

    # Get API key
    api_key = args.api_key
    if not api_key:
        print()
        print("ℹ️  You need a MailCow API key:")
        print("   1. Login to MailCow as admin")
        print("   2. Go to System → API")
        print("   3. Create or copy your API key")
        print()
        api_key = input("API Key: ").strip()

    # Get username
    username = args.username
    if not username:
        if config:
            username = config.get('imap', {}).get('username', '')
            if username:
                print(f"ℹ️  Using username from config: {username}")

        if not username:
            username = input("Email address/username: ").strip()

    # Load Sieve filter
    sieve_file = Path(args.sieve_file)
    if not sieve_file.exists():
        print(f"❌ Sieve filter not found: {sieve_file}")
        print("Please run the email analysis first to generate the filter.")
        sys.exit(1)

    print(f"📄 Reading Sieve filter: {sieve_file}")
    script_data = sieve_file.read_text(encoding='utf-8')

    # Show preview
    lines = script_data.split('\n')
    print()
    print("📋 Filter Preview (first 20 lines):")
    print("-" * 70)
    for i, line in enumerate(lines[:20], 1):
        print(f"  {i:2d}  {line}")
    if len(lines) > 20:
        print(f"  ... ({len(lines) - 20} more lines)")
    print("-" * 70)
    print()

    # Ask for confirmation
    print(f"Upload Settings:")
    print(f"  • MailCow URL: {mailcow_url}")
    print(f"  • Username: {username}")
    print(f"  • Filter Type: {args.filter_type}")
    print(f"  • Active: {'No' if args.inactive else 'Yes'}")
    print(f"  • Verify SSL: {'No' if args.no_verify_ssl else 'Yes'}")
    print()

    response = input("❓ Upload this filter to MailCow? (y/n): ").lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled by user.")
        sys.exit(0)

    # Upload filter
    print()
    success = upload_filter(
        mailcow_url=mailcow_url,
        api_key=api_key,
        username=username,
        script_data=script_data,
        filter_type=args.filter_type,
        active=not args.inactive,
        verify_ssl=not args.no_verify_ssl
    )

    if success:
        print()
        print("=" * 70)
        print("✅ Filter uploaded successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Login to MailCow webmail")
        print("2. Go to Settings → Filters")
        print("3. Verify the filter is active and working")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ Upload failed")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("• Check your API key is valid")
        print("• Verify the MailCow URL is correct")
        print("• Ensure you have permission to add filters")
        print("• Check MailCow logs for errors")
        sys.exit(1)


if __name__ == '__main__':
    main()
