"""Swear word ratio computation."""

import os
import re
import string
from typing import List


def load_list(path: str) -> List[str]:
    """Load a text file (1 element/line) and return a list in lowercase."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip().lower() for ln in f if ln.strip()]


def _prep_text(text: str) -> str:
    """Clean text: lowercase, replace \n, remove punctuation (replaced with spaces)."""
    t = (text or "").lower().replace("\\n", " ")
    return t.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))


def swear_ratio(text: str, swear_words: List[str]) -> float:
    """
    Calculate swear word ratio: exact occurrences / total number of tokens.
    
    Args:
        text: The text to analyze
        swear_words: List of swear words to search for
        
    Returns:
        Ratio of swear word occurrences to total tokens
    """
    t = _prep_text(text)
    toks = [w for w in t.split() if w]
    if not toks:
        return 0.0
    total = 0
    for w in swear_words:
        total += len(list(re.finditer(rf"\b{re.escape(w)}\b", t)))
    return total / len(toks)
