#!/usr/bin/env python3
"""
Create IMAP folders from generated Sieve filter.

This script:
1. Parses the generated Sieve filter to extract folder names
2. Shows the list of folders to be created
3. Asks for your permission before creating anything
4. Creates folders via IMAP
"""

import imaplib
import re
import sys


def extract_folders_from_sieve(sieve_file: str) -> list[str]:
    """Extract all folder names from a Sieve filter file.

    Args:
        sieve_file: Path to Sieve filter file

    Returns:
        List of unique folder paths
    """
    folders = set()

    with open(sieve_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all 'fileinto "folder/path"' statements
    pattern = r'fileinto\s+"([^"]+)"'
    matches = re.findall(pattern, content)

    for folder_path in matches:
        folders.add(folder_path)

        # Also add parent folders
        parts = folder_path.split("/")
        for i in range(1, len(parts)):
            parent = "/".join(parts[:i])
            folders.add(parent)

    return sorted(folders)


def connect_imap(server: str, username: str, password: str, use_ssl: bool = True, port: int = 993):
    """Connect to IMAP server.

    Args:
        server: IMAP server hostname
        username: Email address
        password: Password
        use_ssl: Use SSL/TLS
        port: Port number

    Returns:
        IMAP connection object
    """
    try:
        if use_ssl:
            conn = imaplib.IMAP4_SSL(server, port)
        else:
            conn = imaplib.IMAP4(server, port)

        conn.login(username, password)
        print(f"✅ Connected to {server}")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def get_existing_folders(conn) -> set[str]:
    """Get list of existing folders.

    Args:
        conn: IMAP connection

    Returns:
        Set of folder names
    """
    try:
        status, folder_list = conn.list()
        if status != "OK":
            return set()

        folders = set()
        for folder_data in folder_list:
            folder_str = folder_data.decode() if isinstance(folder_data, bytes) else folder_data
            parts = folder_str.split('"')

            if len(parts) >= 3:
                folder_name = parts[-1].strip()
                if folder_name:
                    folders.add(folder_name)

        return folders
    except Exception as e:
        print(f"⚠️  Error listing folders: {e}")
        return set()


def create_folder(conn, folder_name: str) -> bool:
    """Create a folder via IMAP.

    Args:
        conn: IMAP connection
        folder_name: Folder name to create

    Returns:
        True if successful
    """
    try:
        status, _ = conn.create(f'"{folder_name}"')
        if status == "OK":
            return True
        else:
            return False
    except Exception as e:
        print(f"  ❌ Error creating '{folder_name}': {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 70)
    print("IMAP Folder Creation Script")
    print("=" * 70)
    print()

    # Load configuration
    try:
        from pathlib import Path

        import yaml

        config_file = Path(__file__).parent / "config" / "config.yml"
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        imap_config = config.get("imap", {})
        server = imap_config.get("server")
        username = imap_config.get("username")
        password = imap_config.get("password")
        use_ssl = imap_config.get("use_ssl", True)
        port = imap_config.get("port", 993)

    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        print("Please enter IMAP credentials manually:")
        server = input("IMAP Server: ")
        username = input("Username: ")
        import getpass

        password = getpass.getpass("Password: ")
        use_ssl = input("Use SSL? (y/n): ").lower() == "y"
        port = int(input("Port (993 for SSL, 143 for non-SSL): "))

    # Find Sieve filter file
    sieve_file = Path(__file__).parent / "output" / "generated.sieve"

    if not sieve_file.exists():
        print(f"❌ Sieve filter not found: {sieve_file}")
        print("Please run the email analysis first to generate the filter.")
        sys.exit(1)

    # Extract folders from Sieve filter
    print(f"📄 Reading Sieve filter: {sieve_file}")
    folders_to_create = extract_folders_from_sieve(str(sieve_file))

    if not folders_to_create:
        print("⚠️  No folders found in Sieve filter.")
        sys.exit(0)

    print(f"\n📂 Found {len(folders_to_create)} folders in Sieve filter:")
    print()
    for folder in folders_to_create:
        print(f"  • {folder}")

    print()

    # Ask for confirmation
    response = input("❓ Do you want to create these folders? (y/n): ").lower()

    if response not in ["y", "yes"]:
        print("❌ Cancelled by user.")
        sys.exit(0)

    # Connect to IMAP
    print()
    print(f"🔌 Connecting to {server}...")
    conn = connect_imap(server, username, password, use_ssl, port)

    # Get existing folders
    print("📋 Checking existing folders...")
    existing_folders = get_existing_folders(conn)
    print(f"   Found {len(existing_folders)} existing folders")

    # Create new folders
    print()
    print("🔨 Creating folders...")
    print()

    created = 0
    skipped = 0
    failed = 0

    for folder in folders_to_create:
        if folder in existing_folders:
            print(f"  ⏭️  '{folder}' - already exists, skipping")
            skipped += 1
        else:
            # Ask for individual permission
            response = input(f"  ❓ Create '{folder}'? (y/n/all): ").lower()

            if response == "all":
                # Create this and all remaining without asking
                if create_folder(conn, folder):
                    print(f"  ✅ Created '{folder}'")
                    created += 1
                else:
                    print(f"  ❌ Failed to create '{folder}'")
                    failed += 1

                # Create remaining folders automatically
                for remaining_folder in folders_to_create:
                    if remaining_folder not in existing_folders and remaining_folder != folder:
                        if create_folder(conn, remaining_folder):
                            print(f"  ✅ Created '{remaining_folder}'")
                            created += 1
                        else:
                            print(f"  ❌ Failed to create '{remaining_folder}'")
                            failed += 1
                break

            elif response in ["y", "yes"]:
                if create_folder(conn, folder):
                    print(f"  ✅ Created '{folder}'")
                    created += 1
                else:
                    print(f"  ❌ Failed to create '{folder}'")
                    failed += 1
            else:
                print(f"  ⏭️  Skipped '{folder}'")
                skipped += 1

    # Disconnect
    conn.logout()

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Created:  {created}")
    print(f"⏭️  Skipped:  {skipped}")
    print(f"❌ Failed:   {failed}")
    print()
    print("Done! You can now upload the Sieve filter to MailCow.")


if __name__ == "__main__":
    main()
