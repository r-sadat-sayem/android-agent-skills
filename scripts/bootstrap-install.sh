#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Bootstrap installer for this skills repository.
Designed to run via: curl ... | bash

Usage:
  bootstrap-install.sh [options]

Options:
  --repo <git-url>                Repository clone URL (required)
  --ref <git-ref>                 Branch/tag/commit to checkout (default: main)
  --target <codex|claude|both>    Install target (default: both)
  --mode <copy|link>              Install mode (default: copy)
  --skill <name>                  Install one skill
  --all                           Install all skills
  --codex-dir <path>              Codex skills directory override
  --claude-dir <path>             Claude skills directory override
  -h, --help                      Show help

Examples:
  bootstrap-install.sh --repo https://github.com/acme/android-skills.git --skill xml-to-compose-architect
  bootstrap-install.sh --repo https://github.com/acme/android-skills.git --all --target codex
USAGE
}

REPO_URL=""
REF="main"
TARGET="both"
MODE="copy"
SKILL=""
INSTALL_ALL=0
CODEX_DIR=""
CLAUDE_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO_URL="${2:-}"; shift 2 ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --skill) SKILL="${2:-}"; shift 2 ;;
    --all) INSTALL_ALL=1; shift ;;
    --codex-dir) CODEX_DIR="${2:-}"; shift 2 ;;
    --claude-dir) CLAUDE_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$REPO_URL" ]]; then
  echo "--repo is required"
  usage
  exit 1
fi

if [[ $INSTALL_ALL -eq 1 && -n "$SKILL" ]]; then
  echo "Use either --all or --skill, not both."
  exit 1
fi

if [[ $INSTALL_ALL -eq 0 && -z "$SKILL" ]]; then
  echo "Provide --skill <name> or --all."
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required for bootstrap install."
  exit 1
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

git clone --depth 1 --branch "$REF" "$REPO_URL" "$TMP_DIR/repo"

cd "$TMP_DIR/repo"

cmd=(./scripts/install-skill.sh --target "$TARGET" --mode "$MODE")
if [[ $INSTALL_ALL -eq 1 ]]; then
  cmd+=(--all)
else
  cmd+=(--skill "$SKILL")
fi

if [[ -n "$CODEX_DIR" ]]; then
  cmd+=(--codex-dir "$CODEX_DIR")
fi

if [[ -n "$CLAUDE_DIR" ]]; then
  cmd+=(--claude-dir "$CLAUDE_DIR")
fi

"${cmd[@]}"

# Write .skill-source record into each installed skill directory so update-skill.sh
# knows where to pull from later.
write_source_record() {
  local base_dir="$1"
  local skill_name="$2"
  local dst="${base_dir}/${skill_name}"
  if [[ -d "$dst" && ! -L "$dst" ]]; then
    cat > "${dst}/.skill-source" <<RECORD
repo=${REPO_URL}
ref=${REF}
installed_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RECORD
  fi
}

if [[ $INSTALL_ALL -eq 1 ]]; then
  while IFS= read -r skill_dir; do
    sname="$(basename "$skill_dir")"
    [[ "$TARGET" == "both" || "$TARGET" == "claude" ]] && write_source_record "${CLAUDE_DIR:-${HOME}/.claude/skills}" "$sname"
    [[ "$TARGET" == "both" || "$TARGET" == "codex"  ]] && write_source_record "${CODEX_DIR:-${HOME}/.codex/skills}"  "$sname"
  done < <(find "$TMP_DIR/repo/skills" -mindepth 1 -maxdepth 1 -type d | sort)
else
  [[ "$TARGET" == "both" || "$TARGET" == "claude" ]] && write_source_record "${CLAUDE_DIR:-${HOME}/.claude/skills}" "$SKILL"
  [[ "$TARGET" == "both" || "$TARGET" == "codex"  ]] && write_source_record "${CODEX_DIR:-${HOME}/.codex/skills}"  "$SKILL"
fi

