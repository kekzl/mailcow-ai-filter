"""IMAP Adapter - Implements IEmailFetcher port."""

from __future__ import annotations

import email
import imaplib
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from typing import Sequence

from src.application.ports.i_email_fetcher import IEmailFetcher
from src.domain.entities.email import Email
from src.domain.value_objects.email_address import EmailAddress

logger = logging.getLogger(__name__)


class IMAPAdapter(IEmailFetcher):
    """IMAP adapter for fetching emails."""

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        use_ssl: bool = True,
        port: int | None = None,
    ) -> None:
        """Initialize IMAP adapter.

        Args:
            server: IMAP server hostname
            username: Email address
            password: Password
            use_ssl: Use SSL/TLS
            port: Port number (default: 993 for SSL, 143 for non-SSL)
        """
        self.server = server
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.port = port or (993 if use_ssl else 143)
        self.connection: imaplib.IMAP4_SSL | imaplib.IMAP4 | None = None

        logger.info(f"Initialized IMAP adapter for {server}")

    def connect(self) -> None:
        """Establish connection to IMAP server.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)

            self.connection.login(self.username, self.password)
            logger.info(f"Connected to IMAP server {self.server}")

        except (imaplib.IMAP4.error, OSError, TimeoutError) as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise ConnectionError(f"IMAP connection failed: {e}") from e

    def disconnect(self) -> None:
        """Close connection to IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
            except (imaplib.IMAP4.error, OSError) as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.connection = None

    def fetch_emails(
        self,
        folder: str = "INBOX",
        since_date: datetime | None = None,
        max_emails: int | None = None,
        exclude_folders: list[str] | None = None,
    ) -> Sequence[Email]:
        """Fetch emails from server.

        Args:
            folder: Folder to fetch from (default: INBOX)
            since_date: Only fetch emails after this date
            max_emails: Maximum number of emails to fetch
            exclude_folders: Folders to exclude from fetching

        Returns:
            Sequence of Email entities

        Raises:
            ConnectionError: If not connected
            Exception: If fetching fails
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        logger.info(f"Fetching emails from folder '{folder}'...")

        try:
            # Select folder
            status, _ = self.connection.select(f'"{folder}"', readonly=True)
            if status != "OK":
                raise Exception(f"Failed to select folder {folder}")

            # Build search criteria
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                search_criteria = f"SINCE {date_str}"
            else:
                # Default to last 12 months
                cutoff_date = datetime.now() - timedelta(days=365)
                date_str = cutoff_date.strftime("%d-%b-%Y")
                search_criteria = f"SINCE {date_str}"

            # Search for emails
            status, message_ids = self.connection.search(None, search_criteria)
            if status != "OK":
                logger.warning("Date search failed, falling back to ALL")
                status, message_ids = self.connection.search(None, "ALL")
                if status != "OK":
                    return []

            id_list = message_ids[0].split()

            # Limit to max_emails most recent emails
            if max_emails and len(id_list) > max_emails:
                id_list = id_list[-max_emails:]

            # Reverse to get newest first
            id_list = list(reversed(id_list))

            emails = []
            for msg_id in id_list:
                email_entity = self._fetch_email(msg_id, folder)
                if email_entity:
                    emails.append(email_entity)

            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails

        except (imaplib.IMAP4.error, OSError, TimeoutError) as e:
            logger.error(f"Error fetching emails from {folder}: {e}")
            raise

    def list_folders(self) -> list[str]:
        """List all available folders.

        Returns:
            List of folder names
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            status, folder_list = self.connection.list()
            if status != "OK":
                return []

            folders = []
            for folder_data in folder_list:
                folder_str = (
                    folder_data.decode() if isinstance(folder_data, bytes) else folder_data
                )
                parts = folder_str.split('"')

                if len(parts) >= 3:
                    folder_name = parts[-1].strip()
                    if folder_name:
                        folders.append(folder_name)

            logger.info(f"Found {len(folders)} folders")
            return folders

        except (imaplib.IMAP4.error, OSError) as e:
            logger.error(f"Error listing folders: {e}")
            return []

    def get_folder_count(self, folder: str) -> int:
        """Get email count for a folder.

        Args:
            folder: Folder name

        Returns:
            Number of emails in folder
        """
        if not self.connection:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            status, messages = self.connection.select(f'"{folder}"', readonly=True)
            if status == "OK":
                count = int(messages[0].decode())
                return count
            return 0
        except (imaplib.IMAP4.error, OSError) as e:
            logger.error(f"Error getting folder count: {e}")
            return 0

    def _fetch_email(self, msg_id: bytes, folder_name: str) -> Email | None:
        """Fetch a single email message.

        Args:
            msg_id: Message ID
            folder_name: Current folder name

        Returns:
            Email entity or None
        """
        try:
            status, msg_data = self.connection.fetch(msg_id, "(RFC822)")
            if status != "OK":
                return None

            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract headers
            subject = self._decode_header(email_message.get("Subject", ""))
            from_addr = self._decode_header(email_message.get("From", ""))
            date_str = email_message.get("Date", "")

            # Parse date
            try:
                date = email.utils.parsedate_to_datetime(date_str)
            except (TypeError, ValueError):
                date = datetime.now()

            # Extract body
            body = self._extract_body(email_message)

            # Create EmailAddress value object
            # Extract email from "Name <email@domain.com>" format
            if "<" in from_addr and ">" in from_addr:
                email_addr = from_addr[from_addr.find("<") + 1 : from_addr.find(">")]
            else:
                email_addr = from_addr

            try:
                EmailAddress(email_addr)
            except ValueError:
                logger.warning(f"Invalid email address: {email_addr}, skipping")
                return None

            # Extract recipients (To header)
            to_header = self._decode_header(email_message.get("To", ""))
            recipients = []
            if to_header:
                # Simple parsing - split by comma
                recipient_list = [r.strip() for r in to_header.split(",")]
                for recipient in recipient_list:
                    if "<" in recipient and ">" in recipient:
                        recipient_addr = recipient[recipient.find("<") + 1 : recipient.find(">")]
                    else:
                        recipient_addr = recipient
                    if recipient_addr:
                        recipients.append(recipient_addr)

            # Create Email entity
            return Email.create(
                sender=email_addr,  # Pass string, not EmailAddress object
                recipients=recipients,
                subject=subject,
                body=body,
                received_at=date,  # Fixed: was received_date
                folder=folder_name,
            )

        except (imaplib.IMAP4.error, OSError, ValueError, UnicodeDecodeError) as e:
            logger.warning(f"Error fetching email {msg_id}: {e}")
            return None

    def _decode_header(self, header_value: str) -> str:
        """Decode email header value.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        result = []

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        result.append(part.decode(encoding))
                    except (UnicodeDecodeError, LookupError):
                        result.append(part.decode("utf-8", errors="ignore"))
                else:
                    result.append(part.decode("utf-8", errors="ignore"))
            else:
                result.append(str(part))

        return " ".join(result)

    def _extract_body(self, email_message: email.message.Message) -> str:
        """Extract body text from email message.

        Args:
            email_message: Email message object

        Returns:
            Body text
        """
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                            break
                    except (UnicodeDecodeError, AttributeError):
                        continue
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
            except (UnicodeDecodeError, AttributeError):
                body = ""

        return body[:500]  # Limit body length
