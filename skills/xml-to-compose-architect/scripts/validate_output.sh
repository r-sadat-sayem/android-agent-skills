#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <analysis-report.md>"
  exit 1
fi

FILE="$1"

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE"
  exit 1
fi

required_sections=(
  "## 1) Clarifying Questions"
  "## 3) Architecture Options"
  "## 4) Recommendation"
  "## 6) State Hoisting Plan"
  "## 8) Performance and Recomposition Plan"
)

missing=0
for section in "${required_sections[@]}"; do
  if ! grep -Fq "$section" "$FILE"; then
    echo "Missing section: $section"
    missing=1
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo "Validation failed."
  exit 2
fi

echo "Validation passed: required sections found."

