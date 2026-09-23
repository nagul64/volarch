# Volarch — AI Volunteer Matching

A **hybrid AI recommendation engine** that matches students to community
volunteer opportunities. Backend (FastAPI + SQLite) does the thinking; a
React frontend shows the results with an *explainable score breakdown* for
every match — not a black box.

---

## How it works, in plain English

### Frontend vs backend (the two halves of a website)

Your frontend experience (React) is the part you see and click. It has **no
data** itself — it *asks* for everything. The **backend** (Python) owns the
data and the brains:

```
  React (browser)          HTTP / JSON          FastAPI (Python)
  ──────────────    ───────────────────────→    ──────────────
  shows the UI                                 runs the matching math,
  draws the bars                               reads & writes SQLite
  asks: "GET /students/1/matches"   ←────────  returns JSON results
```

Think of it like a restaurant: the frontend is the **menu + waiter**, the
backend is the **kitchen**. The waiter writes the order on a slip (HTTP
request) and brings back the dish (JSON response). You never see the
kitchen — you just eat the results.

### What SQLite is, and why we used JSON columns

- A **database** is just a place data lives long-term. **SQLite** is the
  easiest one: a single file (`backend/volunteer.db`), no server, built into
  Python. Tables = spreadsheets with rows.
- **SQL** is the language we talk to it with: `SELECT` = "fetch rows",
  `INSERT` = "add rows".
- Inside a table, some columns hold **JSON blobs** (e.g. a student's
  `skills` stored as `["python","web-dev"]`). A "real production" system
  would split those into linked tables (called *normalizing*), but for a
  demo it keeps the code short and easy to edit. Both are legitimate.

### The recommendation math (the "AI")

Every student gets a score from **0–100** against every opportunity. Five
factors, each weighted by how much it matters:

| Factor      | Weight | What it measures                                    |
|-------------|--------|-----------------------------------------------------|
| Skills      | 30%    | Do the student's skills cover what the role requires?|
| Interests   | 25%    | Do the student's interest tags overlap the category + tags? |
| Proximity   | 20%    | Straight-line miles between student & opportunity (Haversine) |
| Time        | 15%    | Does the weekly hour range fit the student's availability? |
| Semantic    | 10%    | How "close in meaning" are the student's profile and the description? |

Example for **Kavya Sridhar** (`/students/1/matches`):

```
1. Adoption Day Crew — ARRC Animal Rescue       Total: 63
   skills 80  ·  interests 25  ·  proximity 85  ·  time 100  ·  semantic 12
```

Kavya matched the required `dog-handling` skill, lives ~7.5 miles from the
PN Palayam shelter, and can cover the full shift — so she ranks top. The
**score breakdown in every response is the whole point**: you can see *why*,
factor by factor.

### The semantic layer (real AI, but it degrades gracefully)

"Semantic" matching means comparing **meaning**, not exact words. Text is
converted to a list of numbers (an **embedding**), and matching = how
similar the two number-lists are. We try engines strongest-first:

1. **Gemini embeddings (Google AI Studio)** — set `GEMINI_API_KEY`.
2. **OpenAI embeddings** — set `OPENAI_API_KEY` (or `OPENAI_BASE_URL` +
   `OPENAI_EMBEDDING_MODEL` for local alternatives).
3. **sentence-transformers** — local neural model. `pip install
   sentence-transformers` (downloads ~90 MB on first use).
4. **Built-in TF-IDF** — plain Python, zero install, always works. Used
   automatically if the first three aren't available.

**The demo runs with zero API keys** because we land on option 4. Check which
engine is active at `GET /diagnostics/semantic` — the frontend shows it in the
header and on every AI-search result.

> **Honest degradation:** if a configured API key is dead/expired, the engine
> *permanently* demotes to TF-IDF (it doesn't keep advertising the API while
> silently failing). The badge always shows what actually ran — that's a
> deliberate design rule here.

### AI search with Google AI Studio (Gemini)

The default tab is a free-text search. You describe yourself — *"I love
animals and can give weekends, near RS Puram"* — and Gemini turns that into
a structured student profile (skills, interests, hours, pincode), which then
goes through the exact same weighted scoring as the seeded students.

