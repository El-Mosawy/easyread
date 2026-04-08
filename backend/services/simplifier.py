import re
from typing import List, Tuple, Dict 

# Common “official” phrases -> simpler equivalents (I think these are the most common phrases mentioned in UK letters)
PHRASE_REPLACEMENTS: List[Tuple[str, str]] = [
    # Very common “official letter” openers
    (r"\bplease be advised that\b", "please note"),
    (r"\bwe regret to inform you that\b", "we’re sorry, but"),
    (r"\bwe regret to inform you\b", "we’re sorry, but"),

    # Common legal/official patterns
    (r"\bin accordance with\b", "under"),
    (r"\bfor the avoidance of doubt\b", "to be clear"),
    (r"\bwith regard to\b", "about"),
    (r"\bin relation to\b", "about"),
    (r"\bin the event that\b", "if"),
    (r"\bprior to\b", "before"),
    (r"\bsubsequent to\b", "after"),
    (r"\bwith immediate effect\b", "from now"),

    # “You must” patterns
    (r"\byou are required to\b", "you must"),
    (r"\bit is your responsibility to\b", "you must"),
    (r"\byou are requested to\b", "please"),
    (r"\byou are advised to\b", "you should"),

    # Consequences
    (r"\bfailure to comply may result in\b", "if you don’t do this, there may be"),
    (r"\bfailure to comply will result in\b", "if you don’t do this, there will be"),

    # Fluffy closings
    (r"\bplease do not hesitate to contact us\b", "you can contact us"),
    (r"\bat your earliest convenience\b", "as soon as you can"),

    # Verbs
    (r"\bassist\b", "help"),
    (r"\butili[sz]e\b", "use"),
    (r"\bcommence\b", "start"),
    (r"\bterminate\b", "end"),
    (r"\badditional\b", "extra"),
]

# Common words -> simpler equivalents (also based on UK letters, but more general than phrases)
WORD_REPLACEMENTS: Dict[str, str] = {
    "approximately": "about",
    "sufficient": "enough",
    "purchase": "buy",
    "request": "ask",
    "require": "need",
    "additional": "extra",
    "respond": "reply",
    "provide": "give",
    "commence": "start",
    "terminate": "end",
    "assist": "help",
    "utilise": "use",
    "endeavour": "try",
    "facilitate": "help",
    "implement": "carry out", 
    "subsequent": "later",
    "prior": "before",
    "within": "in",
    "pursuant": "under",
    "policy": "rules", 
}

# The code below cleans whitespace so text is consistent, replaces common phrases, replaces complex words, splits long sentences, and if it looks like a list, it converts
# it into bullet points

# Makes the whitespace consistent so later logic behaves predicatbly
def _normalise_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ newlines into 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

# Shortens long sentences. If a sentence is too long, we first try to split on sentence-ending punctuation. If it's still too long, we split on commas/semicolons. 
# This isn't perfect but it should help a lot with readability.
def _split_long_sentences(text: str, max_len: int) -> str:
    # Split on sentence-ending punctuation, keep it.
    parts = re.split(r"([.!?])", text)
    if len(parts) == 1:
        return text

    out: List[str] = []
    buf = ""

    for i in range(0, len(parts), 2):
        sentence = parts[i].strip()
        punct = parts[i + 1] if i + 1 < len(parts) else ""
        if not sentence and not punct:
            continue

        candidate = (sentence + punct).strip()
        if not candidate:
            continue

        if len(candidate) <= max_len:
            out.append(candidate)
        else:
            # If too long, split on commas/semicolons
            subparts = re.split(r"[,;]\s+", candidate)
            for sp in subparts:
                sp = sp.strip()
                if sp:
                    out.append(sp if sp.endswith((".", "!", "?")) else sp + ".")
    return " ".join(out)

# Replace common phrases first, then words, to avoid conflicts (e.g. "utilise" -> "use", but we don't want "as per" -> "as" before we replace "per" -> "for")
def _replace_phrases(text: str) -> str:
    out = text
    for pattern, replacement in PHRASE_REPLACEMENTS:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    return out

# Replaces words while preserving punctuation around them, and also preserving capitalization (e.g. "Utilise" -> "Use")
def _replace_words(text: str) -> str:
    # Replace words while preserving punctuation around them.
    def repl(match: re.Match) -> str:
        word = match.group(0)
        lower = word.lower()
        if lower in WORD_REPLACEMENTS:
            new = WORD_REPLACEMENTS[lower]
            # Preserve capitalization if original word started with uppercase
            if word[0].isupper():
                new = new.capitalize()
            return new
        return word

    return re.sub(r"[A-Za-z']+", repl, text)

# Converts obvious lists into bullet points. If a line starts with a number + dot/paren or a dash/bullet, we convert it to a bullet point. 
# This is a bit hacky but it should help with readability for obvious lists.
def _bulletise_if_listy(text: str) -> str:
    """
    If the text contains obvious list markers, convert to bullets.
    """
    lines = [ln.strip() for ln in text.split("\n")]
    has_list = any(re.match(r"^(\d+[\).]|[-•])\s+", ln) for ln in lines)
    if not has_list:
        return text

    bullets = []
    for ln in lines:
        m = re.match(r"^(\d+[\).]|[-•])\s+(.*)$", ln)
        if m:
            bullets.append(f"- {m.group(2).strip()}")
        elif ln:
            bullets.append(ln)
    return "\n".join(bullets)

# Helper function to capitalise the first letter of sentences, and after newlines. This is a bit of polish to improve readability after the other transformations.
def _sentence_case(text: str) -> str:
    """
    Capitalise the first letter of the text and the first letter after . ! ? and after newlines.
    Keeps everything else as-is.
    """
    s = text.strip()
    if not s:
        return s

    # Capitalise first alphabetic character in the string
    s = re.sub(r"^(\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)

    # Capitalise after sentence endings and newlines
    s = re.sub(
        r"([.!?]\s+)([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        s,
    )
    s = re.sub(
        r"(\n\s*)([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        s,
    )

    # Clean up: remove spaces before punctuation
    s = re.sub(r"\s+([,.!?])", r"\1", s)
    return s

def _very_simple_format(text: str) -> str:
    """
    Make the output easier to scan:
    - break into short lines
    - add bullets when its a paragraph
    """
    # Split into sentences-ish chunks (already mostly split)
    chunks = [c.strip() for c in re.split(r"(?<=[.!?])\s+", text) if c.strip()]
    if len(chunks) <= 1:
        return text

    # Convert to bullets
    lines = [f"- {c}" for c in chunks]
    return "\n".join(lines)

# Main function that calls the helper functions. Chooses aggressiveness based on level. Returns simplified text and metadata (lengths, level)
# The metadata can be used to show stats to the user, or for debugging/improving the simplifier later.
def simplify_text(text: str, level: str = "simple") -> Dict[str, object]:
    """
    Returns simplified text + small metadata.
    """
    original = text or ""
    cleaned = _normalise_whitespace(original)

    if not cleaned:
        return {"simplified": "", "meta": {"level": level, "empty": True}}

    # Very simple = more aggressive splitting
    max_sentence_len = 140 if level == "simple" else 90

    out = cleaned
    out = _replace_phrases(out)
    out = _replace_words(out)
    out = _split_long_sentences(out, max_len=max_sentence_len)
    out = _bulletise_if_listy(out)
    out = _sentence_case(out)

    if level == "very_simple":
        out = _very_simple_format(out)

    meta = {
        "level": level,
        "original_length": len(original),
        "simplified_length": len(out),
    }
    return {"simplified": out, "meta": meta}

