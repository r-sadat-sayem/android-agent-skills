#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uninstall one or more skills from Codex, Claude, or both.

Usage:
  uninstall-skill.sh [options]

Options:
  --target <codex|claude|both>   Uninstall target (default: both)
  --skill <name>                 Uninstall one skill by installed folder name
  --all                          Uninstall all installed skills from this repo's skills/ names
  --codex-dir <path>             Base Codex skills directory (default: ~/.codex/skills)
  --claude-dir <path>            Base Claude skills directory (default: ~/.claude/skills)
  -h, --help                     Show this help
USAGE
}

TARGET="both"
SELECTED_SKILL=""
REMOVE_ALL=0
CODEX_BASE="${HOME}/.codex/skills"
CLAUDE_BASE="${HOME}/.claude/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --skill) SELECTED_SKILL="${2:-}"; shift 2 ;;
    --all) REMOVE_ALL=1; shift ;;
    --codex-dir) CODEX_BASE="${2:-}"; shift 2 ;;
    --claude-dir) CLAUDE_BASE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ "$TARGET" != "codex" && "$TARGET" != "claude" && "$TARGET" != "both" ]]; then
  echo "Invalid --target: $TARGET"
  exit 1
fi

if [[ $REMOVE_ALL -eq 1 && -n "$SELECTED_SKILL" ]]; then
  echo "Use either --all or --skill, not both."
  exit 1
fi

if [[ $REMOVE_ALL -eq 0 && -z "$SELECTED_SKILL" ]]; then
  echo "Provide --skill <name> or --all"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"

remove_one_target() {
  local base_dir="$1"
  local target_label="$2"
  local installed_name="$3"
  local dst="${base_dir}/${installed_name}"

  if [[ -e "$dst" ]]; then
    rm -rf "$dst"
    echo "[ok] removed ${target_label}: ${dst}"
  else
    echo "[skip] not found ${target_label}: ${dst}"
  fi
}

remove_skill() {
  local skill_name="$1"

  if [[ "$TARGET" == "codex" || "$TARGET" == "both" ]]; then
    remove_one_target "$CODEX_BASE" "Codex" "$skill_name"
  fi

  if [[ "$TARGET" == "claude" || "$TARGET" == "both" ]]; then
    remove_one_target "$CLAUDE_BASE" "Claude" "$skill_name"
  fi
}

if [[ $REMOVE_ALL -eq 1 ]]; then
  if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "skills/ directory not found in repo root: $REPO_ROOT"
    exit 1
  fi

  found_any=0
  while IFS= read -r skill_dir; do
    found_any=1
    remove_skill "$(basename "$skill_dir")"
  done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

  if [[ $found_any -eq 0 ]]; then
    echo "No skill directories found under ${SKILLS_DIR}"
    exit 1
  fi
else
  remove_skill "$SELECTED_SKILL"
fi
