"""Ollama Adapter - Implements ILLMService port."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Sequence

import requests

from src.application.ports.i_llm_service import ILLMService
from src.domain.entities.email import Email
from src.domain.value_objects.email_cluster import EmailCluster
from src.domain.value_objects.email_summary import EmailSummary

logger = logging.getLogger(__name__)


class OllamaAdapter(ILLMService):
    """Ollama adapter for local LLM analysis."""

    def __init__(
        self,
        model: str = "qwen3:14b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        num_predict: int = 6000,
        top_p: float = 0.9,
    ) -> None:
        """Initialize Ollama adapter.

        Args:
            model: Ollama model to use
            base_url: Ollama server URL
            temperature: Sampling temperature (0-1, higher = more creative)
            num_predict: Maximum tokens to generate
            top_p: Nucleus sampling parameter
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.num_predict = num_predict
        self.top_p = top_p
        self.session = requests.Session()

        logger.info(
            f"Initialized Ollama adapter with model {model} "
            f"(temp={temperature}, max_tokens={num_predict})"
        )
        self._verify_ollama()

    def _verify_ollama(self) -> None:
        """Verify Ollama is running and model is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available: {model_names}")
                logger.info(f"Run: ollama pull {self.model}")
        except (requests.RequestException, OSError) as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            logger.info("Ensure Ollama is running: ollama serve")

    def analyze_emails(
        self,
        emails: Sequence[Email],
        max_sample: int = 20,
    ) -> dict[str, Any]:
        """Analyze emails and detect patterns/categories.

        Args:
            emails: Collection of emails to analyze
            max_sample: Maximum emails to include in analysis

        Returns:
            Dictionary containing categories

        Raises:
            Exception: If analysis fails
            TimeoutError: If analysis times out
        """
        logger.info(f"Analyzing {len(emails)} emails with Ollama ({self.model})...")

        # Prepare email sample
        email_sample = self._prepare_email_sample(emails, max_sample)

        # Create prompt
        prompt = self._create_analysis_prompt(email_sample)

        try:
            # Call Ollama
            response_text = self._call_ollama(prompt)

            # Parse response
            result = self._parse_response(response_text)

            logger.info(f"Ollama identified {len(result.get('categories', []))} categories")
            return result

        except (requests.RequestException, json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"Ollama analysis failed: {e}", exc_info=True)
            raise

    def analyze_summaries(
        self,
        summaries: Sequence[EmailSummary],
        max_sample: int = 100,
        existing_folders: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Analyze email summaries and detect hierarchical patterns (Master tier).

        This is the second tier in the two-tier architecture.
        Uses the master model to analyze patterns across all email summaries
        and create a smart hierarchical folder structure.

        Args:
            summaries: Collection of email summaries from worker tier
            max_sample: Maximum summaries to include in analysis
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Dictionary containing hierarchical categories

        Raises:
            Exception: If analysis fails
            TimeoutError: If analysis times out
        """
        logger.info(
            f"Analyzing {len(summaries)} email summaries with master model ({self.model})..."
        )

        # Prepare summary sample
        summary_sample = self._prepare_summary_sample(summaries, max_sample)

        # Create master analysis prompt
        prompt = self._create_master_analysis_prompt(summary_sample, existing_folders)

        try:
            # Call Ollama with master model
            response_text = self._call_ollama(prompt)

            # Parse response
            result = self._parse_response(response_text)

            logger.info(f"Master model identified {len(result.get('categories', []))} categories")
            return result

        except (requests.RequestException, json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"Master model analysis failed: {e}", exc_info=True)
            raise

    def analyze_clusters(
        self,
        clusters: Sequence[EmailCluster],
        max_representatives: int = 3,
        existing_folders: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Analyze email clusters and label them with categories (Embedding mode).

        This is the embedding-mode equivalent of analyze_summaries().
        For each cluster, looks at representative emails and determines
        the category name, patterns, and filtering rules.

        Args:
            clusters: Collection of email clusters to analyze
            max_representatives: Maximum representative emails per cluster
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Dictionary containing hierarchical categories

        Raises:
            Exception: If analysis fails
            TimeoutError: If analysis times out
        """
        logger.info(
            f"Analyzing {len(clusters)} email clusters with master model ({self.model})..."
        )

        # Create cluster analysis prompt
        prompt = self._create_cluster_analysis_prompt(
            clusters, max_representatives, existing_folders
        )

        try:
            # Call Ollama with master model
            response_text = self._call_ollama(prompt)

            # Parse response
            result = self._parse_response(response_text)

            logger.info(f"Master model identified {len(result.get('categories', []))} categories")
            return result

        except (requests.RequestException, json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"Cluster analysis failed: {e}", exc_info=True)
            raise

    def health_check(self) -> bool:
        """Check if Ollama service is available.

        Returns:
            True if service is healthy
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.RequestException, OSError):
            return False

    def get_model_info(self) -> dict[str, str]:
        """Get information about the Ollama model.

        Returns:
            Dictionary with model details
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"] == self.model:
                        return {
                            "provider": "ollama",
                            "model": self.model,
                            "size": model.get("size", "unknown"),
                            "modified": model.get("modified_at", "unknown"),
                        }
        except (requests.RequestException, KeyError, OSError):
            pass

        return {
            "provider": "ollama",
            "model": self.model,
            "status": "unknown",
        }

    def _call_ollama(
        self, prompt: str, max_retries: int = 3, base_delay: float = 2.0
    ) -> str:
        """Call Ollama API with retry logic.

        Args:
            prompt: Analysis prompt
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff

        Returns:
            Response text

        Raises:
            TimeoutError: If request times out after all retries
            requests.RequestException: If request fails after all retries
        """
        logger.info(f"Calling Ollama with model {self.model}...")

        last_exception: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.num_predict,
                            "top_p": self.top_p,
                        },
                    },
                    timeout=600,  # 10 minutes for local models
                )
                response.raise_for_status()

                result = response.json()
                return result.get("response", "")

            except (requests.RequestException, OSError, TimeoutError) as e:
                last_exception = e
                if attempt < max_retries:
                    delay = base_delay * (2**attempt)
                    logger.warning(
                        f"Ollama request failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Ollama request failed after {max_retries + 1} attempts: {e}")

        raise last_exception or RuntimeError("Ollama request failed")

    def _prepare_summary_sample(
        self, summaries: Sequence[EmailSummary], max_sample: int = 100
    ) -> list[dict[str, Any]]:
        """Prepare summary sample for master AI analysis.

        Args:
            summaries: List of email summaries
            max_sample: Maximum summaries to include

        Returns:
            List of summary data dictionaries
        """
        sample = []
        for summary in list(summaries)[:max_sample]:
            sample.append(summary.to_dict())
        return sample

    def _create_master_analysis_prompt(
        self,
        summary_sample: list[dict[str, Any]],
        existing_folders: dict[str, int] | None = None,
    ) -> str:
        """Create prompt for master AI analysis of email summaries.

        Args:
            summary_sample: Sample of email summaries
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Master analysis prompt
        """
        prompt = f"""I need help creating a smart hierarchical email folder structure based on email patterns.

