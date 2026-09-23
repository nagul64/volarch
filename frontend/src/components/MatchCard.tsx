import type { MatchResult } from '../types'
import ScoreBreakdown from './ScoreBreakdown'

export default function MatchCard({ match, rank }: { match: MatchResult; rank: number }) {
  const opp = match.opportunity
  return (
    <article className="match">
      <div className="matchTop">
        <span className="rank">#{rank}</span>
        <div className="matchTitle">
          <h3>{opp.title}</h3>
          <p className="org">{opp.org_name}</p>
        </div>
        <div className="totalBadge">
          <span className="totalScore">{match.total}</span>
          <span className="totalLabel">match</span>
        </div>
      </div>

      <div className="chips">
        <span className="chip chipCat">{opp.category}</span>
        <span className="chip">{opp.hours_min}–{opp.hours_max} h/wk</span>
        <span className="chip">{opp.zip_code}</span>
        {opp.tags.map((t) => (
          <span className="chip chipTag" key={t}>#{t}</span>
        ))}
      </div>

      <p className="desc">{opp.description}</p>

      {match.reasons.length > 0 && (
        <ul className="reasons">
          {match.reasons.map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      )}

      <ScoreBreakdown factors={match.breakdown} />
    </article>
  )
}