"""Readability metric computation using Coleman-Liau index."""

from readability import ColemanLiauIndex


def readability_cl(text: str) -> int:
    """
    Calculate Coleman–Liau index (integer ≥ 1).
    
    Args:
        text: The text to analyze
        
    Returns:
        Coleman-Liau readability index (integer ≥ 1)
    """
    if not text or not text.strip():
        return 1
    
    # Better text cleaning
    t = text.replace("\\n", " ").replace("\n", " ")
    # Normalize multiple spaces to single space
    t = " ".join(t.split())
    
    try:
        # ColemanLiauIndex requires 3 arguments: letters, words, sentences
        letters = sum(1 for c in t if c.isalpha())
        words = len(t.split())
        sentences = len([s for s in t.split('.') if s.strip()])
        
        if words == 0 or sentences == 0:
            return 1
            
        # ColemanLiauIndex returns a float directly, not an object
        result = ColemanLiauIndex(letters, words, sentences)
        return max(1, int(result))
    except Exception:
        return 1