I have analyzed {len(summary_sample)} emails and extracted key information from each.
"""

        # Add existing folder structure if available
        if existing_folders:
            prompt += f"""
EXISTING FOLDER STRUCTURE:
The user already has {len(existing_folders)} folders set up. Consider this when creating new suggestions:

"""
            for folder_name, count in sorted(
                existing_folders.items(), key=lambda x: x[1], reverse=True
            ):
                prompt += f"- {folder_name} ({count} emails)\n"

            prompt += """
You should:
1. Respect existing folder structure where it makes sense
2. Suggest improvements or consolidations if folders are too specific
3. Create new categories for uncategorized email types
4. Use hierarchical naming (Parent/Child) to organize related folders

"""

        prompt += """
Here's a summary of the emails:

"""
        for i, summary in enumerate(summary_sample, 1):
            prompt += f"""
Email {i}:
- Domain: {summary['sender_domain']}
- Category: {summary['category']}
- Topic: {summary['topic']}
- Keywords: {', '.join(summary['keywords'])}
"""

        prompt += """

Task:
Create a HIERARCHICAL folder structure with smart categorization rules.

HIERARCHICAL FOLDER STRUCTURE GUIDELINES:
- Use slash (/) to separate parent/child folders: "Parent/Child"
- Good examples: "Work/GitHub", "Shopping/Amazon", "Finance/Banking"
- Bad examples: "Work-GitHub", "Shopping_Amazon", "finance-banking"
- Maximum 2-3 levels deep (Parent/Child or Parent/Child/Grandchild)
- Keep folder names short and descriptive (1-3 words)
- Use consistent capitalization (Title Case recommended)

