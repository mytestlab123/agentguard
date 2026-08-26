#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_root}/src"
api_pid=""
ready_file="$(mktemp /tmp/agentguard-api-port.XXXXXX)"

cleanup() {
  if [[ -n "${api_pid}" ]] && kill -0 "${api_pid}" 2>/dev/null; then
    kill "${api_pid}" 2>/dev/null || true
    wait "${api_pid}" 2>/dev/null || true
  fi
  rm -f -- "${ready_file}"
}
trap cleanup EXIT INT TERM

requested_port="${AGENTGUARD_API_PORT:-0}"
python3 -m agentguard.api --port "${requested_port}" --ready-file "${ready_file}" &
api_pid=$!
api_port="$(python3 -m agentguard.wait_api --ready-file "${ready_file}")"
export AGENTGUARD_API_PORT="${api_port}"
printf 'AgentGuard Vite proxy using local API port %s\n' "${api_port}"

npm --prefix "${repo_root}/frontend" run dev