- **GET `POST /search`** in `backend/app/main.py` via `llm.extract()`.
- The backend reports **two modes** on every search result so you always know
  what produced it:
  - `extraction` — `gemini` (Smart) vs `local-keyword` (fallback, no key).
  - `semantic` — which semantic engine scored the 10% factor.
- **No key? Search still works.** The keyword fallback in `llm.py` scans the
  message against the same allowed vocabulary, so matches still come back
  (with TF-IDF doing the semantic leg) — just labeled `local-keyword`.

### Where machine-vs-human judgment lives

- Skills, interests, proximity, time → **deterministic math** (never random,
  easy to audit).
- Semantic → the only *learned* part; it re-ranks ties caused by the math.
- If semantic is missing, that 10% is redistributed over the other factors,
  so totals still total 100.

---

## Run it

### 1. Backend (terminal 1)

```powershell
cd backend
python -m venv .venv          # one-time: isolated Python environment
.\.venv\Scripts\pip install -r requirements.txt
```

Add a Google AI Studio key (free) so the **AI search** and **Gemini
embeddings** turn on. Copy `backend\.env.example` to `backend\.env` and paste
your key in — the `.env` file is gitignored:

```powershell
Copy-Item .env.example .env
# then edit .env and set GEMINI_API_KEY=AIza...
```

Then start the server:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0
```

First launch prints `Seeded sample data into volunteer.db`. Your API lives
at http://localhost:8000 — and FastAPI gives you a **clickable API explorer**
at http://localhost:8000/docs (open it! every endpoint is testable there).

> **Why `--host 0.0.0.0`?** On Windows, `localhost` can resolve to the IPv6
> address `::1`, but uvicorn only listens on IPv4 by default — so the browser
> gets a silent "NetworkError". Binding to all interfaces fixes that and also
> lets you open the API from your phone on the same Wi-Fi.

### 2. Frontend (terminal 2)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Pick a student from the dropdown and watch the
ranked matches + per-factor bars appear.

### Confirm the API on its own

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/students
curl "http://localhost:8000/students/1/matches?limit=3"
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d "{\"query\": \"I love animals and free weekends\", \"zip\": \"641002\"}"
```

---

## Project map

| File | Job |
|------|-----|
| `backend/app/db.py` | SQLite connection + schema + row→dict helpers |
| `backend/app/seed.py` | The demo dataset (8 students, 16 opportunities) |
| `backend/app/scoring.py` | The weighted scoring factors + Haversine distance |
| `backend/app/semantic.py` | Embedding engines + TF-IDF fallback (+ auto-demotion) |
| `backend/app/llm.py` | Gemini search extraction + no-key keyword fallback |
| `backend/app/recommender.py` | Ties it together into ranked matches |
| `backend/app/main.py` | FastAPI routes (the API surface) |
| `backend/app/models.py` | Pydantic schemas (JSON shapes the API promises) |
| `frontend/src/App.tsx` | Main dashboard (AI search / student / all tabs) |
| `frontend/src/components/SearchView.tsx` | Free-text AI search + mode badges |
| `frontend/src/components/` | MatchCard, ScoreBreakdown, etc. |

---

## Your next experiments (all easy edits)

- **Add a student** — append a dict to `STUDENTS` in `backend/app/seed.py`,
  delete `volunteer.db`, restart the server. New data re-seeds
  automatically.
- **Add an opportunity** — same thing in `OPPORTUNITIES`.
- **Tune the weights** — `WEIGHTS` in `scoring.py`. Change `"semantic": 0.10`
  to `0.30` and watch the AI factor matter more.
- **Turn on real AI (Gemini)** — put `GEMINI_API_KEY=AIza...` in
  `backend/.env`, restart the backend. `/diagnostics/semantic`, the header
  badge, and every search result switch to `gemini`.
- **New AI search extractor** — tweak the prompt in `llm.extract_profile()`
  to recognize new sentences, or add entries to `ALLOWED_SKILLS` /
  `ALLOWED_INTERESTS` (and `seed.py`) so search and scoring share vocabulary.
- **New factor** — copy the shape of `proximity_score()` in `scoring.py`,
  add a weight, and feed it in `recommender.recommend_for_student()`.

## Optional upgrades (nice next steps)

- Real auth + student accounts (so students submit their own profiles)
- A "volunteer next" calendar feature
- Let organizations add opportunities through the API (CRUD)
- Docker: one-command startup for both halves