Requirements:
1. Create 3-7 TOP-LEVEL categories (e.g., "Work", "Shopping", "Finance", "Social")
2. Each top-level category SHOULD have SUBCATEGORIES where appropriate (e.g., "Work/GitHub", "Work/Slack")
3. Use GENERAL patterns, NOT brand-specific for categories (but you can use brand domains in patterns)
4. Pattern format:
   - "from:@domain.com" for sender domains (e.g., "from:@github.com", "from:@amazon.de")
   - "from:email@domain.com" for specific senders
   - "subject:keyword" for subject keywords (single keyword)
   - "subject:word1,word2,word3" for multiple keywords (OR logic - matches ANY of these words)
   - "subject:word1 word2" for exact phrase matching
5. Create DETAILED pattern matching rules with multiple conditions where appropriate
6. Include 2-4 example subjects per category to show what emails match

CRITICAL DOMAIN RULES:
- ONLY use REAL domains from the email sample (e.g., github.com, amazon.de, paypal.com)
- NEVER use placeholder domains: example.com, test.com, unsorted.com, random.com, dummy.com
- NEVER use overly generic domains: email.com, mail.com, app.com, security.com, bank.com
- Each "from:@domain" pattern must be an ACTUAL domain you see in the email sample
- If you don't see enough emails from a domain, don't create a pattern for it

Example output:
```json
{
  "categories": [
    {
      "name": "Work",
      "description": "Work-related emails",
      "patterns": [],
      "suggested_folder": "Work",
      "confidence": 0.95,
      "subcategories": [
        {
          "name": "CI/CD",
          "description": "Continuous integration and deployment",
          "patterns": ["from:@github.com", "subject:pipeline,ci,build"],
          "suggested_folder": "Work/CI-CD",
          "confidence": 0.95,
          "example_subjects": ["Pipeline failed", "Build succeeded"]
        },
        {
          "name": "Code Reviews",
          "description": "Pull requests and code reviews",
          "patterns": ["from:@github.com", "subject:pull request,PR"],
          "suggested_folder": "Work/Code-Reviews",
          "confidence": 0.9,
          "example_subjects": ["New PR", "Review requested"]
        }
      ]
    },
    {
      "name": "Shopping",
      "description": "Online shopping and deliveries",
      "patterns": [],
      "suggested_folder": "Shopping",
      "confidence": 0.9,
      "subcategories": [
        {
          "name": "Orders",
          "description": "Order confirmations",
          "patterns": ["subject:order,bestellt,confirmed"],
          "suggested_folder": "Shopping/Orders",
          "confidence": 0.9,
          "example_subjects": ["Order confirmed", "Bestellung"]
        },
        {
          "name": "Shipping",
          "description": "Shipping and delivery updates",
          "patterns": ["subject:shipped,versendet,delivery"],
          "suggested_folder": "Shopping/Shipping",
          "confidence": 0.85,
          "example_subjects": ["Shipped", "Out for delivery"]
        }
      ]
    }
  ]
}
```

