"""Ollama Email Summarizer - Worker tier implementation."""

from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Sequence

import requests

from src.application.ports.i_email_summarizer import IEmailSummarizer
from src.domain.entities.email import Email
from src.domain.value_objects.email_summary import EmailSummary

logger = logging.getLogger(__name__)


class OllamaEmailSummarizer(IEmailSummarizer):
    """Worker tier: Summarizes individual emails using fast Ollama model.

    This is the first tier in the two-tier architecture.
    Uses a smaller, faster model (e.g., qwen3:4b) to extract
    key information from each email independently.
    """

    def __init__(
        self,
        model: str = "qwen3:4b",
        base_url: str = "http://localhost:11434",
    ) -> None:
        """Initialize Ollama email summarizer.

        Args:
            model: Fast worker model for summarization
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.session = requests.Session()

        logger.info(f"Initialized OllamaEmailSummarizer with worker model {model}")

    def summarize(self, email: Email) -> EmailSummary:
        """Summarize a single email.

        Args:
            email: Email entity to summarize

        Returns:
            EmailSummary with extracted information
        """
        logger.debug(f"Summarizing email: {email.subject[:50]}...")

        # Create summarization prompt
        prompt = self._create_summarization_prompt(email)

        # Call Ollama
        response_text = self._call_ollama(prompt)

        # Parse response
        summary_data = self._parse_response(response_text, email)

        # Create EmailSummary
        return EmailSummary.create(
            email_id=email.message_id or email.subject[:50],
            sender_domain=email.sender.domain,
            category=summary_data["category"],
            topic=summary_data["topic"],
            keywords=summary_data["keywords"],
            folder=email.folder,
            received_at=email.received_at,
        )

    def summarize_batch(
        self, emails: Sequence[Email], max_parallel: int = 3
    ) -> list[EmailSummary]:
        """Summarize multiple emails in parallel.

        Args:
            emails: Collection of emails to summarize
            max_parallel: Maximum number of parallel requests

        Returns:
            List of email summaries
        """
        logger.info(
            f"Batch summarizing {len(emails)} emails with {max_parallel} parallel workers..."
        )

        summaries = []

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # Submit all tasks
            future_to_email = {
                executor.submit(self.summarize, email): email for email in emails
            }

            # Collect results as they complete
            for future in as_completed(future_to_email):
                email = future_to_email[future]
                try:
                    summary = future.result()
                    summaries.append(summary)
                except Exception as e:
                    logger.warning(
                        f"Failed to summarize email '{email.subject[:50]}': {e}"
                    )
                    # Create fallback summary
                    summaries.append(self._create_fallback_summary(email))

        logger.info(
            f"Completed batch summarization: {len(summaries)}/{len(emails)} succeeded"
        )
        return summaries

    def _create_summarization_prompt(self, email: Email) -> str:
        """Create prompt for email summarization.

        Args:
            email: Email to summarize

        Returns:
            Summarization prompt
        """
        prompt = f"""Extract email metadata as JSON.

Email data:
From: {email.sender.value}
Subject: {email.subject}
Body: {email.body[:200]}

Task: Analyze this email and determine its natural category.

category: Short category name describing the email type
- Examples: "CI/CD", "Orders", "Shipping", "Birthdays", "Newsletter", "GitHub", "Receipts"
- Use 1-3 words that best describe this email's purpose
- Be specific and descriptive based on content

topic: 2-5 word summary of the main subject

keywords: 3-5 lowercase keywords from subject/body

CRITICAL FORMATTING RULES:
1. Output ONLY valid JSON - all strings MUST be in double quotes
2. NO explanations, NO reasoning, NO markdown code blocks
3. DO NOT write "We are given", "Steps:", "Let me analyze", etc.
4. START your response with {{ and END with }}

CORRECT FORMAT (use this exact structure):
{{"category":"CI/CD","topic":"pipeline failure","keywords":["github","ci","failed"]}}

WRONG - DO NOT do this:
{{category:CI/CD,topic:pipeline failure,keywords:[github,ci,failed]}}

