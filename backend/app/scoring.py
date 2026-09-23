"""Content-based scoring engine.

Each factor produces a score between 0.0 and 1.0 plus a short note about
why. The final score is a weighted average of those factors, converted to
0-100 for humans.

Weights: think of them as "how important is this factor, out of 100%".
If semantic matching is unavailable we renormalize over the factors that
remain so the total still sums to 100.
"""
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

WEIGHTS: dict[str, float] = {
    "skills": 0.30,    # 30%
    "category": 0.25,  # 25%
    "proximity": 0.20, # 20%
    "time": 0.15,      # 15%
    "semantic": 0.10,  # 10%
}

NEUTRAL = 0.6  # score used when a factor just doesn't apply


def haversine_miles(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Straight-line distance between two lat/lon points, in miles."""
    r_lat1, r_lat2 = radians(lat1), radians(lat2)
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(r_lat1) * cos(r_lat2) * sin(d_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    R = 3958.8  # Earth radius in miles
    return R * c


# ---------------------------------------------------------------------------
# Individual factors
# ---------------------------------------------------------------------------

def skills_score(
    student_skills: set[str],
    required_skills: list[str],
    helpful_skills: list[str],
) -> tuple[float, str]:
    """How well the student's skills cover what the role needs.

    Required skills count double (they're the deal-breakers). The note lists
    which skills were matched and which required ones are missing.
    """
    req = [s for s in required_skills if s]
    help_ = [s for s in helpful_skills if s]
    if not req and not help_:
        return NEUTRAL, "No specific skills required."

    matched_req = [s for s in req if s in student_skills]
    matched_help = [s for s in help_ if s in student_skills]
    missing_req = [s for s in req if s not in student_skills]

    numerator = 2 * len(matched_req) + len(matched_help)
    denominator = 2 * len(req) + len(help_)
    score = numerator / denominator if denominator else NEUTRAL

    parts: list[str] = []
    if matched_req:
        parts.append("matched required: " + ", ".join(matched_req))
    if matched_help:
        parts.append("matched helpful: " + ", ".join(matched_help))
    parts.append(
        "missing required: " + (", ".join(missing_req) if missing_req else "none")
    )
    return score, "; ".join(parts)


def category_score(
    student_interests: set[str], category: str, tags: list[str]
) -> tuple[float, str]:
    """Overlap between the student's interest tags and the opportunity's
    category + tags."""
    opp_set = {category} | {t for t in tags if t}
    if not opp_set:
        return NEUTRAL, "No interest tags on this opportunity."

    matched = student_interests & opp_set
    score = len(matched) / len(opp_set)
    note = (
        "matched interests: " + (", ".join(sorted(matched)) if matched else "none")
    )
    return score, note


def proximity_score(dist_miles: float) -> tuple[float, str]:
    """Closer is better, using friendly distance bands."""
    if dist_miles <= 2:
        score = 1.0
    elif dist_miles <= 10:
        score = 0.85
    elif dist_miles <= 25:
        score = 0.65
    elif dist_miles <= 50:
        score = 0.45
    elif dist_miles <= 100:
        score = 0.25
    else:
        score = 0.1
    return score, f"{dist_miles:.1f} mi away"


def time_score(
    max_hours: int, hours_min: int, hours_max: int
) -> tuple[float, str]:
    """Can this opportunity fit in the student's weekly availability?"""
    if hours_min == 0 and hours_max == 0:
        return NEUTRAL, "Flexible hours."
    if max_hours >= hours_max:
        score = 1.0
        verdict = f"can cover up to {hours_max}h/wk"
    elif max_hours >= hours_min:
        span = max(hours_max - hours_min, 1)
        score = 0.6 + 0.4 * ((max_hours - hours_min) / span)
        verdict = f"can cover {max_hours}h of a {hours_min}-{hours_max}h shift"
    else:
        score = max(max_hours / hours_min, 0.0) * 0.6
        verdict = f"below {hours_min}h/wk minimum"
    return score, f"needs {hours_min}-{hours_max}h/wk; {verdict}"


# ---------------------------------------------------------------------------
# Final combination
# ---------------------------------------------------------------------------

@dataclass
class FactorResult:
    name: str
    score01: float
    weight: float
    note: str


def combine(
    factors: list[FactorResult], force_weights: bool = False
) -> tuple[float, list[dict]]:
    """Weighted-average the factors into a single 0-100 score.

    Also returns the human-readable breakdown. If a factor should be skipped
    (e.g. no semantic engine), just don't include it in `factors` — its
    weight is redistributed automatically.
    """
    total_weight = sum(f.weight for f in factors)
    if total_weight <= 0:
        return 0.0, []

    score01 = (
        sum(f.score01 * f.weight for f in factors) / total_weight if not force_weights
        else sum(f.score01 * f.weight for f in factors) / sum(W.values())
    )

    breakdown = []
    for f in factors:
        effective_weight = f.weight / total_weight
        breakdown.append(
            {
                "name": f.name,
                "weight": round(effective_weight * 100, 1),
                "score": round(f.score01 * 100),
                "note": f.note,
            }
        )
    return score01, breakdown


def build_reasons(factors: list[FactorResult], threshold: float = 0.75) -> list[str]:
    """Short one-liners that explain *why* this match was recommended."""
    reasons = []
    for f in factors:
        if f.score01 >= threshold:
            names = {"skills": "their skills", "category": "their interests",
                     "proximity": "the location", "time": "their schedule",
                     "semantic": "natural-language fit"}
            reasons.append(
                f"Strong fit on {names.get(f.name, f.name)} ({f.score01*100:.0f}%)."
            )
    return reasons