#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
evidence_root="${AGENTGUARD_E2E_OUTPUT_DIR:-${HOME}/.AGENTS-temp/agentguard/browser-e2e}"
run_dir="${evidence_root}/run-$(date +%Y%m%d-%H%M%S)-$$"
service_pgid=""
browser_work_dir=""
windows_temp_wsl=""

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"
}

port_is_free() {
  ! ss -ltnH "sport = :$1" | grep -q .
}

choose_port() {
  local candidate
  local first=$1
  for ((candidate = first; candidate < first + 100; candidate++)); do
    if port_is_free "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

validate_port() {
  local port=$1
  [[ "$port" =~ ^[0-9]+$ ]] || fail "invalid port: $port"
  ((port >= 1024 && port <= 65535)) || fail "port outside allowed range: $port"
  port_is_free "$port" || fail "port already in use: $port"
}

wait_for_url() {
  local url=$1
  local attempt
  for ((attempt = 1; attempt <= 60; attempt++)); do
    if curl --fail --silent --show-error "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  fail "readiness check failed: $url"
}

wait_for_port_release() {
  local port=$1
  local attempt
  for ((attempt = 1; attempt <= 40; attempt++)); do
    if port_is_free "$port"; then
      return 0
    fi
    sleep 0.25
  done
  fail "owned listener did not release port: $port"
}

stop_services() {
  local pgid=$service_pgid
  if [[ -n "$pgid" ]] && kill -0 -- "-$pgid" 2>/dev/null; then
    kill -TERM -- "-$pgid" 2>/dev/null || true
    for _ in {1..40}; do
      if ! kill -0 -- "-$pgid" 2>/dev/null; then
        break
      fi
      sleep 0.25
    done
    if kill -0 -- "-$pgid" 2>/dev/null; then
      kill -KILL -- "-$pgid" 2>/dev/null || true
    fi
  fi
  [[ -z "$pgid" ]] || wait "$pgid" 2>/dev/null || true
  service_pgid=""
}

remove_browser_work_dir() {
  if [[ -z "$browser_work_dir" || ! -d "$browser_work_dir" ]]; then
    browser_work_dir=""
    return 0
  fi
  case "$browser_work_dir" in
    "$run_dir"/browser.*|"$windows_temp_wsl"/agentguard-e2e-"$$")
      find "$browser_work_dir" -depth -delete
      ;;
    *)
      fail "refusing unexpected browser cleanup path"
      ;;
  esac
  browser_work_dir=""
}

cleanup() {
  local status=$?
  set +e
  stop_services
  remove_browser_work_dir
  if ((status != 0)) && [[ -d "$run_dir" ]]; then
    printf 'RESULT=FAIL\n' >"$run_dir/result.txt"
  fi
  return "$status"
}
trap cleanup EXIT
trap 'exit 130' INT TERM

find_chrome() {
  local candidate
  if [[ -n "${AGENTGUARD_CHROME_BIN:-}" ]]; then
    [[ -x "$AGENTGUARD_CHROME_BIN" ]] || fail "AGENTGUARD_CHROME_BIN is not executable"
    printf '%s\n' "$AGENTGUARD_CHROME_BIN"
    return 0
  fi
  for candidate in google-chrome chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done
  candidate='/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
  [[ -x "$candidate" ]] || fail "Chrome not found; set AGENTGUARD_CHROME_BIN"
  printf '%s\n' "$candidate"
}

find_browser_node() {
  local candidate
  if [[ "$chrome_bin" == *.exe ]]; then
    candidate="${AGENTGUARD_WINDOWS_NODE:-/mnt/c/Program Files/nodejs/node.exe}"
    [[ -x "$candidate" ]] || fail "Windows Node not found; set AGENTGUARD_WINDOWS_NODE"
    printf '%s\n' "$candidate"
    return 0
  fi
  command -v node >/dev/null 2>&1 || fail "missing required command: node"
  command -v node
}

require_command curl
require_command jq
require_command ss
require_command setsid
require_command realpath
require_command install

demo_story="${AGENTGUARD_E2E_DEMO:-waf}"
[[ "$demo_story" == "waf" || "$demo_story" == "compliance" ]] || \
  fail "AGENTGUARD_E2E_DEMO must be waf or compliance"

