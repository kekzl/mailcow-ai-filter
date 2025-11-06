#!/usr/bin/env python3
"""
Apply Sieve Filters Retroactively

This script reads the generated Sieve filter and applies it to existing emails
in your mailbox. It moves emails from INBOX to their target folders based on
the filter rules.

WARNING: This modifies your existing emails. Make sure you have backups!
"""

import re
import sys
import yaml
import imaplib
import email
from pathlib import Path
from email.header import decode_header
from typing import List, Dict, Tuple, Optional


class SieveFilterParser:
    """Parse Sieve filter rules from generated.sieve"""

    def __init__(self, sieve_file: Path):
        self.sieve_file = sieve_file
        self.rules = []

    def parse(self) -> List[Dict]:
        """Parse Sieve filter and extract rules"""
        print(f"📖 Parsing Sieve filter: {self.sieve_file}")

        with open(self.sieve_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract each filter rule block
        # Pattern: if anyof (...) { fileinto "folder"; stop; }
        pattern = r'if\s+anyof\s*\((.*?)\)\s*\{\s*fileinto\s+"([^"]+)"\s*;'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            conditions_block = match.group(1)
            target_folder = match.group(2)

            conditions = self._parse_conditions(conditions_block)

            if conditions:
                self.rules.append({
                    'folder': target_folder,
                    'conditions': conditions
                })

        print(f"✅ Parsed {len(self.rules)} filter rules")
        return self.rules

    def _parse_conditions(self, conditions_block: str) -> List[Dict]:
        """Parse individual conditions from the anyof block"""
        conditions = []

        # Pattern: address :domain :is "from" "example.com"
        domain_pattern = r'address\s+:domain\s+:is\s+"from"\s+"([^"]+)"'
        for match in re.finditer(domain_pattern, conditions_block):
            conditions.append({
                'type': 'from_domain',
                'value': match.group(1)
            })

        # Pattern: header :contains "subject" "keyword"
        subject_pattern = r'header\s+:contains\s+"subject"\s+"([^"]+)"'
        for match in re.finditer(subject_pattern, conditions_block):
            conditions.append({
                'type': 'subject_contains',
                'value': match.group(1).lower()
            })

        # Pattern: header :contains "from" "sender"
        from_pattern = r'header\s+:contains\s+"from"\s+"([^"]+)"'
        for match in re.finditer(from_pattern, conditions_block):
            conditions.append({
                'type': 'from_contains',
                'value': match.group(1).lower()
            })

        return conditions


class RetroactiveFilterApplicator:
    """Apply parsed filter rules to existing emails"""

    def __init__(self, imap_config: Dict, rules: List[Dict]):
        self.config = imap_config
        self.rules = rules
        self.imap = None
        self.stats = {
            'processed': 0,
            'moved': 0,
            'errors': 0,
            'by_folder': {}
        }

    def connect(self):
        """Connect to IMAP server"""
        print(f"\n🔌 Connecting to IMAP: {self.config['server']}:{self.config['port']}")

        if self.config.get('use_ssl', True):
            self.imap = imaplib.IMAP4_SSL(
                self.config['server'],
                self.config['port']
            )
        else:
            self.imap = imaplib.IMAP4(
                self.config['server'],
                self.config['port']
            )

        self.imap.login(
            self.config['username'],
            self.config['password']
        )
        print("✅ Connected successfully")

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def apply_filters(self, source_folder: str = "INBOX", dry_run: bool = False):
        """Apply filters to emails in source folder"""
        print(f"\n📬 Processing emails in: {source_folder}")
        if dry_run:
            print("🔍 DRY RUN MODE - No emails will be moved\n")

        # Select source folder
        status, data = self.imap.select(source_folder)
        if status != 'OK':
            print(f"❌ Failed to select folder: {source_folder}")
            return

        # Get all email IDs
        status, data = self.imap.search(None, 'ALL')
        if status != 'OK':
            print("❌ Failed to search emails")
            return

        email_ids = data[0].split()
        total_emails = len(email_ids)

        if total_emails == 0:
            print(f"📭 No emails found in {source_folder}")
            return

        print(f"📊 Found {total_emails} emails to process\n")

        # Process each email
        for i, email_id in enumerate(email_ids, 1):
            self.stats['processed'] += 1

            # Fetch email
            status, data = self.imap.fetch(email_id, '(RFC822)')
            if status != 'OK':
                self.stats['errors'] += 1
                continue

            # Parse email
            msg = email.message_from_bytes(data[0][1])

            # Extract headers
            from_addr = self._decode_header(msg.get('From', ''))
            subject = self._decode_header(msg.get('Subject', ''))

            # Find matching rule
            target_folder = self._find_matching_folder(from_addr, subject)

            if target_folder:
                # Show progress
                print(f"[{i}/{total_emails}] ✉️  '{subject[:50]}...'")
                print(f"           → Moving to: {target_folder}")

                if not dry_run:
                    # Move email
                    if self._move_email(email_id, target_folder):
                        self.stats['moved'] += 1
                        self.stats['by_folder'][target_folder] = \
                            self.stats['by_folder'].get(target_folder, 0) + 1
                    else:
                        self.stats['errors'] += 1
                else:
                    self.stats['moved'] += 1
                    self.stats['by_folder'][target_folder] = \
                        self.stats['by_folder'].get(target_folder, 0) + 1
            else:
                # No matching rule - show occasionally
                if i % 50 == 0:
                    print(f"[{i}/{total_emails}] Processing...")

        print("\n" + "="*60)
        self._print_statistics()

    def _find_matching_folder(self, from_addr: str, subject: str) -> Optional[str]:
        """Find target folder based on filter rules"""
        from_lower = from_addr.lower()
        subject_lower = subject.lower()

        for rule in self.rules:
            # Check if any condition matches
            for condition in rule['conditions']:
                if condition['type'] == 'from_domain':
                    if f"@{condition['value']}" in from_lower:
                        return rule['folder']

                elif condition['type'] == 'subject_contains':
                    if condition['value'] in subject_lower:
                        return rule['folder']

                elif condition['type'] == 'from_contains':
                    if condition['value'] in from_lower:
                        return rule['folder']

        return None

    def _move_email(self, email_id: bytes, target_folder: str) -> bool:
        """Move email to target folder"""
        try:
            # Create folder if it doesn't exist
            self.imap.create(target_folder)

            # Copy to target folder
            result = self.imap.copy(email_id, target_folder)
            if result[0] == 'OK':
                # Mark original as deleted
                self.imap.store(email_id, '+FLAGS', '\\Deleted')
                return True
        except Exception as e:
            print(f"    ❌ Error moving email: {e}")

        return False

    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        result = []

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or 'utf-8', errors='ignore'))
                except:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(str(part))

        return ''.join(result)

    def _print_statistics(self):
        """Print processing statistics"""
        print(f"\n📊 Processing Statistics:")
        print(f"   Total processed: {self.stats['processed']}")
        print(f"   Moved:          {self.stats['moved']}")
        print(f"   Errors:         {self.stats['errors']}")
        print(f"   Unchanged:      {self.stats['processed'] - self.stats['moved'] - self.stats['errors']}")

        if self.stats['by_folder']:
            print(f"\n📁 Emails moved by folder:")
            for folder, count in sorted(self.stats['by_folder'].items(),
                                       key=lambda x: x[1], reverse=True):
                print(f"   {folder}: {count}")


