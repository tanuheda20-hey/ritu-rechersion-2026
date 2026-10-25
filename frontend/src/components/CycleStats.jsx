function Stat({ label, value, note, tone }) {
  return (
    <div className={`stat ${tone ? `stat-${tone}` : ''}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value ?? '—'}</div>
      {note && <div className="stat-note">{note}</div>}
    </div>
  )
}

export default function CycleStats({ stats }) {
  if (!stats) return null

  const irregular = stats.irregular_cycles
  const severePain = (stats.severe_pain_days ?? 0) > 0
  const heavy = (stats.heavy_bleeding_days ?? 0) > 0

  return (
    <section className="card" aria-labelledby="cycle-overview">
      <h2 className="section-title" id="cycle-overview">Cycle overview</h2>
      <div className="stats">
        <Stat label="Days logged" value={stats.logged_days}
              note={stats.first_log ? `${stats.first_log} → ${stats.last_log}` : ''} />
        <Stat label="Avg cycle" value={stats.avg_cycle_length ? `${stats.avg_cycle_length}d` : '—'}
              note={`${stats.period_starts} cycles`}
              tone={irregular ? 'warn' : undefined} />
        <Stat label="Variability" value={stats.cycle_variability_days !== null ? `${stats.cycle_variability_days}d` : '—'}
              note={irregular ? 'Irregular' : 'Regular'}
              tone={irregular ? 'warn' : 'ok'} />
        <Stat label="Heavy days" value={stats.heavy_bleeding_days}
              tone={heavy ? 'warn' : 'ok'} />
        <Stat label="Avg pain" value={stats.avg_pain !== null ? `${stats.avg_pain}/10` : '—'}
              note={`peak ${stats.max_pain ?? '—'}`}
              tone={severePain ? 'warn' : undefined} />
        <Stat label="Severe pain days" value={stats.severe_pain_days}
              note="7 or above" tone={severePain ? 'warn' : 'ok'} />
      </div>

      {stats.top_symptoms?.length > 0 && (
        <div className="top-symptoms">
          <span className="stat-label">Most logged</span>
          <ul className="pill-list">
            {stats.top_symptoms.map((s) => (
              <li key={s.tag} className="pill">{s.label} · {s.days}d</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
