import { useEffect, useState } from 'react'
import { api } from './api'
import MatchCard from './components/MatchCard'
import SearchView from './components/SearchView'
import type { Diagnostics, MatchResult, Opportunity, Student } from './types'

type View = 'search' | 'student' | 'all'

export default function App() {
  const [students, setStudents] = useState<Student[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [diagnostics, setDiagnostics] = useState<Diagnostics | null>(null)
  const [matches, setMatches] = useState<MatchResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState<View>('search')

  useEffect(() => {
    api
      .students()
      .then((s) => {
        setStudents(s)
        if (s.length > 0) setSelectedId(s[0].id)
      })
      .catch((e) => setError(String(e)))

    api.diagnostics().then(setDiagnostics).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedId === null) return
    setLoading(true)
    setError(null)
    api
      .matches(selectedId)
      .then((m) => {
        setMatches(m)
        setLoading(false)
      })
      .catch((e) => {
        setError(String(e))
        setLoading(false)
      })
  }, [selectedId])

  const selected = students.find((s) => s.id === selectedId) ?? null

  return (
    <div className="page">
      <header className="header">
        <div className="brand">
          <span className="logo">◆</span>
          <div>
            <h1>Volarch</h1>
            <p>AI recommendation engine — students ↔ community volunteering</p>
          </div>
        </div>
        {diagnostics && (
          <div className="provider" title={diagnostics.description}>
            <span className="pulse" />
            semantic: {diagnostics.provider}
          </div>
        )}
      </header>

      <main>
        <section className="controls">
          <div className="tabs">
            <button
              className={view === 'search' ? 'tab active' : 'tab'}
              onClick={() => setView('search')}
            >
              AI search
            </button>
            <button
              className={view === 'student' ? 'tab active' : 'tab'}
              onClick={() => setView('student')}
            >
              Student view
            </button>
            <button
              className={view === 'all' ? 'tab active' : 'tab'}
              onClick={() => setView('all')}
            >
              All opportunities
            </button>
          </div>

          {view === 'student' && (
            <select
              className="select"
              value={selectedId ?? ''}
              onChange={(e) => setSelectedId(Number(e.target.value))}
            >
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} · {s.school} ({s.grade})
                </option>
              ))}
            </select>
          )}
        </section>

        {view === 'student' && selected && (
          <aside className="profile">
            <h2>{selected.name}</h2>
            <p className="bio">{selected.bio}</p>
            <div>
              <strong>Skills:</strong>{' '}
              <span className="chip">{selected.skills.join(', ')}</span>
            </div>
            <div>
              <strong>Interests:</strong>{' '}
              <span className="chip">{selected.interests.join(', ')}</span>
            </div>
            <div>
              <strong>Available:</strong> {selected.max_hours_per_week} h/wk ·{' '}
              PIN {selected.zip_code}
            </div>
          </aside>
        )}

        {view === 'search' ? (
          <SearchView />
        ) : view === 'all' ? (
          <AllOpportunities />
        ) : (
          <section className="results">
            <h2>Top matches</h2>
            {error && <p className="error">{error}</p>}
            {loading && <p className="muted">Computing matches…</p>}
            {!loading && matches.length === 0 && <p className="muted">No matches.</p>}
            {matches.map((m, i) => (
              <MatchCard key={m.opportunity.id} match={m} rank={i + 1} />
            ))}
          </section>
        )}
      </main>

      <footer className="footer">
        <p>
          Backend &rarr; FastAPI · SQLite · hybrid scorer (content-based + semantic)
        </p>
      </footer>
    </div>
  )
}

function AllOpportunities() {
  const [opps, setOpps] = useState<Opportunity[]>([])
  useEffect(() => {
    api
      .opportunities()
      .then(setOpps)
      .catch(() => {})
  }, [])
  return (
    <section className="results">
      <h2>All {opps.length} opportunities</h2>
      <div className="oppGrid">
        {opps.map((o) => (
          <article className="oppCard" key={o.id}>
            <h3>{o.title}</h3>
            <p className="org">{o.org_name}</p>
            <div className="chips">
              <span className="chip chipCat">{o.category}</span>
              <span className="chip">{o.hours_min}–{o.hours_max} h/wk</span>
              <span className="chip">{o.zip_code}</span>
            </div>
            <p className="desc">{o.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}