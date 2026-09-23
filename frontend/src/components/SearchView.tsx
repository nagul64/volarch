import { useState } from 'react'
import { api } from '../api'
import MatchCard from './MatchCard'
import type { SearchResult } from '../types'

const EXAMPLE = "I love animals and can volunteer on weekends near RS Puram."

export default function SearchView() {
  const [query, setQuery] = useState('')
  const [zip, setZip] = useState('')
  const [result, setResult] = useState<SearchResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function run(e: React.FormEvent) {
    e.preventDefault()
    const q = query.trim()
    if (!q) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await api.search(q, zip.trim() || undefined))
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="results">
      <form className="searchBox" onSubmit={run}>
        <label htmlFor="ai-query" className="searchLabel">
          Describe yourself — the AI will find your volunteer matches
        </label>
        <textarea
          id="ai-query"
          className="searchInput"
          rows={3}
          placeholder={EXAMPLE}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="searchRow">
          <input
            className="zipInput"
            placeholder="PIN code (optional)"
            value={zip}
            onChange={(e) => setZip(e.target.value)}
          />
          <button className="searchBtn" type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Find matches'}
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p className="muted">Analyzing your message and scoring opportunities…</p>}

      {result && (
        <>
          <div className="modeLine" title="Which engines handled this search">
            <span className="badge" data-engine={result.extraction}>
              extraction: {result.extraction}
            </span>
            <span className="badge" data-engine="semantic">
              semantic: {result.semantic}
            </span>
          </div>

          <aside className="profile">
            <h2>Your parsed profile</h2>
            <p className="bio">{result.profile.bio}</p>
            <div>
              <strong>Skills:</strong>{' '}
              <span className="chip">
                {result.profile.skills.length
                  ? result.profile.skills.join(', ')
                  : 'none detected'}
              </span>
            </div>
            <div>
              <strong>Interests:</strong>{' '}
              <span className="chip">
                {result.profile.interests.length
                  ? result.profile.interests.join(', ')
                  : 'none detected'}
              </span>
            </div>
            <div>
              <strong>Available:</strong> {result.profile.max_hours_per_week} h/wk ·{' '}
              PIN {result.profile.zip_code || '—'}
            </div>
          </aside>

          <h2>Top matches</h2>
          {result.matches.length === 0 && <p className="muted">No matches found.</p>}
          {result.matches.map((m, i) => (
            <MatchCard key={m.opportunity.id} match={m} rank={i + 1} />
          ))}
        </>
      )}
    </section>
  )
}