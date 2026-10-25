#!/usr/bin/env bash
# Pre-submission safety net. Run: make verify
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail=0
ok()   { printf "  \033[32mPASS\033[0m  %s\n" "$1"; }
bad()  { printf "  \033[31mFAIL\033[0m  %s\n" "$1"; fail=1; }
warn() { printf "  \033[33mWARN\033[0m  %s\n" "$1"; }

echo ""
echo "recHERsion 2026 — pre-submission verification"
echo "─────────────────────────────────────────────"

# 1. No secrets committed
if [ -f .env ] && git check-ignore -q .env 2>/dev/null; then ok ".env present and git-ignored"
elif [ -f .env ]; then bad ".env exists but is NOT git-ignored — add it to .gitignore"
else ok "no .env in repo root"; fi

if git ls-files | grep -qE '^(\.env$|.*\.env$)' 2>/dev/null; then bad "a .env file is TRACKED by git — remove it now"
else ok "no tracked .env files"; fi

if git grep -InE '(api[_-]?key|secret|password|token)\s*=\s*["'"'"'][A-Za-z0-9_\-]{16,}' -- '*.py' '*.js' '*.jsx' 2>/dev/null | grep -q .; then
  bad "possible hardcoded secret found — run: git grep -InE 'api[_-]?key|secret|password'"
else ok "no hardcoded secrets in source"; fi

# 2. Required files
for f in README.md LICENSE THIRD-PARTY-NOTICES.md .gitignore .env.example; do
  [ -f "$f" ] && ok "$f exists" || bad "$f is MISSING"
done

# 3. Frontend builds
if [ -d frontend ]; then
  if [ -d frontend/node_modules ]; then
    (cd frontend && npm run build >/tmp/build.log 2>&1) && ok "frontend builds" || bad "frontend build FAILED (see /tmp/build.log)"
  else warn "frontend/node_modules missing — run 'npm install' then re-verify"; fi
else warn "no frontend/ directory"; fi

# 4. Backend imports
if [ -d backend ]; then
  (cd backend && python3 -c "import main" >/tmp/imp.log 2>&1) && ok "backend imports cleanly" || bad "backend import FAILED (see /tmp/imp.log)"
else warn "no backend/ directory"; fi

# 5. Git state
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  [ -n "$(git status --porcelain 2>/dev/null)" ] && warn "uncommitted changes — remember: LAST PUSH BY 20:30 IST" || ok "working tree clean"
  remote="$(git remote get-url origin 2>/dev/null || echo '')"
  [ -n "$remote" ] && ok "remote: $remote" || bad "no git remote — judges need a repo URL"
  n="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
  echo "  INFO  $n commits so far"
else warn "not a git repository yet"; fi

# 6. Clock sanity — your commit timestamp comes from THIS machine
echo "  INFO  server time: $(TZ=Asia/Kolkata date '+%a %d %b %Y %H:%M IST')"

echo "─────────────────────────────────────────────"
[ $fail -eq 0 ] && echo "  ✅ All checks passed." || echo "  ❌ Fix the failures above before submitting."
echo ""
exit $fail
