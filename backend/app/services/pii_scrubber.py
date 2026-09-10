"""
pii_scrubber.py — PII Redaction Engine for PsyPredict

Scrubs personally identifiable information from text BEFORE
sending to cloud LLM (Groq). Uses regex-based pattern matching
for common PII types:
  - Email addresses
  - Phone numbers (Indian + international)
  - SSN / Aadhaar numbers
  - Credit card numbers
  - IP addresses
  - Names (simple heuristic: capitalized word sequences after common prefixes)

Design:
  - Reversible: stores a token→original mapping so cloud LLM responses
    can be de-redacted if needed.
  - Configurable: can enable/disable individual scrubbers.
  - Fast: pure regex, no ML models or external dependencies.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PII Patterns
# ---------------------------------------------------------------------------

_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    # Email addresses
    (
        "EMAIL",
        re.compile(
            r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
        ),
        "[EMAIL_REDACTED]",
    ),
    # Phone numbers — Indian (10-digit, optional +91/0 prefix)
    (
        "PHONE_IN",
        re.compile(
            r"(?<!\d)(?:\+91[\s\-]?|0)?[6-9]\d{4}[\s\-]?\d{5}(?!\d)"
        ),
        "[PHONE_REDACTED]",
    ),
    # Phone numbers — International (generic: + followed by 7-15 digits)
    (
        "PHONE_INTL",
        re.compile(
            r"(?<!\d)\+\d{1,3}[\s\-]?\d{4,14}(?!\d)"
        ),
        "[PHONE_REDACTED]",
    ),
    # Aadhaar number (12 digits, often spaced as 4-4-4)
    (
        "AADHAAR",
        re.compile(
            r"(?<!\d)\d{4}[\s\-]?\d{4}[\s\-]?\d{4}(?!\d)"
        ),
        "[AADHAAR_REDACTED]",
    ),
    # SSN (US format: XXX-XX-XXXX)
    (
        "SSN",
        re.compile(
            r"(?<!\d)\d{3}[\-]\d{2}[\-]\d{4}(?!\d)"
        ),
        "[SSN_REDACTED]",
    ),
    # Credit card numbers (13-19 digits, optionally spaced/dashed in groups of 4)
    (
        "CC",
        re.compile(
            r"(?<!\d)\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{1,7}(?!\d)"
        ),
        "[CC_REDACTED]",
    ),
    # IP addresses (IPv4)
    (
        "IP",
        re.compile(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        ),
        "[IP_REDACTED]",
    ),
]

# Name detection heuristic: "my name is X Y", "I am X Y", "I'm X"
_NAME_PATTERNS: List[re.Pattern] = [
    re.compile(
        r"(?:my\s+name\s+is|call\s+me|this\s+is)\s+"
        r"([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:I\s+am|I\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})",
    ),
    re.compile(
        r"(?:name|patient|user)[:\s]+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# Scrubber Result
# ---------------------------------------------------------------------------

@dataclass
class ScrubResult:
    """Result of PII scrubbing operation."""
    scrubbed_text: str
    pii_found: bool
    pii_count: int
    pii_types: List[str]
    token_map: Dict[str, str] = field(default_factory=dict)
    # token_map: { "[PII_abc123]" -> "original_value" } for de-redaction


class PIIScrubber:
    """
    Scrubs PII from text before cloud LLM calls.

    Usage:
        scrubber = PIIScrubber()
        result = scrubber.scrub("My email is john@example.com")
        # result.scrubbed_text == "My email is [EMAIL_REDACTED]"
        # result.pii_found == True
    """

    def __init__(
        self,
        reversible: bool = False,
        detect_names: bool = True,
    ) -> None:
        """
        Args:
            reversible: If True, use unique tokens so redaction can be reversed.
            detect_names: If True, use heuristic name detection patterns.
        """
        self.reversible = reversible
        self.detect_names = detect_names

    def scrub(self, text: str) -> ScrubResult:
        """
        Scrub all PII from the given text.

        Returns a ScrubResult with the cleaned text and metadata.
        """
        if not text or not text.strip():
            return ScrubResult(
                scrubbed_text=text,
                pii_found=False,
                pii_count=0,
                pii_types=[],
            )

        result_text = text
        token_map: Dict[str, str] = {}
        pii_types: List[str] = []
        pii_count = 0

        # Apply regex patterns
        for pii_type, pattern, replacement in _PATTERNS:
            matches = list(pattern.finditer(result_text))
            if not matches:
                continue

            pii_types.append(pii_type)
            # Process matches in reverse order to preserve indices
            for match in reversed(matches):
                original = match.group()
                if self.reversible:
                    token = f"[PII_{pii_type}_{uuid.uuid4().hex[:8]}]"
                    token_map[token] = original
                    result_text = (
                        result_text[: match.start()]
                        + token
                        + result_text[match.end() :]
                    )
                else:
                    result_text = (
                        result_text[: match.start()]
                        + replacement
                        + result_text[match.end() :]
                    )
                pii_count += 1

        # Name detection (heuristic)
        if self.detect_names:
            for pattern in _NAME_PATTERNS:
                matches = list(pattern.finditer(result_text))
                for match in reversed(matches):
                    name = match.group(1)
                    # Skip if it's already been redacted
                    if "[" in name and "REDACTED" in name:
                        continue
                    # Skip common false positives
                    if name.lower() in _FALSE_POSITIVE_NAMES:
                        continue

                    if self.reversible:
                        token = f"[PII_NAME_{uuid.uuid4().hex[:8]}]"
                        token_map[token] = name
                        result_text = result_text.replace(name, token, 1)
                    else:
                        result_text = result_text.replace(
                            name, "[NAME_REDACTED]", 1
                        )
                    pii_count += 1
                    if "NAME" not in pii_types:
                        pii_types.append("NAME")

        if pii_count > 0:
            logger.info(
                "PII scrubbed: %d item(s) of types %s",
                pii_count,
                pii_types,
            )

        return ScrubResult(
            scrubbed_text=result_text,
            pii_found=pii_count > 0,
            pii_count=pii_count,
            pii_types=pii_types,
            token_map=token_map,
        )

    def unscrub(self, text: str, token_map: Dict[str, str]) -> str:
        """
        Reverse the scrubbing operation using the token map.
        Only works if reversible=True was used during scrubbing.
        """
        result = text
        for token, original in token_map.items():
            result = result.replace(token, original)
        return result

    def has_pii(self, text: str) -> bool:
        """Quick check: does the text contain any detectable PII?"""
        for _, pattern, _ in _PATTERNS:
            if pattern.search(text):
                return True
        if self.detect_names:
            for pattern in _NAME_PATTERNS:
                match = pattern.search(text)
                if match and match.group(1).lower() not in _FALSE_POSITIVE_NAMES:
                    return True
        return False


# Common words that look like names but aren't
_FALSE_POSITIVE_NAMES = {
    "depression", "anxiety", "stress", "fear", "anger",
    "happy", "sad", "worried", "scared", "confused",
    "feeling", "stressed", "exhausted", "overwhelmed", "tired",
    "struggling", "hurting", "lost", "broken", "trying",
    "hopeless", "alone", "afraid", "numb", "empty", "guilty",
    "ashamed", "worthless", "helpless", "restless", "nervous",
    "panicking", "fine", "good", "bad", "sick", "done", "here",
    "not", "just", "so", "really", "very", "anxious", "depressed",
    "doctor", "therapist", "counselor", "psychologist",
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "january", "february", "march",
    "april", "may", "june", "july", "august", "september",
    "october", "november", "december",
    "gita", "krishna", "arjuna", "bhagavad",
    "india", "american", "english",
    "psypredict", "hello", "thanks", "okay",
}


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

pii_scrubber = PIIScrubber(reversible=False, detect_names=True)
"""Default scrubber instance (non-reversible, with name detection)."""
