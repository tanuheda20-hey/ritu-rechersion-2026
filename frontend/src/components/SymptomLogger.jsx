import { useState } from 'react'

const FLOWS = ['none', 'spotting', 'light', 'medium', 'heavy', 'very_heavy']
const FLOW_LABEL = {
  none: 'None', spotting: 'Spotting', light: 'Light',
  medium: 'Medium', heavy: 'Heavy', very_heavy: 'Very heavy',
}
const PAIN_LABEL = [
  'No pain', 'Barely noticeable', 'Mild', 'Uncomfortable', 'Distracting',
  'Painful', 'Very painful', 'Severe', 'Debilitating', 'Nearly unbearable', 'Worst imaginable',
]

function today() {
  return new Date().toISOString().slice(0, 10)
}

export default function SymptomLogger({ vocab, onSave, disabled }) {
  const [logDate, setLogDate] = useState(today())
  const [isPeriodStart, setIsPeriodStart] = useState(false)
  const [flow, setFlow] = useState('none')
  const [pain, setPain] = useState(0)
  const [selected, setSelected] = useState([])
  const [notes, setNotes] = useState('')

  const toggle = (key) =>
    setSelected((prev) => (prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]))

  const groups = vocab?.groups ?? []
  const redFlags = new Set(vocab?.red_flags ?? [])

  function submit(e) {
    e.preventDefault()
    onSave({ log_date: logDate, is_period_start: isPeriodStart, flow, pain, symptoms: selected, notes })
  }

  function reset() {
    setIsPeriodStart(false); setFlow('none'); setPain(0); setSelected([]); setNotes('')
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2 className="section-title">Log a day</h2>
      <p className="hint">
        Twenty seconds a day. The pattern only appears once there are a few cycles of data.
      </p>

      <div className="field-row">
        <div className="field">
          <label htmlFor="log-date">Date</label>
          <input id="log-date" type="date" value={logDate} max={today()}
                 onChange={(e) => setLogDate(e.target.value)} disabled={disabled} />
        </div>
        <div className="field">
          <label htmlFor="flow">Bleeding</label>
          <select id="flow" value={flow} onChange={(e) => setFlow(e.target.value)} disabled={disabled}>
            {FLOWS.map((f) => <option key={f} value={f}>{FLOW_LABEL[f]}</option>)}
          </select>
        </div>
      </div>

      <div className="checkbox-row">
        <input id="period-start" type="checkbox" checked={isPeriodStart}
               onChange={(e) => setIsPeriodStart(e.target.checked)} disabled={disabled} />
        <label htmlFor="period-start">My period started today</label>
      </div>

      <div className="field">
        <label htmlFor="pain">
          Pain level <span className="hint">— {pain}/10 · {PAIN_LABEL[pain]}</span>
        </label>
        <input id="pain" type="range" min="0" max="10" step="1" value={pain}
               onChange={(e) => setPain(Number(e.target.value))} disabled={disabled}
               className="slider" aria-valuetext={`${pain} out of 10, ${PAIN_LABEL[pain]}`} />
        <div className="slider-scale" aria-hidden="true">
          <span>0 — none</span><span>10 — worst</span>
        </div>
      </div>

      {groups.length === 0 && <p className="hint">Loading symptom list…</p>}

      {groups.map((g) => (
        <fieldset key={g.category} className="chip-group" disabled={disabled}>
          <legend>{g.label}</legend>
          <div className="chips">
            {g.symptoms.map((s) => {
              const active = selected.includes(s.key)
              const isFlag = redFlags.has(s.key)
              return (
                <button
                  key={s.key}
                  type="button"
                  className={`chip ${active ? 'chip-on' : ''} ${isFlag ? 'chip-flag' : ''}`}
                  aria-pressed={active}
                  onClick={() => toggle(s.key)}
                >
                  {s.label}
                </button>
              )
            })}
          </div>
        </fieldset>
      ))}

      {redFlags.size > 0 && (
        <p className="flag-note">
          <strong>Red-outlined symptoms</strong> are the ones clinical guidance says should be
          seen by a doctor rather than tracked at home. They are always escalated.
        </p>
      )}

      <div className="field">
        <label htmlFor="notes">Notes <span className="hint">— optional</span></label>
        <input id="notes" type="text" value={notes} maxLength={1000}
               placeholder="Anything else worth remembering"
               onChange={(e) => setNotes(e.target.value)} disabled={disabled} />
      </div>

      <div className="actions">
        <button type="submit" className="btn-primary" disabled={disabled}>Save day</button>
        <button type="button" className="btn-secondary" onClick={reset} disabled={disabled}>Clear</button>
      </div>
    </form>
  )
}
