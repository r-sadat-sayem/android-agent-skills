#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <src-root-or-file>"
  exit 1
fi

TARGET="$1"

if [[ ! -e "$TARGET" ]]; then
  echo "Path not found: $TARGET"
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "Error: ripgrep (rg) is required"
  exit 1
fi

failures=0

echo "VALIDATE FIXES"
echo "Target: $TARGET"

echo
printf "[1] Deprecated WindowSizeClass API... "
if rg -n --pcre2 --glob '*.kt' --glob '!**/assets/**' '^(?!\s*//).*calculateWindowSizeClass\s*\(' "$TARGET" >/tmp/adaptive-ui-api-check.txt; then
  echo "FAIL"
  cat /tmp/adaptive-ui-api-check.txt
  failures=$((failures + 1))
else
  echo "PASS"
fi

echo
printf "[2] Legacy nav components (BottomNavigation/NavigationBar)... "
if rg -n --pcre2 --glob '*.kt' --glob '!**/assets/**' '^(?!\s*//).*\b(BottomNavigation|NavigationBar)\s*\(' "$TARGET" >/tmp/adaptive-ui-nav-check.txt; then
  echo "FAIL"
  cat /tmp/adaptive-ui-nav-check.txt
  failures=$((failures + 1))
else
  echo "PASS"
fi

echo
printf "[3] Manifest orientation locks... "
if rg -n --glob '*.xml' 'android:screenOrientation\s*=\s*"(portrait|landscape|reverseLandscape|reversePortrait|sensorLandscape|sensorPortrait|userLandscape|userPortrait|locked)"' "$TARGET" >/tmp/adaptive-ui-orientation-check.txt; then
  echo "FAIL"
  cat /tmp/adaptive-ui-orientation-check.txt
  failures=$((failures + 1))
else
  echo "PASS"
fi

echo
printf "[4] Adaptive API usage without @OptIn... "
missing_optin=0
while IFS= read -r file; do
  if ! rg -q '@file:OptIn\([^)]*ExperimentalMaterial3AdaptiveApi::class|@OptIn\([^)]*ExperimentalMaterial3AdaptiveApi::class' "$file"; then
    if [[ $missing_optin -eq 0 ]]; then
      echo "FAIL"
    fi
    echo "$file"
    missing_optin=1
  fi
done < <(rg -l --glob '*.kt' --glob '!**/assets/**' 'ListDetailPaneScaffold|SupportingPaneScaffold|NavigableListDetailPaneScaffold|NavigableSupportingPaneScaffold|AdaptiveNavigationSuite|currentWindowAdaptiveInfo\s*\(' "$TARGET")

if [[ $missing_optin -eq 0 ]]; then
  echo "PASS"
else
  failures=$((failures + 1))
fi

echo
if [[ $failures -eq 0 ]]; then
  echo "Validation passed: no known bad patterns found."
  exit 0
fi

echo "Validation failed: $failures check(s) failed."
exit 2
