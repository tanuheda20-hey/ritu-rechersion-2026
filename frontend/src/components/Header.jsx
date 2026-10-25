export default function Header({ online }) {
  const statusText =
    online === null ? 'connecting…' : online ? 'backend connected' : 'backend offline'
  const dotClass = online === null ? 'checking' : online ? 'on' : 'off'

  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="brand">
          <span className="brand-mark">◐</span> Ritu
          <span className="brand-sub">cycle-aware symptom intelligence</span>
        </div>
        <span className="status" role="status" aria-live="polite">
          <span className={`dot ${dotClass}`} aria-hidden="true" />
          {statusText}
        </span>
      </div>
    </header>
  )
}
