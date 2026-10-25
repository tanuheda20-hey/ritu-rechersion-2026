export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null
  return (
    <div className="error-banner" role="alert">
      <span>
        <strong>Something went wrong.</strong> {message}
      </span>
      <button type="button" onClick={onDismiss} aria-label="Dismiss error">×</button>
    </div>
  )
}
