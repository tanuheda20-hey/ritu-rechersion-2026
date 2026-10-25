import CycleStats from './CycleStats'
import SignalCard from './SignalCard'

const SCENARIOS = [
  { id: 'pcos', label: 'Priya, 21', hint: 'Irregular cycles' },
  { id: 'endometriosis', label: 'Ananya, 24', hint: 'Severe pain' },
  { id: 'anaemia', label: 'Meera, 27', hint: 'Heavy bleeding' },
  { id: 'healthy', label: 'Ishita, 22', hint: 'No strong pattern' },
]

export default function InsightPanel({ insights, logs, onLoadScenario, disabled }) {
  if (!insights) {
    return (
      <div className="card empty-state">
        <span className="empty-icon" aria-hidden="true">◐</span>
        <p>Loading your patterns…</p>
      </div>
    )
  }

  const { urgency, signals, cycle_stats: stats } = insights

  if (!stats?.has_enough_data) {
    return (
      <>
        <div className={`urgency urgency-routine`}>
          <span className="urgency-label">Not enough data yet</span>
          <p>
            Log at least five days — ideally a couple of cycles — and patterns will start
            appearing here. Consistency is what makes this useful.
          </p>
        </div>
        <DemoCases onLoadScenario={onLoadScenario} disabled={disabled} active={null} />
      </>
    )
  }

  return (
    <>
      <div className={`urgency urgency-${urgency.level}`} role="status">
        <span className="urgency-label">{urgency.label}</span>
        <p>{urgency.advice}</p>
      </div>

      <CycleStats stats={stats} />

      <section aria-labelledby="patterns">
        <h2 className="section-title" id="patterns">
          Patterns the engine found
          <span className="count"> {signals.length}</span>
        </h2>

        {signals.length === 0 ? (
          <div className="card empty-state">
            <span className="empty-icon" aria-hidden="true">✓</span>
            <p>
              <strong>No strong pattern detected.</strong>
              <br />
              That is a real result, not a failure. The engine deliberately stays quiet
              when there is nothing to find — every signal below is earned by matching
              specific criteria, not guessed at.
            </p>
          </div>
        ) : (
          signals.map((s) => <SignalCard key={s.key} signal={s} />)
        )}
      </section>

      <DemoCases onLoadScenario={onLoadScenario} disabled={disabled} active={null} />

      <p className="meta-note">
        {logs.length} daily entries analysed · every signal above lists the exact criteria
        that triggered it, so you can check the reasoning yourself.
      </p>
    </>
  )
}

function DemoCases({ onLoadScenario, disabled, active }) {
  return (
    <section className="card demo-cases" aria-labelledby="demo-cases">
      <h2 className="section-title" id="demo-cases">Try a demo case</h2>
      <p className="hint">
        Loads three cycles of realistic logs so you can see how the engine behaves on
        different presentations — including one where it correctly finds nothing.
      </p>
      <div className="chips">
        {SCENARIOS.map((s) => (
          <button key={s.id} type="button" className="chip chip-action"
                  disabled={disabled} aria-pressed={active === s.id}
                  onClick={() => onLoadScenario(s.id)}>
            <strong>{s.label}</strong>
            <span className="chip-hint">{s.hint}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
