import { useState } from 'react'

const STRENGTH_LABEL = { high: 'Strong signal', moderate: 'Moderate signal', low: 'Weak signal' }

export default function SignalCard({ signal }) {
  const [open, setOpen] = useState(false)

  return (
    <article className={`signal strength-${signal.strength}`}>
      <div className="signal-head">
        <div>
          <h3 className="signal-name">{signal.name}</h3>
          <span className={`badge badge-${signal.strength}`}>
            {STRENGTH_LABEL[signal.strength] ?? signal.strength}
          </span>
        </div>
        <button type="button" className="btn-ghost" aria-expanded={open}
                onClick={() => setOpen((v) => !v)}>
          {open ? 'Hide detail' : 'What to ask'}
        </button>
      </div>

      <ul className="evidence">
        {signal.evidence.map((e, i) => <li key={i}>{e}</li>)}
      </ul>

      <p className="signal-meaning">{signal.meaning}</p>

      {open && (
        <div className="signal-detail">
          <div className="detail-block">
            <h4>Questions to ask your doctor</h4>
            <ol>
              {signal.questions.map((q, i) => <li key={i}>{q}</li>)}
            </ol>
          </div>
          <div className="detail-block">
            <h4>Tests worth discussing</h4>
            <ul className="pill-list">
              {signal.tests.map((t, i) => <li key={i} className="pill">{t}</li>)}
            </ul>
          </div>
        </div>
      )}
    </article>
  )
}