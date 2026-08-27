#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source_path="$repo_root/docs/demo-compliance.md"
output_path="$repo_root/docs/presentation/compliance-guard-director.pptx"
evidence_root="${AGENTGUARD_PRESENTATION_EVIDENCE_DIR:-${HOME}/.AGENTS-temp/agentguard/presentation}"
run_dir="$evidence_root/run-$(date +%Y%m%d-%H%M%S)-$$"
preview_dir="$run_dir/previews"
validation_path="$run_dir/validation.json"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

command -v powershell.exe >/dev/null 2>&1 || fail "powershell.exe is required"
command -v wslpath >/dev/null 2>&1 || fail "wslpath is required"
command -v jq >/dev/null 2>&1 || fail "jq is required"
[[ -f "$source_path" ]] || fail "source deck is missing"

case "$evidence_root" in
  "$repo_root"|"$repo_root"/*) fail "evidence directory must be outside the repository" ;;
esac

umask 077
mkdir -p "$run_dir" "$preview_dir" "$(dirname -- "$output_path")"

script_win="$(wslpath -w "$repo_root/scripts/build-presentation.ps1")"
source_win="$(wslpath -w "$source_path")"
output_win="$(wslpath -w "$output_path")"
preview_win="$(wslpath -w "$preview_dir")"
validation_win="$(wslpath -w "$validation_path")"

powershell.exe \
  -NoProfile \
  -NonInteractive \
  -ExecutionPolicy Bypass \
  -File "$script_win" \
  -SourcePath "$source_win" \
  -OutputPath "$output_win" \
  -PreviewDir "$preview_win" \
  -ValidationPath "$validation_win" \
  >"$run_dir/powerpoint.log" 2>&1

[[ -s "$output_path" ]] || fail "PowerPoint output is missing"
[[ -s "$validation_path" ]] || fail "validation result is missing"
jq -e '
  .result == "PASS" and
  .slideCount == 9 and
  .slideSize == "16:9" and
  .editableTextShapes >= 25 and
  .pictureShapes == 3 and
  .speakerNoteSlides == 9 and
  .metadataSanitized == true and
  .previewCount == 9
' "$validation_path" >/dev/null

printf 'PASS: native editable Compliance Guard PPTX generated and reopened\n'
printf 'PPTX: %s\n' "$output_path"
printf 'Evidence: %s\n' "$run_dir"
