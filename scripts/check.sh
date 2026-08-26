#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_root}/src"

python3 -m unittest discover -s "${repo_root}/tests" -p 'test_*.py' -v
python3 -m agentguard.demo >/dev/null
/usr/bin/bash -n "${repo_root}/scripts/run-local.sh"
/usr/bin/bash -n "${repo_root}/scripts/prove-live-read.sh"
/usr/bin/bash -n "${repo_root}/scripts/browser-e2e.sh"
node --check "${repo_root}/scripts/browser-e2e.mjs"

if [[ ! -d "${repo_root}/frontend/node_modules" ]]; then
  printf '%s\n' 'ERROR: frontend dependencies missing; run npm ci in frontend' >&2
  exit 2
fi

npm --prefix "${repo_root}/frontend" run check
