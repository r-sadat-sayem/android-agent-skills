#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="$SCRIPT_DIR/../tools/psi-audit"

if [[ ! -d "$TOOL_DIR" ]]; then
  echo "PSI tool directory not found: $TOOL_DIR"
  exit 1
fi

if command -v gradle >/dev/null 2>&1; then
  GRADLE_CMD=(gradle)
elif [[ -x "$TOOL_DIR/gradlew" ]]; then
  GRADLE_CMD=("$TOOL_DIR/gradlew")
else
  echo "Gradle is required. Install gradle or add a gradle wrapper in $TOOL_DIR"
  exit 1
fi

ARGS=("$@")
if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Usage: $0 --src <path ...> [--format text|json]"
  exit 1
fi

(
  cd "$TOOL_DIR"
  "${GRADLE_CMD[@]}" --no-daemon run --args="${ARGS[*]}"
)
