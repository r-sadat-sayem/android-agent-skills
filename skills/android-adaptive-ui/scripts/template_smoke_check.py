#!/usr/bin/env python3
"""
Template smoke checks for android-adaptive-ui.

This is a lightweight CI/local guard for paste-ready templates.
It does static checks that catch compile-breaking patterns seen in reviews.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


INVALID_INT_DP_EXTENSION = re.compile(r"private\s+val\s+Int\.dp\s+get\(\)\s*=")
DP_LITERAL_USAGE = re.compile(r"\b\d+\.dp\b")
DP_IMPORT = re.compile(r"import\s+androidx\.compose\.ui\.unit\.dp\b")


def check_template(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path}: could not read file ({e})"]

    violations: list[str] = []

    if INVALID_INT_DP_EXTENSION.search(content):
        violations.append(
            f"{path}: invalid custom Int.dp extension. Use androidx.compose.ui.unit.dp import instead."
        )

    if DP_LITERAL_USAGE.search(content) and not DP_IMPORT.search(content):
        violations.append(
            f"{path}: uses numeric .dp literals but missing `import androidx.compose.ui.unit.dp`."
        )

    return violations


def collect_targets(root: Path) -> list[Path]:
    return sorted(root.glob("*.kt"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-check Wear templates for compile-safety pitfalls.")
    parser.add_argument(
        "--wear-dir",
        default=str(Path(__file__).resolve().parents[1] / "templates" / "wear"),
        help="Directory containing Wear .kt templates.",
    )
    args = parser.parse_args()

    wear_dir = Path(args.wear_dir).resolve()
    if not wear_dir.is_dir():
        print(f"Error: wear template directory not found: {wear_dir}", file=sys.stderr)
        sys.exit(2)

    files = collect_targets(wear_dir)
    if not files:
        print(f"Error: no .kt files found in {wear_dir}", file=sys.stderr)
        sys.exit(2)

    violations: list[str] = []
    for file_path in files:
        violations.extend(check_template(file_path))

    if violations:
        print("TEMPLATE SMOKE CHECK FAILED")
        for violation in violations:
            print(f"- {violation}")
        sys.exit(1)

    print(f"TEMPLATE SMOKE CHECK PASSED ({len(files)} file(s))")
    sys.exit(0)


if __name__ == "__main__":
    main()
