export default function Footer({ disclaimer }) {
  return (
    <footer className="site-footer">
      {disclaimer && <p className="footer-disclaimer">{disclaimer}</p>}
      <div className="footer-inner">
        <span>
          <strong>Ritu</strong> · built for <strong>recHERsion 2026</strong> · ACM-W NITK Surathkal · PS1 Women&apos;s Healthcare
        </span>
        <span>
          <a href="https://github.com/YOUR-ORG/YOUR-REPO" target="_blank" rel="noreferrer noopener">GitHub</a>
          {' · '}
          <a href="/api/docs" target="_blank" rel="noreferrer noopener">API docs</a>
        </span>
      </div>
    </footer>
  )
}