IMPORTANT:
- Return ONLY the JSON output
- Do NOT use <think> tags
- Do NOT add explanations
- Use simple ASCII characters only (no special quotes)
- Top-level categories can have empty patterns if all emails go to subcategories
- Subcategories should have specific patterns
- Use folder separators like "Work/CI-CD" for hierarchical structure
"""
        return prompt

    def _create_cluster_analysis_prompt(
        self,
        clusters: Sequence[EmailCluster],
        max_representatives: int = 3,
        existing_folders: dict[str, int] | None = None,
    ) -> str:
        """Create prompt for analyzing email clusters (Embedding mode).

        Args:
            clusters: Email clusters to analyze
            max_representatives: Maximum representative emails per cluster
            existing_folders: Optional dict of existing folder names to email counts

        Returns:
            Prompt string for the LLM
        """
        prompt = f"""I need help creating a smart hierarchical email folder structure based on email clusters.

I have clustered {sum(cluster.size for cluster in clusters)} emails into {len(clusters)} groups of similar emails.
"""

        # Add existing folder structure if available
        if existing_folders:
            prompt += f"""
EXISTING FOLDER STRUCTURE:
The user already has {len(existing_folders)} folders set up. Consider this when creating new suggestions:

"""
            for folder_name, count in sorted(
                existing_folders.items(), key=lambda x: x[1], reverse=True
            ):
                prompt += f"- {folder_name} ({count} emails)\n"

            prompt += """
You should:
1. Respect existing folder structure where it makes sense
2. Suggest improvements or consolidations if folders are too specific
3. Create new categories for uncategorized email types
4. Use hierarchical naming (Parent/Child) to organize related folders

"""

        prompt += """
Here are the representative emails from each cluster:

"""
        for i, cluster in enumerate(clusters, 1):
            prompt += f"""
Cluster {i} ({cluster.size} emails):
"""
            # Get representative emails (up to max_representatives)
            representatives = cluster.representative_emails[:max_representatives]
            for j, email in enumerate(representatives, 1):
                # Extract domain from email sender
                sender_domain = (
                    email.sender.value.split("@")[-1] if "@" in email.sender.value else "unknown"
                )
                prompt += f"""  Email {j}:
  - From: {sender_domain}
  - Subject: {email.subject[:80]}
  - Body snippet: {email.body[:150]}
"""

        prompt += f"""

Task:
Analyze EACH of the {len(clusters)} CLUSTERS individually and create precise Sieve filter rules.

CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE EXACTLY:
1. You MUST analyze ALL {len(clusters)} clusters - do not skip ANY
2. MINIMUM OUTPUT: Create at least {max(10, min(len(clusters), 25))} subcategories
3. Each cluster MUST map to AT LEAST one subcategory (preferably its own)
4. Be GRANULAR and SPECIFIC - create separate subcategories for:
   - Different sender domains (GitHub vs GitLab vs PayPal vs Amazon)
   - Different email types from same sender (Orders vs Shipping vs Returns)
   - Different purposes (Receipts vs Invoices vs Notifications)
5. DO NOT over-consolidate - if 2 clusters have different senders or purposes, create separate subcategories
6. Group related subcategories under parent categories
   (e.g., "Work/GitHub", "Work/GitLab", "Shopping/Amazon-Orders", "Shopping/Amazon-Shipping")

