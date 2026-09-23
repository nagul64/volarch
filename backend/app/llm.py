"""Google Gemini integration: turns a free-text search into a student profile.

Requires the `google-genai` package and a Google AI Studio key:

    $env:GEMINI_API_KEY = "AIza..."
    Get a free key at https://aistudio.google.com

The engine reuses the exact same weighted scoring as the seeded students —
search just swaps in a "synthetic profile" that Gemini extracts from the
user's words.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

# The student model can only pick from THIS vocabulary, so the extracted
# profile matches the seed data and scoring works. Add new ones here (and
# to seed.py) if you invent new student skills or interest tags.
ALLOWED_SKILLS = [
    "dog-handling", "social-media", "fundraising", "python", "web-dev",
    "tutoring", "coding", "data-analysis", "cooking", "tamil",
    "event-planning", "communication", "photography", "writing",
    "gardening", "art", "first-aid", "organization", "nursing",
    "graphic-design", "public-speaking", "website", "english", "math",
    "computer-basics", "teamwork",
]

ALLOWED_INTERESTS = [
    "animals", "environment", "arts", "technology", "education",
    "food", "community", "health", "elderly-care",
]

# A handful of Coimbatore pincodes -> (lat, lng) so distance scoring works
# when the user supplies a pincode. A real app would call a geocoding API
# (e.g. Google Maps Geocoding) instead of this hard-coded lookup.
PINCODE_LOOKUP: dict[str, tuple[float, float]] = {
    "641001": (10.9926, 76.9570),  # Ukkadam
    "641002": (10.9989, 76.9654),  # RS Puram
    "641004": (11.0201, 77.0116),  # Peelamedu
    "641005": (11.0058, 77.0145),  # Singanallur
    "641006": (11.0217, 76.9868),  # Ganapathy
    "641011": (11.0195, 76.9727),  # Saibaba Colony
    "641012": (11.0168, 76.9558),  # Gandhipuram
    "641023": (10.9691, 76.9940),  # Podanur
    "641034": (11.0825, 76.9580),  # Thudiyalur
    "641035": (11.0574, 77.0187),  # Saravanampatti
    "641037": (11.0645, 76.9080),  # PN Palayam
    "641041": (10.9925, 76.8982),  # Vadavalli
    "641042": (11.0180, 76.9971),  # Kovaipudur
    "641045": (10.9873, 76.9908),  # Ramanathapuram
    "641402": (11.0333, 77.1272),  # Sulur
}

_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class LlmError(Exception):
    """Raised when the Gemini step cannot run (missing key, bad key, quota)."""


def _client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise LlmError(
            "GEMINI_API_KEY is not set. In PowerShell run:\n"
            '    $env:GEMINI_API_KEY = "AIza..."\n'
            "Get a free key at https://aistudio.google.com — then restart "
            "the backend."
        )
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - guard against missing install
        raise LlmError(
            "The `google-genai` package is missing. Run:\n"
            "    .\\.venv\\Scripts\\pip install google-genai"
        ) from exc
    return genai.Client(api_key=key)


def _clean_pincode(raw: Any, zip_hint: str | None) -> str:
    candidates = []
    if isinstance(raw, str):
        candidates.append(raw)
    if zip_hint:
        candidates.append(zip_hint)
    for c in candidates:
        m = re.search(r"\b\d{6}\b", c)
        if m:
            return m.group(0)
    return ""


def _coords_for(pincode: str) -> tuple[float | None, float | None]:
    if pincode in PINCODE_LOOKUP:
        lat, lng = PINCODE_LOOKUP[pincode]
        return lat, lng
    return None, None


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                pass
    return {}


def _pick(value: Any, allowed: list[str]) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item) in allowed]
    return []


def _build_profile(
    data: dict[str, Any], message: str, zip_hint: str | None
) -> dict[str, Any]:
    """Turn a parsed key/value blob into the profile shape the recommender wants."""
    pincode = _clean_pincode(data.get("zip_code"), zip_hint)
    lat, lng = _coords_for(pincode)

    hours = data.get("max_hours_per_week", 4)
    try:
        hours = int(hours)
    except (TypeError, ValueError):
        hours = 4
    hours = max(1, min(40, hours))

    return {
        "skills": _pick(data.get("skills"), ALLOWED_SKILLS),
        "interests": _pick(data.get("interests"), ALLOWED_INTERESTS),
        "max_hours_per_week": hours,
        "zip_code": pincode,
        "bio": str(data.get("bio") or message)[:500],
        "latitude": lat,
        "longitude": lng,
    }


def extract_profile(query: str, zip_hint: str | None = None) -> dict[str, Any]:
    """Ask Gemini to distill a free-text message into a structured profile."""
    message = (query or "").strip()
    if not message:
        raise LlmError("Please describe what you'd like to do.")

    client = _client()
    prompt = f"""You are the extraction step of an AI volunteer-matching engine
in Coimbatore, Tamil Nadu. Read the student's message and answer with ONLY a
single JSON object and nothing else.

Rules:
- "skills": a JSON array of strings, choosing ONLY from this allowed list:
  {", ".join(sorted(ALLOWED_SKILLS))}
- "interests": a JSON array of strings, choosing ONLY from this allowed list:
  {", ".join(sorted(ALLOWED_INTERESTS))}
- "max_hours_per_week": integer hours per week the student can volunteer
  (use 4 if unknown, keep between 1 and 40)
- "zip_code": the 6-digit Coimbatore pincode if the message mentions one,
  else ""
- "bio": one short first-person sentence restating what the student said

Student message: "{message}"
"""

    try:
        resp = client.models.generate_content(model=_DEFAULT_MODEL, contents=prompt)
    except Exception as exc:
        raise LlmError(f"Gemini request failed ({type(exc).__name__}): {exc}") from exc

    data = _parse_json(resp.text or "")
    return _build_profile(data, message, zip_hint)


def _tokens_in(message: str, allowed: list[str]) -> list[str]:
    """Rule-based scan: which allowed words appear in the message?

    Uses word boundaries so "art" doesn't match "cart" and "data-analysis"
    still matches as a single unit. This is the no-key fallback — Gemini does
    the smart version.
    """
    hits: list[str] = []
    for tag in allowed:
        if re.search(rf"\b{re.escape(tag)}\b", message, re.IGNORECASE):
            hits.append(tag)
    return hits


def local_extract(query: str, zip_hint: str | None = None) -> dict[str, Any]:
    """Fallback extractor that needs no API key.

    Keyword-scans the message against the allowed vocabulary, pulls the first
    6-digit pincode, and defaults availability to 4 h/wk. Keeps search working
    (with TF-IDF / local semantic matching) when no Gemini key is configured.
    """
    message = (query or "").strip()
    if not message:
        raise LlmError("Please describe what you'd like to do.")

    pincode = _clean_pincode(message, zip_hint)
    lat, lng = _coords_for(pincode)

    return {
        "skills": _tokens_in(message, ALLOWED_SKILLS),
        "interests": _tokens_in(message, ALLOWED_INTERESTS),
        "max_hours_per_week": 4,
        "zip_code": pincode,
        "bio": message[:500],
        "latitude": lat,
        "longitude": lng,
    }


def extract(query: str, zip_hint: str | None = None) -> tuple[dict[str, Any], str]:
    """Best-effort profile extraction.

    Tries Gemini first (returns "gemini"); falls back to the built-in
    keyword scanner (returns "local-keyword") when there's no key, a bad key,
    or a quota failure. The engine name lets the UI show which mode is active.
    """
    try:
        return extract_profile(query, zip_hint), "gemini"
    except LlmError:
        return local_extract(query, zip_hint), "local-keyword"