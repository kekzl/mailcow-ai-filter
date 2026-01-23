#!/usr/bin/env python3
"""
Fetch existing Sieve filters from mail server.

This script connects to your mail server and retrieves existing
Sieve filters so they can be included in the AI analysis.
"""

from pathlib import Path


def load_config():
    """Load configuration from config.yml."""
    try:
        import yaml

        config_file = Path(__file__).parent / "config" / "config.yml"
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        return config
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        return None


def fetch_via_managesieve(server: str, username: str, password: str, port: int = 4190):
    """Fetch filters via ManageSieve protocol.

    Args:
        server: Server hostname
        username: Email address
        password: Password
        port: ManageSieve port

    Returns:
        Dict of script name to content
    """
    try:
        from managesieve import MANAGESIEVE

        print(f"📡 Connecting to ManageSieve server {server}:{port}...")
        conn = MANAGESIEVE(server, port)
        conn.login(username, password)
        print("✅ Connected")

        # List all scripts
        scripts = conn.listscripts()
        print(f"📋 Found {len(scripts)} Sieve scripts")

        all_scripts = {}
        for script_name, is_active in scripts:
            marker = " (ACTIVE)" if is_active else ""
            print(f"   • {script_name}{marker}")

            # Fetch script content
            content = conn.getscript(script_name)
            all_scripts[script_name] = {"content": content, "active": is_active}

        conn.logout()
        return all_scripts

    except ImportError:
        print("❌ 'managesieve' library not installed")
        print("   Install with: pip install managesieve")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def fetch_via_imap_metadata(
    server: str, username: str, password: str, use_ssl: bool = True, port: int = 993
):
    """Attempt to fetch filter info via IMAP METADATA (limited).

    Args:
        server: IMAP server
        username: Email address
        password: Password
        use_ssl: Use SSL
        port: IMAP port

    Returns:
        Basic filter information if available
    """
    import imaplib

    try:
        print(f"📡 Connecting to IMAP server {server}:{port}...")

        if use_ssl:
            conn = imaplib.IMAP4_SSL(server, port)
        else:
            conn = imaplib.IMAP4(server, port)

        conn.login(username, password)
        print("✅ Connected")

        # Try to get metadata about filters
        # Note: This is limited and server-dependent
        try:
            status, data = conn.getmetadata(
                '""', "/private/vendor/vendor.dovecot/sieve"
            )
            if status == "OK":
                print("📋 Found Sieve metadata:")
                print(data)
        except Exception:
            print("⚠️  IMAP server doesn't support METADATA for Sieve")

        conn.logout()
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def parse_sieve_rules(script_content: str):
    """Parse Sieve script and extract rules.

    Args:
        script_content: Sieve script content

    Returns:
        List of rule dictionaries
    """
    if not script_content:
        return []

    rules = []
    lines = script_content.split("\n")
    current_description = ""
    in_rule = False
    current_rule = []

    for line in lines:
        stripped = line.strip()

        # Extract comments
        if stripped.startswith("#"):
            comment = stripped[1:].strip()
            if (
                comment
                and not comment.startswith("=")
                and not comment.startswith("Rule:")
            ):
                if "Description:" in comment:
                    current_description = comment.split("Description:")[1].strip()
                elif "Rule:" in comment:
                    # Skip rule headers
                    pass
                elif current_description:
                    current_description += " " + comment
                else:
                    current_description = comment

        # Detect rule start
        elif stripped.startswith("if "):
            in_rule = True
            current_rule = [line]

        # Inside rule
        elif in_rule:
            current_rule.append(line)
            # Check for rule end
            if "}" in stripped and "stop;" in stripped:
                # Rule complete
                rule_text = "\n".join(current_rule)

                # Extract destination folder
                import re

                folder_match = re.search(r'fileinto\s+"([^"]+)"', rule_text)
                folder = folder_match.group(1) if folder_match else "INBOX"

                # Extract conditions
                conditions = []
                if "address :domain :is" in rule_text:
                    domain_matches = re.findall(
                        r'address :domain :is "from" "([^"]+)"', rule_text
                    )
                    conditions.extend([f"from:{domain}" for domain in domain_matches])

                if "header :contains" in rule_text:
                    header_matches = re.findall(
                        r'header :contains "([^"]+)" "([^"]+)"', rule_text
                    )
                    conditions.extend(
                        [f"{header}:{value}" for header, value in header_matches]
                    )

                rules.append(
                    {
                        "description": current_description or "Unknown rule",
                        "folder": folder,
                        "conditions": conditions,
                        "rule_text": rule_text,
                    }
                )

                current_description = ""
                in_rule = False
                current_rule = []

    return rules


def save_existing_filters(
    scripts: dict, output_file: str = "output/existing_filters.txt"
):
    """Save existing filters to file for AI analysis.

    Args:
        scripts: Dict of script name to script data
        output_file: Where to save the summary
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("EXISTING SIEVE FILTERS\n")
        f.write("=" * 70 + "\n\n")

        for script_name, script_data in scripts.items():
            content = script_data["content"]
            is_active = script_data["active"]

            f.write(f"\n## Script: {script_name}\n")
            f.write(f"Status: {'ACTIVE' if is_active else 'Inactive'}\n")
            f.write("-" * 70 + "\n\n")

            # Parse rules
            rules = parse_sieve_rules(content)

            if rules:
                f.write(f"Found {len(rules)} filter rules:\n\n")
                for i, rule in enumerate(rules, 1):
                    f.write(f"{i}. {rule['description']}\n")
                    f.write(f"   → Folder: {rule['folder']}\n")
                    if rule["conditions"]:
                        f.write("   → Conditions:\n")
                        for cond in rule["conditions"]:
                            f.write(f"      - {cond}\n")
                    f.write("\n")
            else:
                f.write("No rules found (empty or custom script)\n\n")

            # Also save full script
            f.write("Full script:\n")
            f.write("```sieve\n")
            f.write(content)
            f.write("\n```\n\n")

    print(f"✅ Saved existing filters to: {output_path}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("Fetch Existing Sieve Filters")
    print("=" * 70)
    print()

    # Load configuration
    config = load_config()

    if config:
        imap_config = config.get("imap", {})
        server = imap_config.get("server")
        username = imap_config.get("username")
        password = imap_config.get("password")
        imap_config.get("port", 993)
        imap_config.get("use_ssl", True)

        print("📋 Using config from config.yml:")
        print(f"   Server: {server}")
        print(f"   Username: {username}")
        print()
    else:
        print("Enter connection details:")
        server = input("Server: ")
        username = input("Username: ")
        import getpass

        password = getpass.getpass("Password: ")

    # Try ManageSieve first (port 4190)
    print("Attempting ManageSieve connection (port 4190)...")
    scripts = fetch_via_managesieve(server, username, password)

    if scripts:
        print()
        print("=" * 70)
        print(f"✅ Retrieved {len(scripts)} scripts")
        print("=" * 70)
        print()

        # Save to file
        save_existing_filters(scripts)

        print()
        print("Next steps:")
        print("1. Review output/existing_filters.txt")
        print(
            "2. Re-run the email analysis - it will now consider your existing filters"
        )
        print("3. New filters will complement (not duplicate) existing ones")

    else:
        print()
        print("=" * 70)
        print("⚠️  Could not fetch filters via ManageSieve")
        print("=" * 70)
        print()
        print("Alternative options:")
        print("1. Check if ManageSieve is enabled on your server (port 4190)")
        print("2. Install managesieve library: pip install managesieve")
        print("3. Manually export your filters from MailCow webmail")


if __name__ == "__main__":
    main()
