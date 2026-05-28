#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_ROOT="$SCRIPT_DIR/../fixtures/projects"

if [[ ! -d "$FIXTURE_ROOT" ]]; then
  echo "Fixture root not found: $FIXTURE_ROOT"
  exit 1
fi

if command -v gradle >/dev/null 2>&1; then
  GRADLE_CMD=(gradle)
else
  echo "Gradle is required to compile fixture projects"
  exit 1
fi

failures=0
for project in "$FIXTURE_ROOT"/*; do
  [[ -d "$project" ]] || continue
  echo "==> compiling fixture: $(basename "$project")"
  (
    cd "$project"
    "${GRADLE_CMD[@]}" --no-daemon :app:assembleDebug
  ) || failures=$((failures + 1))
  echo

done

if [[ $failures -gt 0 ]]; then
  echo "Fixture compile failed in $failures project(s)"
  exit 2
fi

echo "All fixture projects compiled successfully"