IMPORTANT: If you create fewer than {max(10, min(len(clusters)//2, 25))} subcategories, your response will be REJECTED.

HIERARCHICAL FOLDER STRUCTURE GUIDELINES:
- Use slash (/) to separate parent/child folders: "Parent/Child"
- Good examples: "Work/GitHub-CI", "Shopping/Amazon-Orders", "Finance/PayPal-Receipts"
- Bad examples: "Work-GitHub", "Shopping_Amazon", "finance"
- Maximum 2-3 levels deep (Parent/Child or Parent/Child/Grandchild)
- Keep folder names short and descriptive (1-4 words)
- Use consistent capitalization (Title Case recommended)

SIEVE FILTER PATTERN RULES (use multiple patterns per category):
   - "from:@domain.com" - sender domain (e.g., "from:@github.com")
   - "from:email@domain.com" - exact sender email
   - "subject:keyword" - single keyword in subject
   - "subject:word1,word2,word3" - ANY of the words (OR logic - matches if subject contains word1 OR word2 OR word3)
   - "subject:word1 word2" - exact phrase matching

CRITICAL DOMAIN RULES:
   - ONLY use REAL domains from the cluster emails (e.g., github.com, amazon.de, paypal.com)
   - NEVER use placeholder domains: example.com, test.com, unsorted.com, random.com, dummy.com
   - NEVER use overly generic domains: email.com, mail.com, app.com, security.com, bank.com
   - Each "from:@domain" pattern must be an ACTUAL domain you see in the cluster emails
   - If you don't see a specific domain in the emails, don't create a pattern for it

ADVANCED SIEVE CAPABILITIES:
   - Combine FROM + SUBJECT for precision (e.g., from:@amazon.de AND subject:bestellt,order)
   - Use domain matching for company emails
   - Use multilingual keywords (e.g., "subject:order,bestellung,bestelling,commande")
   - Match notification patterns (e.g., "subject:shipped,versendet,expédié,verzonden")

CATEGORIZATION STRATEGY:
1. Identify email types in each cluster:
   - Transactional: orders, shipping, receipts, invoices, returns
   - Notifications: newsletters, alerts, social media, app notifications
   - Work: meetings, CI/CD, code reviews, deployments, alerts
   - Finance: banking, payments, bills, crypto, transfers
   - Social: invitations, messages, events, friend requests
2. Create specific subcategories for sender+type combinations
3. Include 2-4 example subjects per subcategory
4. Set confidence 0.75-1.0 based on pattern specificity
"""

        prompt += f"""
Example output (notice how SPECIFIC and GRANULAR the subcategories are):
```json
{{
  "categories": [
    {{
      "name": "Work",
      "description": "Work-related emails",
      "patterns": [],
      "suggested_folder": "Work",
      "confidence": 0.95,
      "subcategories": [
        {{
          "name": "GitHub-Actions",
          "description": "GitHub CI/CD pipeline notifications",
          "patterns": ["from:@github.com", "subject:action,workflow,ci"],
          "suggested_folder": "Work/GitHub-Actions",
          "confidence": 0.95,
          "example_subjects": ["Workflow failed", "CI passed"]
        }},
        {{
          "name": "GitHub-PRs",
          "description": "GitHub pull requests",
          "patterns": ["from:@github.com", "subject:pull request,PR,review"],
          "suggested_folder": "Work/GitHub-PRs",
          "confidence": 0.9,
          "example_subjects": ["New PR", "Review requested"]
        }},
        {{
          "name": "GitLab-MR",
          "description": "GitLab merge requests",
          "patterns": ["from:@gitlab.com", "subject:merge request,MR"],
          "suggested_folder": "Work/GitLab-MR",
          "confidence": 0.9,
          "example_subjects": ["Merge request assigned"]
        }}
      ]
    }},
    {{
      "name": "Shopping",
      "description": "Online shopping",
      "patterns": [],
      "suggested_folder": "Shopping",
      "confidence": 0.9,
      "subcategories": [
        {{
          "name": "Amazon-Orders",
          "description": "Amazon order confirmations",
          "patterns": ["from:@amazon.de", "subject:bestellt,order"],
          "suggested_folder": "Shopping/Amazon-Orders",
          "confidence": 0.95,
          "example_subjects": ["Bestellung bestaetigt"]
        }},
        {{
          "name": "Amazon-Shipping",
          "description": "Amazon shipping updates",
          "patterns": ["from:@amazon.de", "subject:versendet,shipped"],
          "suggested_folder": "Shopping/Amazon-Shipping",
          "confidence": 0.9,
          "example_subjects": ["Paket wurde versendet"]
        }},
        {{
          "name": "eBay-Activity",
          "description": "eBay notifications",
          "patterns": ["from:@ebay.de", "subject:gebot,bid,won"],
          "suggested_folder": "Shopping/eBay-Activity",
          "confidence": 0.85,
          "example_subjects": ["You won the auction"]
        }}
      ]
    }},
    {{
      "name": "Finance",
      "description": "Financial transactions",
      "patterns": [],
      "suggested_folder": "Finance",
      "confidence": 0.95,
      "subcategories": [
        {{
          "name": "PayPal-Receipts",
          "description": "PayPal payment receipts",
          "patterns": ["from:@paypal.com", "subject:receipt,zahlung"],
          "suggested_folder": "Finance/PayPal-Receipts",
          "confidence": 0.95,
          "example_subjects": ["Receipt for payment"]
        }},
        {{
          "name": "Stripe-Invoices",
          "description": "Stripe invoices",
          "patterns": ["from:@stripe.com", "subject:invoice,rechnung"],
          "suggested_folder": "Finance/Stripe-Invoices",
          "confidence": 0.9,
          "example_subjects": ["Invoice for subscription"]
        }}
      ]
    }}
  ]
}}
```

NOTICE in the example:
- GitHub is split into "GitHub-Actions" and "GitHub-PRs" (GRANULAR)
- Amazon is split into "Amazon-Orders" and "Amazon-Shipping" (SPECIFIC)
- Each subcategory has a unique sender+purpose combination
- Parent categories group related services, subcategories distinguish types
- Total subcategories in example: 7 (and you should create {max(10, min(len(clusters), 25))})

IMPORTANT:
- Return ONLY the JSON output
- Do NOT use <think> tags
- Do NOT add explanations
- Use simple ASCII characters only (no special quotes)
- Top-level categories can have empty patterns if all emails go to subcategories
- Subcategories should have specific patterns
- Use folder separators like "Work/CI-CD" for hierarchical structure
"""
        return prompt

    def _prepare_email_sample(
        self, emails: Sequence[Email], max_sample: int = 20
    ) -> list[dict[str, str]]:
        """Prepare email sample for AI analysis.

        Args:
            emails: List of emails
            max_sample: Maximum emails to include

        Returns:
            List of email data dictionaries
        """
        sample = []
        for email in list(emails)[:max_sample]:
            sample.append(
                {
                    "from": email.sender.value,
                    "subject": email.subject,
                    "folder": email.folder,
                    "body_preview": email.body[:100] if email.body else "",
                }
            )
        return sample

    def _create_analysis_prompt(self, email_sample: list[dict[str, str]]) -> str:
        """Create prompt for AI analysis.

        Args:
            email_sample: Sample of emails

        Returns:
            Analysis prompt
        """
        prompt = f"""I need help analyzing email patterns to create automatic sorting rules.

Here's a sample of {len(email_sample)} emails:

"""
        for i, email in enumerate(email_sample, 1):
            prompt += f"""
Email {i}:
- From: {email['from']}
- Subject: {email['subject']}
- Current folder: {email['folder']}
- Preview: {email['body_preview']}
"""

        prompt += """

Analyze these emails and group them into broad categories like
"Shopping", "Finance", "Social Media", "Work", or "Newsletters".

Rules:
1. Create GENERAL categories, NOT brand-specific (e.g., "Shopping" not "Amazon Orders")
2. Use this pattern format:
   - "from:@domain.com" for sender domains
   - "subject:keyword" for subject keywords
   - "subject:word1,word2" for multiple keywords

Example output:
```json
{
  "categories": [
    {
      "name": "Shopping",
      "description": "Online store orders and shipping",
      "patterns": ["from:@amazon.de", "subject:order,bestellt"],
      "suggested_folder": "Shopping",
      "confidence": 0.9,
      "example_subjects": ["Order confirmed", "Shipped"]
    }
  ]
}
```

IMPORTANT:
- Return ONLY the JSON output
- Do NOT use <think> tags
- Do NOT add explanations
- Use simple ASCII characters only in example_subjects (no special quotes, no newlines)
- Keep example_subjects short (under 50 characters each)
"""
        return prompt

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse Ollama response into structured data.

        Args:
            response_text: AI response text

        Returns:
            Dictionary with categories

        Raises:
            ValueError: If response cannot be parsed
        """
        if not response_text or not response_text.strip():
            raise ValueError("AI returned empty response")

        logger.debug(f"AI Response (first 500 chars): {response_text[:500]}")

        # Strip out <think>...</think> blocks (chain-of-thought reasoning)
        cleaned_text = re.sub(
            r"<think>.*?</think>", "", response_text, flags=re.DOTALL | re.IGNORECASE
        )

        # Also try to get content after </think> if it exists
        if "<think>" in response_text.lower():
            after_think = re.split(r"</think>", response_text, flags=re.IGNORECASE)
            if len(after_think) > 1:
                cleaned_text = after_think[-1]  # Get everything after last </think>

        # Extract JSON from response
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Save full response for debugging
                debug_file = "/app/logs/failed_ai_response_full.txt"
                try:
                    with open(debug_file, "w") as f:
                        f.write("=== FULL AI RESPONSE (No JSON Found) ===\n\n")
                        f.write(response_text)
                    logger.error(f"Saved full AI response to {debug_file}")
                except (OSError, IOError):
                    pass
                raise ValueError(f"No JSON found in response: {cleaned_text[:200]}")

        # Try to parse JSON with multiple strategies
        result = self._parse_json_with_fixes(json_str)

        if "categories" not in result:
            raise ValueError("Response missing 'categories' field")

        return result

    def _parse_json_with_fixes(self, json_str: str) -> dict[str, Any]:
        """Parse JSON with automatic fixes for common errors.

        Args:
            json_str: JSON string to parse

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Strategy 1: Try direct parsing
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {e}")
            logger.debug(f"Failed JSON (first 1000 chars): {json_str[:1000]}")

        # Strategy 1.5: Replace Unicode quotes
        try:
            # Replace German/fancy quotes with standard ASCII quotes
            fixed_json = json_str.replace("„", "").replace('"', "").replace('"', "")
            fixed_json = fixed_json.replace(""", "'").replace(""", "'")
            result = json.loads(fixed_json)
            logger.info("Successfully parsed JSON after replacing Unicode quotes")
            return result
        except json.JSONDecodeError:
            pass

        # Strategy 2: Fix trailing commas
        try:
            fixed_json = re.sub(r",\s*}", "}", json_str)  # Remove trailing commas before }
            fixed_json = re.sub(r",\s*]", "]", fixed_json)  # Remove trailing commas before ]
            result = json.loads(fixed_json)
            logger.info("Successfully parsed JSON after fixing trailing commas")
            return result
        except json.JSONDecodeError:
            pass

        # Strategy 3: Fix missing commas between array elements
        try:
            fixed_json = re.sub(r"\}\s*\{", "},{", json_str)  # Add comma between objects
            fixed_json = re.sub(r'"\s*"', '","', fixed_json)  # Add comma between strings
            result = json.loads(fixed_json)
            logger.info("Successfully parsed JSON after fixing missing commas")
            return result
        except json.JSONDecodeError:
            pass

        # Strategy 4: Try to extract just the categories array
        try:
            categories_match = re.search(r'"categories"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
            if categories_match:
                categories_str = "[" + categories_match.group(1) + "]"
                # Try to fix and parse categories array
                categories_str = re.sub(r",\s*]", "]", categories_str)
                categories_str = re.sub(r"\}\s*\{", "},{", categories_str)
                categories = json.loads(categories_str)
                logger.info("Successfully extracted and parsed categories array")
                return {"categories": categories}
        except json.JSONDecodeError:
            pass

        # Strategy 5: Save failed response for debugging and raise error
        debug_file = "/app/logs/failed_ai_response.txt"
        try:
            with open(debug_file, "w") as f:
                f.write("=== FAILED AI RESPONSE ===\n\n")
                f.write(json_str)
            logger.error(f"Saved failed AI response to {debug_file}")
        except (OSError, IOError):
            pass

        logger.error(
            f"All JSON parsing strategies failed. JSON (first 1000 chars): {json_str[:1000]}"
        )
        raise ValueError(
            f"Could not parse JSON after trying multiple fixes. Check {debug_file} for details"
        )