evidence_root="$(realpath -m "$evidence_root")"
case "$evidence_root" in
  "$repo_root"|"$repo_root"/*) fail "evidence directory must be outside the repository" ;;
esac
umask 077
mkdir -p "$run_dir"

api_port="${AGENTGUARD_E2E_API_PORT:-$(choose_port 19000)}"
frontend_port="${AGENTGUARD_E2E_FRONTEND_PORT:-$(choose_port 15173)}"
validate_port "$api_port"
validate_port "$frontend_port"
[[ "$api_port" != "$frontend_port" ]] || fail "API and frontend ports must differ"

chrome_bin="$(find_chrome)"
browser_node="$(find_browser_node)"
browser_script="$repo_root/scripts/browser-e2e.mjs"
playwright_entry="$repo_root/frontend/node_modules/playwright-core/index.mjs"
[[ -f "$browser_script" ]] || fail "browser test script is missing"
[[ -f "$playwright_entry" ]] || fail "playwright-core is missing; run npm ci in frontend"

if [[ "$chrome_bin" == *.exe ]]; then
  require_command powershell.exe
  require_command wslpath
  windows_temp="$(powershell.exe -NoProfile -NonInteractive -Command '[System.IO.Path]::GetTempPath()' | tr -d '\r\n')"
  [[ -n "$windows_temp" ]] || fail "Windows temporary path unavailable"
  windows_temp_wsl="$(wslpath -u "$windows_temp")"
  browser_work_dir="$windows_temp_wsl/agentguard-e2e-$$"
  mkdir -p "$browser_work_dir/node_modules"
  install -m 600 "$browser_script" "$browser_work_dir/browser-e2e.mjs"
  cp -R "$repo_root/frontend/node_modules/playwright-core" \
    "$browser_work_dir/node_modules/playwright-core"
  browser_script_arg="$(wslpath -w "$browser_work_dir/browser-e2e.mjs")"
  chrome_arg="$(wslpath -w "$chrome_bin")"
  evidence_arg="$(wslpath -w "$run_dir")"
  playwright_arg="$(wslpath -w "$browser_work_dir/node_modules/playwright-core/index.mjs")"
else
  browser_script_arg="$browser_script"
  chrome_arg="$chrome_bin"
  evidence_arg="$run_dir"
  playwright_arg="$playwright_entry"
fi

app_url="http://localhost:$frontend_port"
api_url="http://localhost:$api_port"
printf 'AgentGuard browser E2E starting\n'
printf 'Frontend: %s\n' "$app_url"
printf 'Evidence: %s\n' "$run_dir"

setsid env \
  AGENTGUARD_MODE=synthetic \
  AGENTGUARD_DEMO="$demo_story" \
  AGENTGUARD_API_PORT="$api_port" \
  AGENTGUARD_FRONTEND_PORT="$frontend_port" \
  "$repo_root/scripts/run-local.sh" >"$run_dir/services.log" 2>&1 &
service_pgid=$!

wait_for_url "$api_url/api/health"
wait_for_url "$app_url/"

"$browser_node" \
  "$browser_script_arg" \
  "$app_url" \
  "$chrome_arg" \
  "$evidence_arg" \
  "$playwright_arg" \
  "$demo_story" >"$run_dir/playwright.log" 2>&1

jq -e --arg story "$demo_story" '
  (.result | startswith("PASS")) and
  .evidenceMode == "INTERACTIVE_PLAYWRIGHT" and
  .story == $story and
  (.uiActions | length) == 4 and
  (.apiAssertions | length) == 3 and
  (.domAssertions | length) == 2 and
  (.pageErrors | length) == 0 and
  (.requestFailures | length) == 0 and
  (.externalRequests | length) == 0 and
  (.screenshots | length) == (if $story == "compliance" then 6 else 3 end) and
  (.screenshotDetails | length) == (if $story == "compliance" then 6 else 3 end)
' "$run_dir/result.json" >/dev/null

if [[ "$demo_story" == "compliance" ]]; then
  for screenshot in \
    proposal-full proposal-slide \
    approval-valid-full approval-valid-slide \
    bypass-denied-full bypass-denied-slide; do
    [[ -s "$run_dir/$screenshot.png" ]] || fail "missing screenshot: $screenshot.png"
  done
  for suffix in full slide; do
    cmp -s "$run_dir/proposal-$suffix.png" "$run_dir/bypass-denied-$suffix.png" && \
      fail "proposal and bypass $suffix screenshots are identical"
    cmp -s "$run_dir/proposal-$suffix.png" "$run_dir/approval-valid-$suffix.png" && \
      fail "proposal and approval $suffix screenshots are identical"
    cmp -s "$run_dir/approval-valid-$suffix.png" "$run_dir/bypass-denied-$suffix.png" && \
      fail "approval and bypass $suffix screenshots are identical"
  done
else
  for screenshot in proposal approval-valid bypass-denied; do
    [[ -s "$run_dir/$screenshot.png" ]] || fail "missing screenshot: $screenshot.png"
  done
  cmp -s "$run_dir/proposal.png" "$run_dir/bypass-denied.png" && \
    fail "proposal and bypass screenshots are identical"
  cmp -s "$run_dir/proposal.png" "$run_dir/approval-valid.png" && \
    fail "proposal and approval screenshots are identical"
  cmp -s "$run_dir/approval-valid.png" "$run_dir/bypass-denied.png" && \
    fail "approval and bypass screenshots are identical"
fi

stop_services
wait_for_port_release "$api_port"
wait_for_port_release "$frontend_port"
remove_browser_work_dir

result="$(jq -r '.result' "$run_dir/result.json")"
console_error_count="$(jq '.consoleErrors | length' "$run_dir/result.json")"
http_error_count="$(jq '.httpErrors | length' "$run_dir/result.json")"
jq '.cleanup = {
  browser: "CLOSED",
  services: "STOPPED",
  ports: "RELEASED",
  temporaryFiles: "REMOVED"
}' "$run_dir/result.json" >"$run_dir/result.tmp"
mv "$run_dir/result.tmp" "$run_dir/result.json"

{
  printf 'RESULT=%s\n' "$result"
  printf 'MODE=synthetic-%s\n' "$demo_story"
  printf 'EVIDENCE_MODE=INTERACTIVE_PLAYWRIGHT\n'
  printf 'PLAYWRIGHT_CORE=PINNED_REPO_DEPENDENCY\n'
  printf 'UI_ACTIONS=4\n'
  printf 'API_ASSERTIONS=3\n'
  printf 'DOM_ASSERTIONS=2\n'
  printf 'CONSOLE_ERRORS=%s\n' "$console_error_count"
  printf 'HTTP_ERRORS=%s\n' "$http_error_count"
  printf 'PAGE_ERRORS=0\n'
  printf 'REQUEST_FAILURES=0\n'
  printf 'EXTERNAL_REQUESTS=0\n'
  if [[ "$demo_story" == "compliance" ]]; then
    printf 'PROPOSAL=APPROVAL_REQUIRED TWO_NON_COMPLIANT MUTATION_FALSE\n'
    printf 'APPROVAL=ALLOW APPROVAL_VALID TWO_COMPLIANT MUTATION_TRUE VERIFIED_TRUE\n'
    printf 'BYPASS=DENY HUMAN_APPROVAL_REQUIRED MUTATION_FALSE\n'
  else
    printf 'PROPOSAL=APPROVAL_REQUIRED COUNT_TO_BLOCK MUTATION_FALSE\n'
    printf 'APPROVAL=ALLOW APPROVAL_VALID COUNT_TO_BLOCK MUTATION_TRUE VERIFIED_TRUE\n'
    printf 'BYPASS=DENY HUMAN_APPROVAL_REQUIRED MUTATION_FALSE\n'
  fi
  printf 'CLEANUP=BROWSER_CLOSED SERVICES_STOPPED PORTS_RELEASED TEMPORARY_FILES_REMOVED\n'
} >"$run_dir/result.txt"

trap - EXIT INT TERM
printf '%s: proposal, approval, and bypass Playwright evidence captured\n' "$result"
printf 'Evidence: %s\n' "$run_dir"
