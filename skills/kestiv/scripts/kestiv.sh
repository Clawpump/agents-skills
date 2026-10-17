#!/usr/bin/env bash
# Thin wrapper around the Kestiv CLI. Locates the repo, builds once, then execs the CLI.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
home="${KESTIV_HOME:-$(cd "$here/../../.." 2>/dev/null && pwd)}"

if [ ! -f "$home/agent/package.json" ]; then
  echo "kestiv: cannot find the Kestiv repo. Clone https://github.com/mystiquemide/kestiv and set KESTIV_HOME to the checkout." >&2
  exit 2
fi

cd "$home"

if [ ! -f agent/dist/cli.js ]; then
  command -v npm >/dev/null 2>&1 || { echo "kestiv: npm is required to build the agent" >&2; exit 2; }
  echo "kestiv: building agent (first run)..." >&2
  [ -d node_modules ] || npm install --no-audit --no-fund >&2
  npm run build -w agent >&2
fi

exec node agent/dist/cli.js "$@"