Your JSON output:"""
        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with worker model.

        Args:
            prompt: Summarization prompt

        Returns:
            Response text

        Raises:
            Exception: If request fails
        """
        response = self.session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Request JSON output format
                "options": {
                    "temperature": 0.1,  # Very low for consistent extraction
                    "num_predict": 200,  # Short response
                    "top_p": 0.9,
                },
            },
            timeout=30,  # Fast timeout for worker model
        )
        response.raise_for_status()

        result = response.json()
        return result.get("response", "")

    def _parse_response(self, response_text: str, email: Email) -> dict:
        """Parse Ollama response into structured data.

        Args:
            response_text: AI response
            email: Original email (for fallback)

        Returns:
            Dictionary with summary fields

        Raises:
            ValueError: If response cannot be parsed
        """
        if not response_text or not response_text.strip():
            raise ValueError("AI returned empty response")

        # Strip <think> tags if present
        cleaned_text = re.sub(
            r"<think>.*?</think>", "", response_text, flags=re.DOTALL | re.IGNORECASE
        )
        cleaned_text = cleaned_text.strip()

        # Extract JSON - try different patterns
        # 1. Try with code blocks
        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", cleaned_text, re.DOTALL
        )
        if json_match:
            json_str = json_match.group(1)
        # 2. Try finding first { to last }
        elif "{" in cleaned_text and "}" in cleaned_text:
            start = cleaned_text.find("{")
            end = cleaned_text.rfind("}") + 1
            json_str = cleaned_text[start:end]
        else:
            logger.warning(f"No JSON found in response: {cleaned_text[:200]}")
            raise ValueError("No JSON in response")

        # Parse JSON with fixes
        try:
            # Replace Unicode quotes
            json_str = json_str.replace("„", "").replace('"', "").replace('"', "")
            json_str = json_str.replace(""", "'").replace(""", "'")

            # Fix unquoted property names (e.g., {sender_type: "value"} → {"sender_type": "value"})
            json_str = re.sub(
                r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)", r'\1"\2"\3', json_str
            )

            # Fix unquoted string values after colons (e.g., "key": Value → "key": "Value")
            # Match: colon, optional space, unquoted word(s), then comma or closing brace
            json_str = re.sub(
                r":\s*([A-Z][a-zA-Z0-9/\-\s]+)(?=\s*[,}])", r': "\1"', json_str
            )

            # Fix unquoted array items (e.g., [item1, item2] → ["item1", "item2"])
            # Match items inside brackets that aren't already quoted
            json_str = re.sub(
                r"\[([^\]]+)\]",
                lambda m: "["
                + ", ".join(
                    (
                        f'"{item.strip()}"'
                        if not item.strip().startswith('"')
                        else item.strip()
                    )
                    for item in m.group(1).split(",")
                )
                + "]",
                json_str,
            )

            # DEBUG: Log the JSON string being parsed
            logger.debug(f"Attempting to parse JSON: {json_str[:200]}")

            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            logger.warning(f"Problematic JSON: {json_str[:500]}")
            raise ValueError(f"Invalid JSON: {e}")

        # Validate required fields
        required = ["category", "topic", "keywords"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")

        # Ensure keywords is a list
        if not isinstance(result["keywords"], list):
            result["keywords"] = [result["keywords"]]

        return result

    def _create_fallback_summary(self, email: Email) -> EmailSummary:
        """Create fallback summary when AI fails.

        Args:
            email: Email entity

        Returns:
            Basic EmailSummary with extracted info
        """
        logger.debug(f"Creating fallback summary for: {email.subject[:50]}")

        # Simple heuristics to determine category
        sender_domain = email.sender.domain.lower()
        subject_lower = email.subject.lower()

        # Determine dynamic category based on content
        if any(word in sender_domain for word in ["github", "gitlab"]) or any(
            word in subject_lower for word in ["pull request", "pr", "review"]
        ):
            category = "Code Reviews"
        elif any(word in sender_domain for word in ["jenkins", "ci"]) or any(
            word in subject_lower for word in ["ci", "cd", "pipeline", "build"]
        ):
            category = "CI/CD"
        elif any(word in subject_lower for word in ["order", "bestell", "confirmed"]):
            category = "Orders"
        elif any(
            word in subject_lower
            for word in ["ship", "delivery", "versand", "zugestellt"]
        ):
            category = "Shipping"
        elif any(word in subject_lower for word in ["birthday", "geburtstag"]):
            category = "Birthdays"
        elif any(word in subject_lower for word in ["friend", "freund"]):
            category = "Friends"
        elif any(word in subject_lower for word in ["finance", "stock", "aktien"]):
            category = "Finance"
        elif any(
            word in subject_lower
            for word in ["offer", "sale", "discount", "deal", "promotion"]
        ):
            category = "Promotions"
        elif any(word in sender_domain for word in ["newsletter", "news", "marketing"]):
            category = "Newsletter"
        elif "noreply" in sender_domain or "notification" in sender_domain:
            category = "Notifications"
        elif any(word in subject_lower for word in ["hi", "hello", "re:", "fwd:"]):
            category = "Social"
        else:
            category = "General"

        # Extract simple keywords from subject
        keywords = [word.lower() for word in email.subject.split() if len(word) > 3][:5]

        return EmailSummary.create(
            email_id=email.message_id or email.subject[:50],
            sender_domain=email.sender.domain,
            category=category,
            topic=email.subject[:50],
            keywords=keywords,
            folder=email.folder,
            received_at=email.received_at,
        )
