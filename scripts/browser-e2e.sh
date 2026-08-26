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

capture_screenshot() {
  local name=$1
  local output="$run_dir/$name.png"
  local browser_output=$output
  local browser_output_arg=$output
  local browser_profile_arg="$browser_work_dir/profile"

  if [[ "$chrome_bin" == *.exe ]]; then
    browser_output="$browser_work_dir/$name.png"
    browser_output_arg="$(wslpath -w "$browser_output")"
    browser_profile_arg="$(wslpath -w "$browser_work_dir/profile")"
  fi

  "$chrome_bin" \
    --headless \
    --disable-gpu \
    --hide-scrollbars \
    --no-first-run \
    "--user-data-dir=$browser_profile_arg" \
    --window-size=1920,1080 \
    --virtual-time-budget=3000 \
    "--screenshot=$browser_output_arg" \
    "$app_url" >>"$run_dir/chrome.log" 2>&1

  [[ -s "$browser_output" ]] || fail "browser did not create $name.png"
  if [[ "$browser_output" != "$output" ]]; then
    install -m 600 "$browser_output" "$output"
  fi
}

require_command curl
require_command jq
require_command ss
require_command setsid
require_command sha256sum
require_command realpath
require_command awk
require_command install

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
if [[ "$chrome_bin" == *.exe ]]; then
  require_command powershell.exe
  require_command wslpath
  windows_temp="$(powershell.exe -NoProfile -NonInteractive -Command '[System.IO.Path]::GetTempPath()' | tr -d '\r\n')"
  [[ -n "$windows_temp" ]] || fail "Windows temporary path unavailable"
  windows_temp_wsl="$(wslpath -u "$windows_temp")"
  browser_work_dir="$windows_temp_wsl/agentguard-e2e-$$"
  mkdir -p "$browser_work_dir/profile"
else
  browser_work_dir="$(mktemp -d "$run_dir/browser.XXXXXX")"
  mkdir -p "$browser_work_dir/profile"
fi

app_url="http://localhost:$frontend_port"
api_url="http://localhost:$api_port"
printf 'AgentGuard browser E2E starting\n'
printf 'Frontend: %s\n' "$app_url"
printf 'Evidence: %s\n' "$run_dir"

setsid env \
  AGENTGUARD_MODE=synthetic \
  AGENTGUARD_API_PORT="$api_port" \
  AGENTGUARD_FRONTEND_PORT="$frontend_port" \
  "$repo_root/scripts/run-local.sh" >"$run_dir/services.log" 2>&1 &
service_pgid=$!

wait_for_url "$api_url/api/health"
wait_for_url "$app_url/"

curl --fail --silent --show-error \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-AgentGuard-Intent: human-ui-v1' \
  --data '{}' \
  "$app_url/api/review" >"$run_dir/proposal.json"

jq -e '
  .environment == "synthetic" and
  .decision == "APPROVAL_REQUIRED" and
  .reason == "HUMAN_APPROVAL_REQUIRED" and
  .beforeAction == "COUNT" and
  .requestedAction == "BLOCK" and
  .actualAction == "COUNT" and
  .mutationPerformed == false
' "$run_dir/proposal.json" >/dev/null
capture_screenshot proposal

curl --fail --silent --show-error \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-AgentGuard-Intent: human-ui-v1' \
  --data '{}' \
  "$app_url/api/approve" >"$run_dir/approval-valid.json"

jq -e '
  .decision == "ALLOW" and
  .reason == "APPROVAL_VALID" and
  .beforeAction == "COUNT" and
  .requestedAction == "BLOCK" and
  .actualAction == "BLOCK" and
  .mutationPerformed == true and
  .verified == true and
  .audit == "RECORDED"
' "$run_dir/approval-valid.json" >/dev/null
capture_screenshot approval-valid

curl --fail --silent --show-error \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-AgentGuard-Intent: human-ui-v1' \
  --data '{}' \
  "$app_url/api/reset" >/dev/null

curl --fail --silent --show-error \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-AgentGuard-Intent: human-ui-v1' \
  --data '{}' \
  "$app_url/api/bypass" >"$run_dir/bypass.json"

jq -e '
  .decision == "DENY" and
  .reason == "HUMAN_APPROVAL_REQUIRED" and
  .actualAction == "COUNT" and
  .mutationPerformed == false and
  .verified == false
' "$run_dir/bypass.json" >/dev/null
capture_screenshot bypass-denied

cmp -s "$run_dir/proposal.png" "$run_dir/bypass-denied.png" && \
  fail "proposal and bypass screenshots are identical"
cmp -s "$run_dir/proposal.png" "$run_dir/approval-valid.png" && \
  fail "proposal and approval screenshots are identical"
cmp -s "$run_dir/approval-valid.png" "$run_dir/bypass-denied.png" && \
  fail "approval and bypass screenshots are identical"

stop_services
wait_for_port_release "$api_port"
wait_for_port_release "$frontend_port"
remove_browser_work_dir

proposal_sha="$(sha256sum "$run_dir/proposal.png" | awk '{print $1}')"
approval_sha="$(sha256sum "$run_dir/approval-valid.png" | awk '{print $1}')"
bypass_sha="$(sha256sum "$run_dir/bypass-denied.png" | awk '{print $1}')"
{
  printf 'RESULT=PASS\n'
  printf 'MODE=synthetic\n'
  printf 'PROPOSAL=APPROVAL_REQUIRED COUNT_TO_BLOCK MUTATION_FALSE\n'
  printf 'APPROVAL=ALLOW APPROVAL_VALID COUNT_TO_BLOCK MUTATION_TRUE VERIFIED_TRUE\n'
  printf 'BYPASS=DENY HUMAN_APPROVAL_REQUIRED MUTATION_FALSE\n'
  printf 'PROPOSAL_PNG_SHA256=%s\n' "$proposal_sha"
  printf 'APPROVAL_PNG_SHA256=%s\n' "$approval_sha"
  printf 'BYPASS_PNG_SHA256=%s\n' "$bypass_sha"
  printf 'CLEANUP=PORTS_RELEASED\n'
} >"$run_dir/result.txt"

trap - EXIT INT TERM
printf 'PASS: proposal, approval, and bypass browser evidence captured\n'
printf 'Evidence: %s\n' "$run_dir"
