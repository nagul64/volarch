"""FastAPI application. Run with:

    uvicorn app.main:app --reload

from inside the `backend/` folder, then open http://localhost:8000/docs
for an auto-generated, clickable API explorer.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import db, llm, recommender, seed, semantic
from .models import (
    MatchResult,
    Opportunity,
    SearchProfile,
    SearchRequest,
    SearchResult,
    SemanticDiagnostics,
    Student,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    conn = db.get_conn()
    try:
        if seed.seed_if_empty(conn):
            print("Seeded sample data into volunteer.db")
        else:
            print("Database already contains data — skipping seed")
    finally:
        conn.close()
    yield


app = FastAPI(title="Volarch — Volunteer Matching AI", version="0.1.0", lifespan=lifespan)

# The React dev server runs on :5173; allow it (and anything else in dev).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    prov, _desc = semantic.provider_description()
    return {"status": "ok", "semantic_provider": prov}


@app.get("/students", response_model=list[Student])
def list_students():
    conn = db.get_conn()
    try:
        rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
        return [db.to_dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    conn = db.get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return db.to_dict(row)


@app.get("/opportunities", response_model=list[Opportunity])
def list_opportunities():
    conn = db.get_conn()
    try:
        rows = conn.execute("SELECT * FROM opportunities ORDER BY title").fetchall()
        return [db.to_dict(r) for r in rows]
    finally:
        conn.close()


@app.get(
    "/students/{student_id}/matches",
    response_model=list[MatchResult],
)
def student_matches(student_id: int, limit: int = 10):
    limit = min(max(limit, 1), 50)
    conn = db.get_conn()
    try:
        return recommender.recommend_for_student(conn, student_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        conn.close()


@app.get("/diagnostics/semantic", response_model=SemanticDiagnostics)
def semantic_diagnostics():
    provider, description = semantic.provider_description()
    return SemanticDiagnostics(provider=provider, description=description)


@app.post("/search", response_model=SearchResult)
def search(req: SearchRequest, limit: int = 10):
    """Best-effort AI search: parse the free-text query into a profile, then
    rank opportunities against it.

    Extraction mode ("gemini" vs "local-keyword") and the active semantic
    provider are both returned so the UI can show what's actually running.
    """
    limit = min(max(limit, 1), 50)
    try:
        profile, extraction = llm.extract(req.query, req.zip)
    except llm.LlmError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    conn = db.get_conn()
    try:
        matches = recommender.recommend(conn, profile, limit=limit)
    finally:
        conn.close()

    # Reported *after* scoring so a bad API key that demoted to TF-IDF shows
    # what actually ran, not what we hoped to use.
    semantic_provider, _desc = semantic.provider_description()

    return SearchResult(
        extraction=extraction,
        semantic=semantic_provider,
        profile=SearchProfile(**profile),
        matches=matches,
    )