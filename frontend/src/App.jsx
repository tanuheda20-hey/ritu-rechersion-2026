import { useCallback, useEffect, useState } from 'react'
import api from './api'
import Header from './components/Header'
import SymptomLogger from './components/SymptomLogger'
import InsightPanel from './components/InsightPanel'
import ReportView from './components/ReportView'
import ErrorBanner from './components/ErrorBanner'
import Footer from './components/Footer'

const PROFILE = 'me'
const TABS = [
  { id: 'log', label: 'Log today' },
  { id: 'insights', label: 'Insights' },
  { id: 'report', label: 'Doctor report' },
]

/**
 * ⭐ The end-to-end workflow:
 *   log a day → engine recomputes patterns → one-page report a doctor can act on
 * Saving a log refreshes insights immediately, so the pattern panel updates
 * live. That live update is the strongest moment in the demo video.
 */
export default function App() {
  const [tab, setTab] = useState('insights')
  const [vocab, setVocab] = useState(null)
  const [insights, setInsights] = useState(null)
  const [logs, setLogs] = useState([])
  const [online, setOnline] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const refreshInsights = useCallback(async () => {
    const [ins, lg] = await Promise.all([api.insights(PROFILE), api.listLogs(PROFILE)])
    setInsights(ins)
    setLogs(lg)
  }, [])

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        const [v, health] = await Promise.all([api.symptoms(), api.health()])
        if (!alive) return
        setVocab(v)
        setOnline(true)
      } catch {
        if (alive) setOnline(false)
      }
      try {
        await refreshInsights()
      } catch (err) {
        if (alive) setError(err.message)
      }
    })()
    return () => { alive = false }
  }, [refreshInsights])

  async function handleSave(payload) {
    setBusy(true)
    setError(null)
    try {
      await api.createLog({ ...payload, profile: PROFILE })
      await refreshInsights()
      setTab('insights')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleScenario(scenario) {
    setBusy(true)
    setError(null)
    try {
      const res = await api.loadScenario(scenario, PROFILE)
      setInsights(res.insights)
      setLogs(await api.listLogs(PROFILE))
      setTab('insights')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const stats = insights?.cycle_stats
  const loggedDays = stats?.logged_days ?? 0

  return (
    <div className="app">
      <Header online={online} />

      <main className="container" id="main">
        <h1 className="hero-title">
          Your symptoms are data. <span className="accent">Make them impossible to dismiss.</span>
        </h1>
        <p className="hero-sub">
          Ritu turns months of cycle-aware symptom logs into patterns you can hand to a doctor —
          with the questions to ask and the tests to request.
        </p>

        <ErrorBanner message={error} onDismiss={() => setError(null)} />

        <nav className="tabs" aria-label="Sections">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`tab ${tab === t.id ? 'tab-active' : ''}`}
              aria-current={tab === t.id ? 'page' : undefined}
              onClick={() => setTab(t.id)}
            >
              {t.label}
              {t.id === 'insights' && insights?.signals?.length ? (
                <span className="tab-badge">{insights.signals.length}</span>
              ) : null}
              {t.id === 'log' && loggedDays ? <span className="tab-badge muted">{loggedDays}d</span> : null}
            </button>
          ))}
        </nav>

        {busy && (
          <div className="card loading-card" aria-live="polite">
            <span className="spinner" />&nbsp; Updating…
          </div>
        )}

        {tab === 'log' && (
          <SymptomLogger vocab={vocab} onSave={handleSave} disabled={busy} />
        )}

        {tab === 'insights' && (
          <InsightPanel
            insights={insights}
            logs={logs}
            onLoadScenario={handleScenario}
            disabled={busy}
          />
        )}

        {tab === 'report' && (
          <ReportView profile={PROFILE} onLoad={() => api.report(PROFILE)} />
        )}
      </main>

      <Footer disclaimer={insights?.disclaimer} />
    </div>
  )
}
