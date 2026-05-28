#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Verify an Android project build using that project's own Gradle settings.

Usage:
  verify_project_build.sh [options]

Options:
  --project-dir <path>   Android project root (default: current directory)
  --module <name>        Module to verify (default: app)
  --task <task>          Full Gradle task to run (overrides --module)
  --clean                Run clean before verify task
  -h, --help             Show help

Examples:
  ./scripts/verify_project_build.sh --project-dir /path/to/project
  ./scripts/verify_project_build.sh --project-dir . --module app
  ./scripts/verify_project_build.sh --project-dir . --task :app:assembleRelease
USAGE
}

PROJECT_DIR="$(pwd)"
MODULE="app"
TASK=""
RUN_CLEAN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir) PROJECT_DIR="${2:-}"; shift 2 ;;
    --module) MODULE="${2:-}"; shift 2 ;;
    --task) TASK="${2:-}"; shift 2 ;;
    --clean) RUN_CLEAN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Project directory not found: $PROJECT_DIR"
  exit 1
fi

if [[ -z "$TASK" ]]; then
  TASK=":${MODULE}:assembleDebug"
fi

if [[ -x "$PROJECT_DIR/gradlew" ]]; then
  GRADLE_CMD=("$PROJECT_DIR/gradlew")
elif command -v gradle >/dev/null 2>&1; then
  GRADLE_CMD=(gradle)
else
  echo "Gradle not found. Add a gradlew wrapper in the project or install gradle."
  exit 1
fi

echo "VERIFY PROJECT BUILD"
echo "Project: $PROJECT_DIR"
echo "Task   : $TASK"

declare -a run_args
run_args=(--no-daemon)
if [[ $RUN_CLEAN -eq 1 ]]; then
  run_args+=(clean)
fi
run_args+=("$TASK")

(
  cd "$PROJECT_DIR"
  "${GRADLE_CMD[@]}" "${run_args[@]}"
)

echo "Verification completed successfully."
