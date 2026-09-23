"""Hybrid recommender: content-based scoring + semantic text matching.

For a given student we score every opportunity, then hand back the best
ones ranked by total score, with a per-factor breakdown so the *why* is
visible — not a black box.
"""
import sqlite3

from . import db, scoring, semantic

# +30 is the strongest engine; anything forced off (None) means "skip".
SEMANTIC_WEIGHT = scoring.WEIGHTS["semantic"]


def _load_student(conn: sqlite3.Connection, student_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    return db.to_dict(row) if row else None


def _load_opportunities(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM opportunities").fetchall()
    return [db.to_dict(r) for r in rows]


def _semantic_text_student(student: dict) -> str:
    bits = [student.get("bio", "")] + list(student.get("interests", [])) + list(student.get("skills", []))
    return " ".join(str(b) for b in bits if b)


def _semantic_text_opp(opp: dict) -> str:
    bits = [opp.get("description", ""), opp.get("category", "")] + list(opp.get("tags", []))
    return " ".join(str(b) for b in bits if b)


def _semantic_factor(
    student: dict, opp: dict, scorer
) -> scoring.FactorResult | None:
    """Semantic match of the student's profile vs the opportunity description."""
    try:
        sim = scorer.similarity(
            _semantic_text_student(student), _semantic_text_opp(opp)
        )
    except Exception:
        return None
    note = f"profile vs description similarity {sim * 100:.0f}%"
    return scoring.FactorResult("semantic", sim, SEMANTIC_WEIGHT, note)


def recommend_for_student(
    conn: sqlite3.Connection, student_id: int, limit: int = 10
) -> list[dict]:
    student = _load_student(conn, student_id)
    if student is None:
        raise ValueError(f"Student {student_id} not found")
    return recommend(conn, student, limit=limit)


def recommend(
    conn: sqlite3.Connection, profile: dict, limit: int = 10
) -> list[dict]:
    """Score every opportunity against any student-shaped profile.

    `profile` needs: skills, interests, latitude, longitude,
    max_hours_per_week, bio. If latitude/longitude are missing (e.g. no
    pincode given in a search), the proximity factor is skipped and its
    weight is redistributed over the remaining factors.
    """
    opps = _load_opportunities(conn)

    # Teach the semantic scorer the vocabulary once, for the whole corpus.
    corpus = [_semantic_text_student(profile)] + [
        _semantic_text_opp(o) for o in opps
    ]
    scorer = semantic.get_scorer()
    scorer.fit(corpus)

    profile_skills = set(profile.get("skills", []))
    profile_interests = set(profile.get("interests", []))
    has_location = (
        profile.get("latitude") is not None and profile.get("longitude") is not None
    )

    results = []
    for opp in opps:
        factors: list[scoring.FactorResult] = []

        sk, sk_note = scoring.skills_score(
            profile_skills, opp.get("required_skills", []), opp.get("helpful_skills", [])
        )
        factors.append(scoring.FactorResult("skills", sk, scoring.WEIGHTS["skills"], sk_note))

        cat, cat_note = scoring.category_score(
            profile_interests, opp.get("category", ""), opp.get("tags", [])
        )
        factors.append(scoring.FactorResult("category", cat, scoring.WEIGHTS["category"], cat_note))

        if has_location:
            dist = scoring.haversine_miles(
                profile["latitude"], profile["longitude"],
                opp["latitude"], opp["longitude"],
            )
            prox, prox_note = scoring.proximity_score(dist)
            factors.append(scoring.FactorResult("proximity", prox, scoring.WEIGHTS["proximity"], prox_note))

        tm, tm_note = scoring.time_score(
            profile.get("max_hours_per_week", 0),
            opp.get("hours_min", 0),
            opp.get("hours_max", 0),
        )
        factors.append(scoring.FactorResult("time", tm, scoring.WEIGHTS["time"], tm_note))

        sem = _semantic_factor(profile, opp, scorer)
        if sem is not None:
            factors.append(sem)

        total01, breakdown = scoring.combine(factors)
        reasons = scoring.build_reasons(factors)

        results.append(
            {
                "opportunity": opp,
                "total": round(total01 * 100),
                "breakdown": breakdown,
                "reasons": reasons,
            }
        )

    results.sort(key=lambda r: r["total"], reverse=True)
    return results[:limit]