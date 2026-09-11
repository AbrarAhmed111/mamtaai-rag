"""
Text Normalization for Intent Detection.
Cleans and standardizes user input without discarding essential semantic details.
"""

import re


def normalize_text(text: str) -> str:
    """
    Standardize text for deterministic rule matching:
    1. Lowercase and strip whitespace.
    2. Normalize redundant whitespace.
    3. Collapse elongated repeated characters (e.g. 'heyyy' -> 'hey', 'sooo' -> 'so').
    4. Strip surrounding punctuation while preserving internal words.
    """
    if not text:
        return ""

    # 1. Lowercase & strip
    cleaned = text.strip().lower()

    # 2. Collapse repeated characters (3 or more identical characters -> 1 or 2)
    # e.g., 'heyyy' -> 'hey', 'helloooo' -> 'hello', 'thanks!!!' -> 'thanks!'
    # Handles characters like 'y', 'o', 'e', '!'
    cleaned = re.sub(r'([a-zA-Z])\1{2,}', r'\1', cleaned)

    # 3. Collapse multiple punctuation marks (e.g. '???' -> '?', '!!!' -> '!')
    cleaned = re.sub(r'([!?.,])\1+', r'\1', cleaned)

    # 4. Collapse multiple whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def strip_punctuation(text: str) -> str:
    """
    Remove leading and trailing punctuation for exact short phrase checks.
    e.g., 'thanks!' -> 'thanks', 'hello...' -> 'hello'
    """
    return re.sub(r'^[^\w\s]+|[^\w\s]+$', '', text).strip()
