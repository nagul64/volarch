import type { ScoreFactor } from '../types'

function scoreColor(score: number): string {
  if (score >= 75) return 'var(--good)'
  if (score >= 45) return 'var(--mid)'
  return 'var(--low)'
}

export default function ScoreBreakdown({ factors }: { factors: ScoreFactor[] }) {
  return (
    <div className="breakdown">
      {factors.map((f) => (
        <div className="factor" key={f.name}>
          <div className="factorHead">
            <span className="factorName">{f.name}</span>
            <span className="factorMeta">
              {f.score}/100 · {f.weight}% weight
            </span>
          </div>
          <div className="bar">
            <div
              className="barFill"
              style={{
                width: `${f.score}%`,
                background: scoreColor(f.score),
              }}
            />
          </div>
          <div className="factorNote">{f.note}</div>
        </div>
      ))}
    </div>
  )
}