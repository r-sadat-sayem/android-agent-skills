#!/usr/bin/env bash
# update-skill.sh — pull latest skill content from GitHub and reinstall.
#
# Works whether the skill was installed via:
#   (a) bootstrap-install.sh  → install record at ~/.claude/skills/<name>/.skill-source
#   (b) install-skill.sh      → local repo; update = git pull + reinstall
#   (c) --mode link            → nothing to do (symlink already points at live source)
#
# Usage:
#   update-skill.sh --skill android-adaptive-ui
#   update-skill.sh --all
#   update-skill.sh --skill android-adaptive-ui --target claude
#   update-skill.sh --skill android-adaptive-ui --ref v1.2.0
#   update-skill.sh --check                          (dry-run: show installed vs remote version)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"

TARGET="both"
SELECTED_SKILL=""
UPDATE_ALL=0
REF="main"
CHECK_ONLY=0
CODEX_BASE="${HOME}/.codex/skills"
CLAUDE_BASE="${HOME}/.claude/skills"

usage() {
  cat <<'USAGE'
Update installed skills to the latest version from their source.

Usage:
  update-skill.sh [options]

Options:
  --skill <name>               Update one skill by name
  --all                        Update all installed skills
  --target <codex|claude|both> Which install to update (default: both)
  --ref <branch|tag|commit>    Git ref to pull (default: main)
  --check                      Show installed vs remote version without updating
  --codex-dir <path>           Override Codex skills base directory
  --claude-dir <path>          Override Claude skills base directory
  -h, --help                   Show this help

How it works:
  Each skill installed via bootstrap-install.sh writes a .skill-source file
  recording the GitHub URL, ref, and install date. update-skill.sh reads that
  file to know where to pull from, then re-runs the install over the existing
  directory (overwriting changed files, preserving nothing local).

  If the skill was installed via install-skill.sh (local repo), update is a
  git pull on this repo followed by reinstall.

  If the skill was installed with --mode link, the symlink already points at
  the live source — this script exits early with a reminder.

Examples:
  # Update one skill (auto-detects source from .skill-source):
  ./scripts/update-skill.sh --skill android-adaptive-ui

  # Update all skills:
  ./scripts/update-skill.sh --all

  # Only update the Claude install, not Codex:
  ./scripts/update-skill.sh --skill android-adaptive-ui --target claude

  # Pull a specific tag instead of main:
  ./scripts/update-skill.sh --skill android-adaptive-ui --ref v1.2.0

  # Check what version is installed vs what's on main without changing anything:
  ./scripts/update-skill.sh --check --skill android-adaptive-ui
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)      SELECTED_SKILL="${2:-}"; shift 2 ;;
    --all)        UPDATE_ALL=1; shift ;;
    --target)     TARGET="${2:-}"; shift 2 ;;
    --ref)        REF="${2:-}"; shift 2 ;;
    --check)      CHECK_ONLY=1; shift ;;
    --codex-dir)  CODEX_BASE="${2:-}"; shift 2 ;;
    --claude-dir) CLAUDE_BASE="${2:-}"; shift 2 ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ "$TARGET" != "codex" && "$TARGET" != "claude" && "$TARGET" != "both" ]]; then
  echo "Invalid --target: $TARGET"; exit 1
fi

if [[ $UPDATE_ALL -eq 1 && -n "$SELECTED_SKILL" ]]; then
  echo "Use either --all or --skill, not both."; exit 1
fi

if [[ $UPDATE_ALL -eq 0 && -z "$SELECTED_SKILL" && $CHECK_ONLY -eq 0 ]]; then
  echo "Provide --skill <name> or --all"; usage; exit 1
fi

# ── helpers ──────────────────────────────────────────────────────────────────

read_installed_version() {
  local dir="$1"
  local vfile="${dir}/VERSION"
  if [[ -f "$vfile" ]]; then
    tr -d '[:space:]' < "$vfile"
  else
    echo "(no VERSION file)"
  fi
}

read_skill_source() {
  # Returns the repo URL from .skill-source, or empty string if not found.
  local dir="$1"
  local src="${dir}/.skill-source"
  if [[ -f "$src" ]]; then
    grep '^repo=' "$src" | cut -d= -f2-
  else
    echo ""
  fi
}

is_symlink() {
  [[ -L "$1" ]]
}

check_remote_version() {
  local repo_url="$1"
  local ref="$2"
  local skill="$3"
  # Try to fetch VERSION file from GitHub raw URL (works for github.com repos)
  local raw_url
  raw_url="$(echo "$repo_url" | sed 's|\.git$||')"
  raw_url="${raw_url/github.com/raw.githubusercontent.com}/${ref}/skills/${skill}/VERSION"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --max-time 5 "$raw_url" 2>/dev/null | tr -d '[:space:]' || echo "(fetch failed)"
  else
    echo "(curl not available)"
  fi
}

