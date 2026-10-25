import { useEffect, useState } from 'react'

/**
 * Minimal renderer for the exact markdown subset our report emits
 * (#, ##, ###, -, 1., **bold**, *italic*, ---). Hand-rolled on purpose:
 * it keeps the bundle small and avoids pulling in a parser dependency.
 */
function renderBlock(line, key) {
  const inline = (text) => {
    const parts = []
    const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g
    let last = 0
    let m
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) parts.push(text.slice(last, m.index))
      const tok = m[0]
      if (tok.startsWith('**')) parts.push(<strong key={m.index}>{tok.slice(2, -2)}</strong>)
      else parts.push(<em key={m.index}>{tok.slice(1, -1)}</em>)
      last = m.index + tok.length
    }
    if (last < text.length) parts.push(text.slice(last))
    return parts
  }

  if (/^###\s+/.test(line)) return <h3 key={key} className="rpt-h3">{inline(line.replace(/^###\s+/, ''))}</h3>
  if (/^##\s+/.test(line)) return <h2 key={key} className="rpt-h2">{inline(line.replace(/^##\s+/, ''))}</h2>
  if (/^#\s+/.test(line)) return <h1 key={key} className="rpt-h1">{inline(line.replace(/^#\s+/, ''))}</h1>
  if (/^---+$/.test(line.trim())) return <hr key={key} />
  if (/^\d+\.\s+/.test(line)) return <li key={key} className="rpt-num">{inline(line.replace(/^\d+\.\s+/, ''))}</li>
  if (/^-\s+/.test(line)) return <li key={key} className="rpt-bullet">{inline(line.replace(/^-\s+/, ''))}</li>
  if (line.trim() === '') return null
  return <p key={key} className="rpt-p">{inline(line)}</p>
}

export default function ReportView({ profile, onLoad }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    setLoading(true)
    onLoad()
      .then((r) => { if (alive) setReport(r) })
      .catch((e) => { if (alive) setError(e.message) })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [onLoad])

  if (loading) return <div className="card loading-card"><span className="spinner" />&nbsp; Building your report…</div>
  if (error) return <div className="card empty-state"><p>{error}</p></div>
  if (!report) return null

  const lines = report.markdown.split('\n')

  return (
    <>
      <div className="report-actions">
        <button type="button" className="btn-primary" onClick={() => window.print()}>
          Print / Save as PDF
        </button>
        <span className="hint">
          One page, written to be handed over — start with the urgency line, then the
          patterns, then the questions.
        </span>
      </div>

      <article className="report" aria-label="Symptom summary report">
        {lines.map((l, i) => renderBlock(l, i))}
      </article>

      <p className="disclaimer">{report.disclaimer}</p>
    </>
  )
}
