"""Helpers for NammaSeve's "Ask the Notice" chat.

* detect_question_language: decides the answer language from the QUESTION text only
  (never from the notice or the answer), using Unicode scripts.
* finalize_answer: keeps the cited source sentence an exact, verified copy of the
  original notice text, so a translated answer can never replace or alter it.
"""
import difflib
import html
import re

# Languages the app supports (the values match LANGUAGES in app.py).
NOT_STATED = {
    "English": "This is not clearly stated in the notice.",
    "Hindi": "यह जानकारी सूचना में स्पष्ट रूप से नहीं दी गई है।",
    "Telugu": "ఈ సమాచారం నోటీసులో స్పష్టంగా పేర్కొనబడలేదు.",
    "Kannada": "ಈ ಮಾಹಿತಿಯನ್ನು ನೋಟಿಸ್‌ನಲ್ಲಿ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಲಾಗಿಲ್ಲ.",
}
NO_SOURCE = {
    "English": "No supporting sentence found in the notice.",
    "Hindi": "सूचना में कोई समर्थन करने वाला वाक्य नहीं मिला।",
    "Telugu": "నోటీసులో మద్దతు ఇచ్చే వాక్యం కనుగొనబడలేదు.",
    "Kannada": "ನೋಟಿಸ್‌ನಲ್ಲಿ ಬೆಂಬಲಿಸುವ ವಾಕ್ಯ ಕಂಡುಬಂದಿಲ್ಲ.",
}

SOURCE_MARKER = "SUPPORTING KANNADA SENTENCE:"


def detect_question_language(text: str, fallback: str = "English") -> str:
    """Return Telugu, Kannada, Hindi or English based on the script of ``text``.

    Devanagari is treated as Hindi. Romanised input (e.g. Telugu typed in English
    letters) cannot be told apart from English by script and is treated as English.
    If the text has no letters at all, ``fallback`` is returned.
    """
    counts = {"Telugu": 0, "Kannada": 0, "Hindi": 0}
    latin = 0
    for ch in text or "":
        o = ord(ch)
        if 0x0C00 <= o <= 0x0C7F:
            counts["Telugu"] += 1
        elif 0x0C80 <= o <= 0x0CFF:
            counts["Kannada"] += 1
        elif 0x0900 <= o <= 0x097F:
            counts["Hindi"] += 1
        elif ch.isascii() and ch.isalpha():
            latin += 1
    best = max(counts, key=counts.get)
    if counts[best] == 0 and latin == 0:
        return fallback
    # A few English words (GST, PDF, a date) inside an Indic-script question must not flip it.
    if counts[best] > 0 and counts[best] * 2 >= latin:
        return best
    return "English"


def _norm(s: str) -> str:
    return " ".join(s.split())


def _clean_line(s: str) -> str:
    s = re.sub(r"^\s*(?:\d+[.)]|[-•*>])\s*", "", s)
    return s.strip().strip("\"'“”‘’*`").strip()


def _sentences(text: str):
    parts = re.split(r"(?<=[.!?।])\s+|\n+", text)
    return [_norm(p) for p in parts if len(_norm(p)) > 3]


def verify_source(source_part: str, notice_text: str, language: str) -> str:
    """Return HTML for the citation box containing only text that really exists in the notice."""
    notice_norm = _norm(notice_text)
    candidates = _sentences(notice_text)

    whole = _clean_line(_norm(source_part))
    if len(whole) > 3 and whole in notice_norm:
        return html.escape(whole)

    kept = []
    for raw in source_part.splitlines():
        line = _norm(_clean_line(raw))
        if len(line) <= 3:
            continue
        if line in notice_norm:
            found = line
        else:
            match = difflib.get_close_matches(line, candidates, n=1, cutoff=0.85)
            found = match[0] if match else None
        if found and found not in kept:
            kept.append(found)
    if not kept:
        return html.escape(NO_SOURCE.get(language, NO_SOURCE["English"]))
    return "<br>".join(html.escape(k) for k in kept)


def finalize_answer(raw: str, notice_text: str, language: str) -> str:
    """Rebuild the model output in the app's existing 'ANSWER: … / SUPPORTING KANNADA SENTENCE: …' format."""
    if SOURCE_MARKER in raw:
        answer_part, source_part = raw.split(SOURCE_MARKER, 1)
    else:
        answer_part, source_part = raw, ""
    answer_part = re.sub(r"^\s*ANSWER:\s*", "", answer_part.strip()).strip()
    if not answer_part:
        answer_part = NOT_STATED.get(language, NOT_STATED["English"])
    return f"ANSWER: {answer_part}\n{SOURCE_MARKER} {verify_source(source_part, notice_text, language)}"


def answer_only(stored_answer: str) -> str:
    """The answer text without the citation, with markdown symbols removed (used for speech)."""
    part = stored_answer.split(SOURCE_MARKER, 1)[0].replace("ANSWER:", "", 1)
    return re.sub(r"[*#`_>]", "", part).strip()