update_one_skill() {
  local skill_name="$1"
  local bases=()
  [[ "$TARGET" == "claude" || "$TARGET" == "both" ]] && bases+=("$CLAUDE_BASE")
  [[ "$TARGET" == "codex" || "$TARGET" == "both" ]] && bases+=("$CODEX_BASE")

  local found_any=0

  for base in "${bases[@]}"; do
    local dst="${base}/${skill_name}"
    local target_label
    [[ "$base" == "$CLAUDE_BASE" ]] && target_label="Claude" || target_label="Codex"

    if [[ ! -d "$dst" ]]; then
      echo "[skip] ${target_label}/${skill_name}: not installed at ${dst}"
      continue
    fi

    found_any=1

    # Symlink install — nothing to do
    if is_symlink "$dst"; then
      echo "[link] ${target_label}/${skill_name}: symlink install — source is live at $(readlink "$dst")"
      continue
    fi

    local installed_ver
    installed_ver="$(read_installed_version "$dst")"
    local source_url
    source_url="$(read_skill_source "$dst")"

    if [[ $CHECK_ONLY -eq 1 ]]; then
      local remote_ver="(local repo)"
      if [[ -n "$source_url" ]]; then
        remote_ver="$(check_remote_version "$source_url" "$REF" "$skill_name")"
      fi
      printf "%-10s  %-20s  installed=%-12s  remote=%s\n" \
        "$target_label" "$skill_name" "$installed_ver" "$remote_ver"
      continue
    fi

    # --- Do the update ---
    echo ""
    echo "Updating ${target_label}/${skill_name} (installed: ${installed_ver})"

    if [[ -n "$source_url" ]]; then
      # Installed via bootstrap — re-clone and re-install from recorded URL
      echo "  Source : ${source_url} @ ${REF}"
      TMP_DIR="$(mktemp -d)"
      trap 'rm -rf "$TMP_DIR"' EXIT

      git clone --depth 1 --branch "$REF" "$source_url" "${TMP_DIR}/repo" --quiet

      local src_skill_dir="${TMP_DIR}/repo/skills/${skill_name}"
      if [[ ! -d "$src_skill_dir" ]]; then
        echo "  ERROR: skill '${skill_name}' not found in remote repo at ref '${REF}'"
        rm -rf "$TMP_DIR"
        continue
      fi

      # Overwrite install dir, preserve .skill-source (record stays valid)
      rsync -a \
        --exclude ".DS_Store" \
        --exclude ".git" \
        --exclude ".skill-source" \
        "${src_skill_dir}/" "${dst}/"

      # Update the .skill-source record with new ref + timestamp
      cat > "${dst}/.skill-source" <<SOURCE
repo=${source_url}
ref=${REF}
updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SOURCE

      local new_ver
      new_ver="$(read_installed_version "$dst")"
      echo "  [ok] ${target_label}/${skill_name}: ${installed_ver} → ${new_ver}"
      rm -rf "$TMP_DIR"
      trap - EXIT

    else
      # Installed from local repo — git pull this repo, then re-copy
      echo "  Source : local repo (${REPO_ROOT})"
      local local_src="${SKILLS_DIR}/${skill_name}"

      if [[ ! -d "$local_src" ]]; then
        echo "  ERROR: local source not found at ${local_src}"
        continue
      fi

      # Pull the repo
      (cd "$REPO_ROOT" && git pull --ff-only --quiet)

      rsync -a \
        --exclude ".DS_Store" \
        --exclude ".git" \
        --exclude ".skill-source" \
        "${local_src}/" "${dst}/"

      local new_ver
      new_ver="$(read_installed_version "$dst")"
      echo "  [ok] ${target_label}/${skill_name}: ${installed_ver} → ${new_ver}"
    fi
  done

  if [[ $found_any -eq 0 && $CHECK_ONLY -eq 0 ]]; then
    echo "[warn] ${skill_name}: not installed in any target (checked: ${bases[*]:-none})"
    echo "       To install: ./scripts/install-skill.sh --skill ${skill_name}"
  fi
}

# ── main ─────────────────────────────────────────────────────────────────────

if [[ $UPDATE_ALL -eq 1 ]]; then
  # Discover all skills that exist in at least one install target
  declare -A seen=()
  for base in "$CLAUDE_BASE" "$CODEX_BASE"; do
    if [[ -d "$base" ]]; then
      while IFS= read -r dir; do
        name="$(basename "$dir")"
        seen["$name"]=1
      done < <(find "$base" -mindepth 1 -maxdepth 1 -type d -o -type l 2>/dev/null || true)
    fi
  done

  if [[ ${#seen[@]} -eq 0 ]]; then
    echo "No skills found in ${CLAUDE_BASE} or ${CODEX_BASE}"
    exit 0
  fi

  for skill_name in $(echo "${!seen[@]}" | tr ' ' '\n' | sort); do
    update_one_skill "$skill_name"
  done
else
  update_one_skill "$SELECTED_SKILL"
fi

if [[ $CHECK_ONLY -eq 0 ]]; then
  echo ""
  echo "Update complete."
fi