def main():
    """Main entry point"""
    print("="*60)
    print("Apply Sieve Filters Retroactively")
    print("="*60)

    # Check if sieve filter exists
    sieve_file = Path("output/generated.sieve")
    if not sieve_file.exists():
        print("❌ Error: output/generated.sieve not found")
        print("   Run './mailcow-filter.sh analyze' first to generate filters")
        sys.exit(1)

    # Load configuration
    config_file = Path("config/config.yml")
    if not config_file.exists():
        print("❌ Error: config/config.yml not found")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Parse Sieve filter
    parser = SieveFilterParser(sieve_file)
    rules = parser.parse()

    if not rules:
        print("❌ No filter rules found in generated.sieve")
        sys.exit(1)

    # Show what will be done
    print(f"\n📋 Filter rules to apply:")
    for i, rule in enumerate(rules, 1):
        print(f"   {i}. {rule['folder']} ({len(rule['conditions'])} conditions)")

    # Ask for confirmation
    print(f"\n⚠️  WARNING: This will move existing emails in your INBOX")
    print(f"   Source folder: INBOX")
    print(f"   Target folders: {len(rules)} different folders")
    print(f"   Server: {config['imap']['server']}")

    print(f"\n🔍 First, let's do a DRY RUN to see what would happen...")
    response = input("   Run dry run? (Y/n): ").strip().lower()

    if response == 'n':
        print("❌ Cancelled")
        sys.exit(0)

    # Dry run
    applicator = RetroactiveFilterApplicator(config['imap'], rules)
    try:
        applicator.connect()
        applicator.apply_filters(dry_run=True)
        applicator.disconnect()
    except Exception as e:
        print(f"\n❌ Error during dry run: {e}")
        sys.exit(1)

    # Ask if they want to proceed with actual move
    print(f"\n{'='*60}")
    print(f"💡 Dry run complete. No emails were actually moved.")
    print(f"{'='*60}")

    response = input("\n   Proceed with ACTUAL email moving? (yes/no): ").strip().lower()

    if response != 'yes':
        print("❌ Cancelled. No emails were moved.")
        sys.exit(0)

    # Apply filters for real
    print(f"\n🚀 Applying filters to existing emails...")
    applicator = RetroactiveFilterApplicator(config['imap'], rules)
    try:
        applicator.connect()
        applicator.apply_filters(dry_run=False)

        # Expunge deleted emails
        print(f"\n🗑️  Expunging deleted emails from INBOX...")
        applicator.imap.expunge()

        applicator.disconnect()

        print(f"\n✅ All done! Your existing emails have been organized.")
        print(f"   Check your email client to see the results.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        applicator.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()
