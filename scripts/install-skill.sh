#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install one or more skills from this repository into Codex, Claude, or both.

Usage:
  install-skill.sh [options]

Options:
  --target <codex|claude|both>   Install target (default: both)
  --mode <copy|link>             Install mode (default: copy)
  --skill <name>                 Install one skill by folder name under skills/
  --all                          Install all skills under skills/
  --name <installed-name>        Override installed name (only valid with --skill)
  --codex-dir <path>             Base Codex skills directory (default: ~/.codex/skills)
  --claude-dir <path>            Base Claude skills directory (default: ~/.claude/skills)
  -h, --help                     Show this help

Examples:
  ./scripts/install-skill.sh --skill xml-to-compose-architect
  ./scripts/install-skill.sh --all --target codex
  ./scripts/install-skill.sh --skill xml-to-compose-architect --mode link
USAGE
}

TARGET="both"
MODE="copy"
SELECTED_SKILL=""
INSTALL_ALL=0
OVERRIDE_NAME=""
CODEX_BASE="${HOME}/.codex/skills"
CLAUDE_BASE="${HOME}/.claude/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --mode) MODE="${2:-}"; shift 2 ;;
    --skill) SELECTED_SKILL="${2:-}"; shift 2 ;;
    --all) INSTALL_ALL=1; shift ;;
    --name) OVERRIDE_NAME="${2:-}"; shift 2 ;;
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

if [[ "$MODE" != "copy" && "$MODE" != "link" ]]; then
  echo "Invalid --mode: $MODE"
  exit 1
fi

if [[ $INSTALL_ALL -eq 1 && -n "$SELECTED_SKILL" ]]; then
  echo "Use either --all or --skill, not both."
  exit 1
fi

if [[ $INSTALL_ALL -eq 0 && -z "$SELECTED_SKILL" ]]; then
  echo "Provide --skill <name> or --all"
  exit 1
fi

if [[ -n "$OVERRIDE_NAME" && $INSTALL_ALL -eq 1 ]]; then
  echo "--name can only be used with --skill"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "skills/ directory not found in repo root: $REPO_ROOT"
  exit 1
fi

install_one_target() {
  local base_dir="$1"
  local target_label="$2"
  local skill_name="$3"
  local src_dir="$4"
  local installed_name="$5"
  local dst="${base_dir}/${installed_name}"

  mkdir -p "$base_dir"
  rm -rf "$dst"

  if [[ "$MODE" == "link" ]]; then
    ln -s "$src_dir" "$dst"
  else
    mkdir -p "$dst"
    rsync -a \
      --exclude ".DS_Store" \
      --exclude ".git" \
      "${src_dir}/" "${dst}/"
  fi

  echo "[ok] ${target_label}: ${skill_name} -> ${dst}"
}

install_skill() {
  local skill_name="$1"
  local src_dir="${SKILLS_DIR}/${skill_name}"

  if [[ ! -d "$src_dir" ]]; then
    echo "Skill not found: ${skill_name}"
    return 1
  fi

  if [[ ! -f "${src_dir}/SKILL.md" ]]; then
    echo "Skipping ${skill_name}: missing SKILL.md"
    return 0
  fi

  local installed_name="$skill_name"
  if [[ -n "$OVERRIDE_NAME" ]]; then
    installed_name="$OVERRIDE_NAME"
  fi

  if [[ "$TARGET" == "codex" || "$TARGET" == "both" ]]; then
    install_one_target "$CODEX_BASE" "Codex" "$skill_name" "$src_dir" "$installed_name"
  fi

  if [[ "$TARGET" == "claude" || "$TARGET" == "both" ]]; then
    install_one_target "$CLAUDE_BASE" "Claude" "$skill_name" "$src_dir" "$installed_name"
  fi
}

if [[ $INSTALL_ALL -eq 1 ]]; then
  found_any=0
  while IFS= read -r skill_dir; do
    skill_name="$(basename "$skill_dir")"
    found_any=1
    install_skill "$skill_name"
  done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

  if [[ $found_any -eq 0 ]]; then
    echo "No skills found under ${SKILLS_DIR}"
    exit 1
  fi
else
  install_skill "$SELECTED_SKILL"
fi

echo
echo "Install complete. Mode: ${MODE}, target: ${TARGET}"
