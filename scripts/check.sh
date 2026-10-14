#!/usr/bin/env bash
# check.sh — every quality gate in one portable script.
# Runs the same on a laptop, on GitHub Actions, GitLab CI, Codeberg (Forgejo Actions) or any CI.
# CI files are thin wrappers around this script, so no check is locked to one platform.
set -euo pipefail
GITLEAKS_VERSION="${GITLEAKS_VERSION:-8.28.0}"
LYCHEE_VERSION="${LYCHEE_VERSION:-0.20.1}"
BIN="${BIN_DIR:-$HOME/.local/bin}"; mkdir -p "$BIN"; export PATH="$BIN:$PATH"
os=$(uname -s | tr '[:upper:]' '[:lower:]'); arch=$(uname -m); [ "$arch" = "aarch64" ] && arch=arm64; [ "$arch" = "x86_64" ] && arch=x64

step() { printf '\n▶ %s\n' "$*"; }

step "1/4 secret scan, full history (gitleaks, MIT licence, no key needed)"
if ! command -v gitleaks >/dev/null; then
  curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${os}_${arch}.tar.gz" | tar -xz -C "$BIN" gitleaks
fi
gitleaks git . --redact --no-banner

step "2/4 deny-list (client names, hosts, personal data markers) — skipped if no list"
if [ -n "${DENY_LIST:-}" ] && [ -f "$DENY_LIST" ]; then
  if grep -rInEf "$DENY_LIST" . --exclude-dir=.git; then echo "✖ deny-listed terms found"; exit 1; fi
fi

step "3/4 Markdown links (lychee, offline-safe: skips if binary unavailable)"
if ! command -v lychee >/dev/null; then
  l_arch=$([ "$arch" = arm64 ] && echo aarch64 || echo x86_64)
  curl -sSfL "https://github.com/lycheeverse/lychee/releases/download/lychee-v${LYCHEE_VERSION}/lychee-${l_arch}-unknown-linux-gnu.tar.gz" 2>/dev/null | tar -xz -C "$BIN" lychee 2>/dev/null || echo "lychee not installed; skipping link check"
fi
command -v lychee >/dev/null && lychee --no-progress ${LYCHEE_OFFLINE:+--offline} './**/*.md'

step "4/4 project tests"
if [ -f package.json ]; then npm ci && npm test; fi
if [ -f requirements.txt ]; then
  # Hash-pinned dependencies only (OpenSSF Scorecard: Pinned-Dependencies)
  python3 -m pip install -q --require-hashes -r requirements.txt 2>/dev/null || python3 -m pip install -q --break-system-packages --require-hashes -r requirements.txt
  python3 -m pytest -q
fi
echo "✅ all checks passed"
