#!/usr/bin/env python3
"""
Android Adaptive UI Audit Script
Scans Android UI files for device-fragmentation issues.

Only reads files that are identified as UI files via a cheap header scan
(first 4 KB) — data classes, repositories, network layers are skipped entirely.

Usage:
    # Directory
    python layout_audit.py --src /project/app/src/main

    # Single file
    python layout_audit.py --src /project/app/src/main/java/HomeScreen.kt

    # Multiple files and/or directories (mixed)
    python layout_audit.py --src /project/app/src/main/java/ui/ /project/app/src/main/res/layout/activity_main.xml

    # With memory cache and JSON output
    python layout_audit.py --src /project/app/src/main --memory /project/.adaptive-ui-memory.json --format json

Exit codes:
    0  No CRITICAL findings
    1  One or more CRITICAL findings found
    2  Bad arguments or invalid path
"""

import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Literal, Optional


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass
class Finding:
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    category: str
    file: str
    line: int
    message: str
    fix: str
    template_ref: Optional[str] = None


@dataclass
class AuditResult:
    findings: list[Finding] = field(default_factory=list)
    scanned_kt: int = 0
    scanned_xml: int = 0
    skipped_cached: int = 0
    skipped_non_ui: int = 0
    detected_form_factors: list[str] = field(default_factory=list)
    memory_path: Optional[str] = None

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "CRITICAL")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARNING")

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "INFO")


# ─── UI file detection (header scan) ─────────────────────────────────────────
# Read only the first 4 KB to decide whether a file is UI-relevant.
# This avoids loading data classes, repositories, network layers, etc.

_HEADER_BYTES = 4096

# Kotlin UI signals: Compose annotations, UI imports, Activity/Fragment base classes
_UI_SIGNALS_KT = re.compile(
    r'@Composable'
    r'|@Preview'
    r'|import\s+androidx\.compose\.'
    r'|import\s+androidx\.wear\.compose\.'
    r'|import\s+androidx\.car\.app\.'
    r'|import\s+androidx\.window\.'           # foldable WindowInfoTracker
    r'|import\s+androidx\.activity\.compose\.'
    r'|:\s*(Activity|AppCompatActivity|ComponentActivity|Fragment)\s*[({]'
    r'|setContent\s*\{'
    r'|WindowSizeClass'
    r'|FoldingFeature'
    r'|CarAppService'
)

# XML UI signals: layout root elements or resource directory name
_UI_SIGNALS_XML = re.compile(
    r'<(LinearLayout|ConstraintLayout|RelativeLayout|FrameLayout'
    r'|ScrollView|HorizontalScrollView|CoordinatorLayout'
    r'|merge|include|ViewGroup|androidx\.)'
)

# XML directories that are always UI-relevant
_UI_XML_DIR_PARTS = {"layout", "menu", "navigation", "drawable", "xml"}


def _read_header(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return f.read(_HEADER_BYTES).decode("utf-8", errors="replace")
    except OSError:
        return ""


def is_ui_kt_file(path: str) -> bool:
    """Returns True when the .kt file is likely a UI file based on its first 4 KB."""
    return bool(_UI_SIGNALS_KT.search(_read_header(path)))


def is_ui_xml_file(path: str) -> bool:
    """Returns True for AndroidManifest.xml, layout dirs, or XML with layout root elements."""
    basename = os.path.basename(path)
    if basename == "AndroidManifest.xml":
        return True
    # Check directory components for known UI resource dirs
    norm = path.replace("\\", "/")
    parts = norm.split("/")
    if any(part in _UI_XML_DIR_PARTS or part.startswith("layout") for part in parts):
        return True
    return bool(_UI_SIGNALS_XML.search(_read_header(path)))


# ─── Memory store (JSON-LD) ───────────────────────────────────────────────────

_MEMORY_CONTEXT = {
    "@vocab": "https://schema.adaptive-android.dev/audit/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "schema": "https://schema.org/",
    "fileHash": {"@type": "xsd:string"},
    "lastAudited": {"@type": "xsd:dateTime"},
    "findings": {"@container": "@list"},
    "formFactors": {"@container": "@set"},
}

_MEMORY_VERSION = "1"


def _file_hash(path: str) -> str:
    h = hashlib.sha1()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


class MemoryStore:
    """
    Persistent JSON-LD knowledgebase at .adaptive-ui-memory.json.
    Tracks per-file audit state (SHA-1 hash + findings) so clean, unchanged
    files are skipped on subsequent runs. Accumulates a project-level knowledge
    graph of form factors, open issues, and resolved findings across sessions.

    Schema (JSON-LD):
      @context        — vocab anchored to adaptive-android.dev
      @type           — AdaptiveUIAuditGraph
      @id             — file:// URI of this memory file
      version         — schema version (bump on breaking changes)
      project         — { @id: file:// URI of src root, name: last path component }
      lastRun         — ISO-8601 timestamp of most recent audit
      formFactors     — accumulated set of detected track names
      files           — relativePath → FileAuditNode
        FileAuditNode:
          @type         FileAuditNode
          @id           file:// URI
          fileHash      SHA-1
          lastAudited   ISO-8601
          clean         true = no CRITICAL/WARNING last run
          findings      list of Finding dicts
      resolvedFindings — audit trail of developer-confirmed fixes
      knowledgeBase   — KnowledgeEntry list (open/resolved facts per file:line)
    """

    def __init__(self, memory_path: str) -> None:
        self.path = memory_path
        self._data: dict = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("version") == _MEMORY_VERSION:
                    return data
                # Version mismatch: back up the old file before reinitializing so
                # the resolved-findings audit trail is not silently discarded.
                backup = self.path + f".v{data.get('version', 'unknown')}.bak"
                try:
                    import shutil
                    shutil.copy2(self.path, backup)
                    print(
                        f"[memory] Schema version mismatch (found {data.get('version')!r}, "
                        f"expected {_MEMORY_VERSION!r}). "
                        f"Old data backed up to {backup}.",
                        file=sys.stderr,
                    )
                except OSError as e:
                    print(f"[memory] Version mismatch — could not back up {self.path}: {e}", file=sys.stderr)
            except (json.JSONDecodeError, OSError):
                pass
        return self._empty()

    def save(self) -> None:
        self._data["lastRun"] = _now()
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            print(f"[memory] Could not write {self.path}: {e}", file=sys.stderr)

    def _empty(self) -> dict:
        return {
            "@context": _MEMORY_CONTEXT,
            "@type": "AdaptiveUIAuditGraph",
            "@id": f"file://{os.path.abspath(self.path)}",
            "version": _MEMORY_VERSION,
            "project": {},
            "lastRun": _now(),
            "formFactors": [],
            "files": {},
            "resolvedFindings": [],
            "knowledgeBase": [],
        }

    def set_project(self, label: str) -> None:
        abs_path = os.path.abspath(label)
        self._data["project"] = {
            "@id": f"file://{abs_path}",
            "name": os.path.basename(abs_path),
        }

    def set_form_factors(self, factors: list[str]) -> None:
        existing = set(self._data.get("formFactors", []))
        self._data["formFactors"] = sorted(existing | set(factors))

    def is_clean_and_unchanged(self, path: str) -> bool:
        rel = self._rel(path)
        node = self._data["files"].get(rel)
        if not node or not node.get("clean", False):
            return False
        return node.get("fileHash") == _file_hash(path)

    def record_file(self, path: str, findings: list[Finding]) -> None:
        rel = self._rel(path)
        has_issues = any(f.severity in ("CRITICAL", "WARNING") for f in findings)
        self._data["files"][rel] = {
            "@type": "FileAuditNode",
            "@id": f"file://{os.path.abspath(path)}",
            "fileHash": _file_hash(path),
            "lastAudited": _now(),
            "clean": not has_issues,
            "findings": [asdict(f) for f in findings],
        }
        for finding in findings:
            if finding.severity in ("CRITICAL", "WARNING"):
                self._upsert_kb(
                    fact=f"{os.path.basename(path)}:{finding.line} — {finding.category}: {finding.fix}",
                    status="open",
                )

    def mark_resolved(self, path: str, line: int, category: str) -> None:
        rel = self._rel(path)
        for f in self._data["files"].get(rel, {}).get("findings", []):
            if f.get("line") == line and f.get("category") == category:
                f["resolved"] = True
        self._data["resolvedFindings"].append({
            "@type": "ResolvedFinding",
            "file": rel, "line": line,
            "category": category, "resolvedAt": _now(),
        })
        self._upsert_kb(
            fact=f"{os.path.basename(path)}:{line} — {category}",
            status="resolved",
        )

    def _upsert_kb(self, fact: str, status: str) -> None:
        kb = self._data.setdefault("knowledgeBase", [])
        for entry in kb:
            if entry.get("fact") == fact:
                entry["status"] = status
                return
        kb.append({"@type": "KnowledgeEntry", "fact": fact, "status": status, "since": _now()})

    def add_kb_fact(self, fact: str, status: str = "open") -> None:
        self._upsert_kb(fact, status)

    def _rel(self, path: str) -> str:
        try:
            return os.path.relpath(path, start=os.path.dirname(self.path))
        except ValueError:
            return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── File collection ──────────────────────────────────────────────────────────
# Accepts any mix of file paths and directory paths.
# Applies UI-file filtering so only relevant files are returned.

EXCLUDED_DIRS = {"build", ".gradle", ".idea", ".git", "node_modules"}


def collect_files(
    targets: list[str],
    result: Optional[AuditResult] = None,
) -> tuple[list[str], list[str]]:
    """
    Resolve each target (file or directory) into kt_files / xml_files lists.
    Non-UI files are counted in result.skipped_non_ui but never returned.
    Duplicate paths are deduplicated.
    """
    kt_files: list[str] = []
    xml_files: list[str] = []
    seen: set[str] = set()

    def _try_add(path: str) -> None:
        path = os.path.abspath(path)
        if path in seen:
            return
        seen.add(path)
        if path.endswith(".kt"):
            if is_ui_kt_file(path):
                kt_files.append(path)
            elif result is not None:
                result.skipped_non_ui += 1
        elif path.endswith(".xml"):
            if is_ui_xml_file(path):
                xml_files.append(path)
            elif result is not None:
                result.skipped_non_ui += 1

    for target in targets:
        if os.path.isfile(target):
            _try_add(target)
        elif os.path.isdir(target):
            for dirpath, dirnames, filenames in os.walk(target):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
                for name in filenames:
                    _try_add(os.path.join(dirpath, name))

    return kt_files, xml_files


def read_lines(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except OSError:
        return []


# ─── Checker 1: Hardcoded dp values ──────────────────────────────────────────

_DP_LITERAL_KT = re.compile(r'\b(\d+)\.dp\b')
_DP_LITERAL_XML = re.compile(r'android:(layout_width|layout_height|minWidth|minHeight|padding\w*)="(\d+)dp"')
_SAFE_DP_VALUES = {0, 1, 2, 4, 8, 16, 24, 32, 48, 56, 64, 72}
_DP_THRESHOLD = 100


class HardcodedDpChecker:
    def check_kt(self, path: str, lines: list[str], result: AuditResult) -> None:
        for i, line in enumerate(lines, 1):
            for match in _DP_LITERAL_KT.finditer(line):
                value = int(match.group(1))
                if value > _DP_THRESHOLD and value not in _SAFE_DP_VALUES:
                    stripped = line.strip()
                    if stripped.startswith("val ") or stripped.startswith("const val "):
                        continue
                    result.add(Finding(
                        severity="WARNING", category="HardcodedDp",
                        file=path, line=i,
                        message=f"Hardcoded {value}.dp may clip on small screens or waste space on large ones.",
                        fix=f"Extract to a named dimension: `val mySize = {value}.dp` or use WindowSizeClass.",
                        template_ref="templates/phone/BoxWithConstraintsGuard.kt",
                    ))

    def check_xml(self, path: str, lines: list[str], result: AuditResult) -> None:
        for i, line in enumerate(lines, 1):
            for match in _DP_LITERAL_XML.finditer(line):
                attr, value = match.group(1), int(match.group(2))
                if value > _DP_THRESHOLD and value not in _SAFE_DP_VALUES:
                    result.add(Finding(
                        severity="WARNING", category="HardcodedDp",
                        file=path, line=i,
                        message=f'Hardcoded android:{attr}="{value}dp" in XML layout.',
                        fix="Use match_parent, wrap_content, or a dimension resource @dimen/...",
                    ))


# ─── Checker 2: Scrollability ─────────────────────────────────────────────────

_COLUMN_OPEN = re.compile(r'\bColumn\s*\(')
_COLUMN_SCROLL = re.compile(r'\.verticalScroll\s*\(')
_ITEM_THRESHOLD = 5


class ScrollabilityChecker:
    def check_kt(self, path: str, lines: list[str], result: AuditResult) -> None:
        content = "".join(lines)
        for pos in [m.start() for m in _COLUMN_OPEN.finditer(content)]:
            window = content[pos:pos + 600]
            item_count = window.count("item {") + window.count("Text(") + window.count("Button(")
            # Search the forward window: .verticalScroll appears inside the Column's modifier
            # argument or on the wrapping composable — never before the Column call site.
            has_scroll = bool(_COLUMN_SCROLL.search(window))
            if item_count >= _ITEM_THRESHOLD and not has_scroll:
                result.add(Finding(
                    severity="WARNING", category="Scrollability",
                    file=path, line=content[:pos].count("\n") + 1,
                    message=f"Column with ~{item_count} children has no .verticalScroll modifier — clips on compact screens.",
                    fix="Add Modifier.verticalScroll(rememberScrollState()), or replace with LazyColumn.",
                    template_ref="templates/phone/AdaptiveScaffold.kt",
                ))

    def check_xml(self, path: str, result: AuditResult) -> None:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            return

        def has_scroll_ancestor(xml_root: ET.Element) -> bool:
            scroll_tags = {"ScrollView", "HorizontalScrollView", "androidx.core.widget.NestedScrollView"}
            return any(
                (n.tag.split("}")[-1] if "}" in n.tag else n.tag) in scroll_tags
                for n in xml_root.iter()
            )

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            n_children = len(list(elem))
            if tag == "LinearLayout" and n_children >= _ITEM_THRESHOLD and not has_scroll_ancestor(root):
                result.add(Finding(
                    severity="WARNING", category="Scrollability",
                    file=path, line=0,
                    message=f"LinearLayout with {n_children} children has no ScrollView ancestor.",
                    fix="Wrap in a ScrollView or migrate to RecyclerView / LazyColumn.",
                ))


# ─── Checker 3: Orientation lock ─────────────────────────────────────────────

_ORIENTATION_ATTR = re.compile(
    r'android:screenOrientation\s*=\s*"(portrait|landscape|reverseLandscape|reversePortrait'
    r'|sensorLandscape|sensorPortrait|userLandscape|userPortrait|locked)"'
)
# Manifest-level targetSdkVersion (legacy projects only)
_TARGET_SDK_MANIFEST = re.compile(r'android:targetSdkVersion\s*=\s*"(\d+)"')
# Gradle DSL forms: `targetSdk = 36`, `targetSdkVersion = 36`, `targetSdk(36)`
_TARGET_SDK_GRADLE = re.compile(r'targetSdk(?:Version)?\s*[=(]\s*(\d+)')
# Minimum SDK that enforces orientation policy on large screens
_ORIENTATION_CRITICAL_SDK = 36


def _resolve_target_sdk(manifest_path: str, manifest_content: str) -> int:
    """
    Return the project's targetSdk as an int.
    Priority: manifest attribute → nearest build.gradle.kts / build.gradle → default 36.
    Defaulting to 36 is the safe-fail direction: it surfaces CRITICAL rather than
    silently downgrading to WARNING on projects that don't embed targetSdk in the manifest.
    """
    m = _TARGET_SDK_MANIFEST.search(manifest_content)
    if m:
        return int(m.group(1))

    # Walk up from the manifest's directory looking for a Gradle build file
    directory = os.path.dirname(manifest_path)
    for _ in range(5):  # max 5 levels up
        for gradle_name in ("build.gradle.kts", "build.gradle"):
            gradle_path = os.path.join(directory, gradle_name)
            if os.path.isfile(gradle_path):
                try:
                    with open(gradle_path, encoding="utf-8", errors="replace") as f:
                        gradle_content = f.read()
                    gm = _TARGET_SDK_GRADLE.search(gradle_content)
                    if gm:
                        return int(gm.group(1))
                except OSError:
                    pass
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent

    # Could not determine targetSdk — assume modern project
    return _ORIENTATION_CRITICAL_SDK


class OrientationLockChecker:
    def check_xml(self, path: str, lines: list[str], result: AuditResult) -> None:
        if "AndroidManifest.xml" not in path:
            return
        content = "".join(lines)
        target_sdk = _resolve_target_sdk(path, content)
        for i, line in enumerate(lines, 1):
            m = _ORIENTATION_ATTR.search(line)
            if m:
                result.add(Finding(
                    severity="CRITICAL" if target_sdk >= _ORIENTATION_CRITICAL_SDK else "WARNING",
                    category="OrientationLock",
                    file=path, line=i,
                    message=f'screenOrientation="{m.group(1)}" ignored on large-screen/foldable (targetSdk {target_sdk}).',
                    fix='Remove android:screenOrientation or set to "unspecified". Use WindowSizeClass instead.',
                    template_ref="templates/phone/AdaptiveScaffold.kt",
                ))


# ─── Checker 4: WindowSizeClass API ──────────────────────────────────────────

_DEPRECATED_WSC = re.compile(r'calculateWindowSizeClass\s*\(')
_ENUM_EQUALITY = re.compile(
    r'WindowWidthSizeClass\.(Compact|Medium|Expanded)\s*==|==\s*WindowWidthSizeClass\.(Compact|Medium|Expanded)'
)
_HEIGHT_EQUALITY = re.compile(
    r'WindowHeightSizeClass\.(Compact|Medium|Expanded)\s*==|==\s*WindowHeightSizeClass\.(Compact|Medium|Expanded)'
)
_WRONG_IMPORT = re.compile(r'import\s+androidx\.compose\.material3\.windowsizeclass\.')
_MISSING_OPTIN = re.compile(
    r'ListDetailPaneScaffold|SupportingPaneScaffold'
    r'|NavigableListDetailPaneScaffold|NavigableSupportingPaneScaffold|AdaptiveNavigationSuite'
)
_HAS_OPTIN = re.compile(r'@file:OptIn\(ExperimentalMaterial3AdaptiveApi|@OptIn\(ExperimentalMaterial3AdaptiveApi')


class WindowSizeClassApiChecker:
    def check_kt(self, path: str, lines: list[str], result: AuditResult) -> None:
        content = "".join(lines)
        for i, line in enumerate(lines, 1):
            if _DEPRECATED_WSC.search(line):
                result.add(Finding(
                    severity="CRITICAL", category="WindowSizeClass",
                    file=path, line=i,
                    message="calculateWindowSizeClass() is deprecated.",
                    fix="val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass",
                    template_ref="templates/phone/AdaptiveScaffold.kt",
                ))
            if _ENUM_EQUALITY.search(line):
                result.add(Finding(
                    severity="WARNING", category="WindowSizeClass",
                    file=path, line=i,
                    message="WindowWidthSizeClass enum equality breaks when L/XL classes are added.",
                    fix="windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)",
                    template_ref="references/breakpoints.md",
                ))
            if _HEIGHT_EQUALITY.search(line):
                result.add(Finding(
                    severity="WARNING", category="WindowSizeClass",
                    file=path, line=i,
                    message="WindowHeightSizeClass enum equality is fragile.",
                    fix="windowSizeClass.isHeightAtLeastBreakpoint(HEIGHT_DP_MEDIUM_LOWER_BOUND)",
                    template_ref="references/breakpoints.md",
                ))
        if _WRONG_IMPORT.search(content):
            result.add(Finding(
                severity="WARNING", category="WindowSizeClass",
                file=path, line=1,
                message="Importing from deprecated androidx.compose.material3.windowsizeclass package.",
                fix="Import from androidx.compose.material3; use currentWindowAdaptiveInfo().",
                template_ref="templates/phone/AdaptiveScaffold.kt",
            ))
        if _MISSING_OPTIN.search(content) and not _HAS_OPTIN.search(content):
            result.add(Finding(
                severity="CRITICAL", category="WindowSizeClass",
                file=path, line=1,
                message="Adaptive scaffold APIs used without @OptIn(ExperimentalMaterial3AdaptiveApi::class).",
                fix="Add @file:OptIn(ExperimentalMaterial3AdaptiveApi::class) at top of file.",
                template_ref="templates/tablet-large-screen/ListDetailScreen.kt",
            ))


# ─── Checker 5: Form factor compliance ───────────────────────────────────────

_WEAR_COMPOSE_IMPORT = re.compile(r'import\s+androidx\.wear\.compose\.')
_MOBILE_MATERIAL3_IMPORT = re.compile(r'import\s+androidx\.compose\.material3\.')
_SCALING_LAZY_COLUMN = re.compile(r'\bScalingLazyColumn\b')
_TRANSFORMING_LAZY_COLUMN = re.compile(r'\bTransformingLazyColumn\b')
_CAR_SCREEN_EXTENDS = re.compile(r'class\s+\w+\s*[:(]\s*Screen\s*\(')
_COMPOSE_SET_CONTENT = re.compile(r'\bsetContent\s*\{')
_WINDOW_INFO_TRACKER = re.compile(r'\bWindowInfoTracker\b')
_COLLECT_STATE = re.compile(r'collectAsStateWithLifecycle|collectFoldingFeaturesAsState')
_MIN_CAR_API = re.compile(r'androidx\.car\.app\.minCarApiLevel')
_CAR_IMPORT = re.compile(r'import\s+androidx\.car\.app\.')
_BITMAP_DECODE = re.compile(r'BitmapFactory\.decodeResource\s*\(')


class FormFactorComplianceChecker:
    def check_kt(self, path: str, lines: list[str], result: AuditResult) -> None:
        content = "".join(lines)
        has_wear = bool(_WEAR_COMPOSE_IMPORT.search(content))
        has_m3 = bool(_MOBILE_MATERIAL3_IMPORT.search(content))
        if has_wear and has_m3:
            result.add(Finding(
                severity="CRITICAL", category="Wear",
                file=path, line=1,
                message="androidx.wear.compose.* and androidx.compose.material3.* in same file — incompatible MaterialTheme.",
                fix="Move Wear code to a separate :wear module. Remove androidx.compose.material3 imports.",
                template_ref="templates/wear/WearAppScaffold.kt",
            ))
        if has_wear and _SCALING_LAZY_COLUMN.search(content) and not _TRANSFORMING_LAZY_COLUMN.search(content):
            result.add(Finding(
                severity="INFO", category="Wear",
                file=path, line=1,
                message="ScalingLazyColumn is superseded by TransformingLazyColumn.",
                fix="Migrate to TransformingLazyColumn with rememberTransformingLazyColumnState().",
                template_ref="templates/wear/WearAppScaffold.kt",
            ))
        if _CAR_IMPORT.search(content) and _CAR_SCREEN_EXTENDS.search(content) and _COMPOSE_SET_CONTENT.search(content):
            result.add(Finding(
                severity="CRITICAL", category="Auto",
                file=path, line=1,
                message="setContent{} inside Car App Screen — Auto does not support Compose rendering.",
                fix="Remove setContent{}. Return a Template from onGetTemplate() instead.",
                template_ref="templates/auto/MainScreen.kt",
            ))
        if _WINDOW_INFO_TRACKER.search(content) and not _COLLECT_STATE.search(content):
            result.add(Finding(
                severity="WARNING", category="Foldable",
                file=path, line=1,
                message="WindowInfoTracker without collectAsStateWithLifecycle — may leak on config change.",
                fix="Use collectFoldingFeaturesAsState() or collectAsStateWithLifecycle().",
                template_ref="templates/foldable/PostureDetector.kt",
            ))
        for i, line in enumerate(lines, 1):
            if _BITMAP_DECODE.search(line):
                result.add(Finding(
                    severity="INFO", category="Density",
                    file=path, line=i,
                    message="BitmapFactory.decodeResource() — ensure drawable has density variants.",
                    fix="Provide drawable-mdpi + drawable-xxhdpi variants, or use a vector drawable.",
                    template_ref="references/density-table.md",
                ))

    def check_xml(self, path: str, content: str, result: AuditResult) -> None:
        if "AndroidManifest.xml" not in path:
            return
        if "CarAppService" in content and not _MIN_CAR_API.search(content):
            result.add(Finding(
                severity="WARNING", category="Auto",
                file=path, line=1,
                message="CarAppService in manifest but androidx.car.app.minCarApiLevel meta-data missing.",
                fix='Add <meta-data android:name="androidx.car.app.minCarApiLevel" android:value="1" /> inside <service>.',
                template_ref="templates/auto/MyCarAppService.kt",
            ))


# ─── Checker 6: Text overflow ─────────────────────────────────────────────────

_TEXT_COMPOSABLE = re.compile(r'\bText\s*\(')
_HAS_OVERFLOW = re.compile(r'overflow\s*=')
_HAS_MAX_LINES = re.compile(r'maxLines\s*=')


class TextOverflowChecker:
    def check_kt(self, path: str, lines: list[str], result: AuditResult) -> None:
        for i, line in enumerate(lines, 1):
            if _TEXT_COMPOSABLE.search(line):
                # Scan until the closing paren of the Text() call (up to 10 lines).
                # A 4-line window misses maxLines/overflow on line 5+ in idiomatic
                # multi-parameter Compose calls.
                end = min(i + 9, len(lines))
                closing = next(
                    (j for j in range(i - 1, end) if ")" in lines[j] and j > i - 1),
                    end - 1,
                )
                window = "".join(lines[i - 1:closing + 1])
                if not _HAS_OVERFLOW.search(window) and not _HAS_MAX_LINES.search(window):
                    result.add(Finding(
                        severity="INFO", category="TextOverflow",
                        file=path, line=i,
                        message="Text() without overflow/maxLines — clips unpredictably on small screens.",
                        fix="Add maxLines=1, overflow=TextOverflow.Ellipsis for titles; softWrap=true for body.",
                    ))


# ─── Form factor detection ────────────────────────────────────────────────────
# Reuses the already-collected file lists — no extra disk reads.

def detect_form_factors(kt_files: list[str], xml_files: list[str], _preloaded: dict[str, list[str]] | None = None) -> list[str]:
    # Derive form factors from already-loaded line buffers when available to
    # avoid a second full disk read pass over the same files.
    def _get(p: str) -> list[str]:
        if _preloaded and p in _preloaded:
            return _preloaded[p]
        return read_lines(p)

    content = "".join("".join(_get(p)) for p in kt_files + xml_files)
    factors: list[str] = []
    if re.search(r'androidx\.wear\.compose\.', content):
        factors.append("wear")
    if re.search(r'CarAppService|androidx\.car\.app\.', content):
        factors.append("auto")
    if re.search(r'FoldingFeature|WindowInfoTracker', content):
        factors.append("foldable")
    if re.search(r'ListDetailPaneScaffold|SupportingPaneScaffold|NavigationSuiteScaffold', content):
        factors.append("large-screen")
    if not factors or "large-screen" not in factors:
        factors.append("phone")
    return factors


# ─── Runner ───────────────────────────────────────────────────────────────────

def run_audit(targets: list[str], memory: Optional[MemoryStore] = None) -> AuditResult:
    result = AuditResult()

    kt_files, xml_files = collect_files(targets, result)

    # Pre-load all file content once and reuse across form-factor detection and
    # checkers — eliminates the 2× full disk read that detect_form_factors caused.
    line_cache: dict[str, list[str]] = {}
    for path in kt_files + xml_files:
        line_cache[path] = read_lines(path)

    result.detected_form_factors = detect_form_factors(kt_files, xml_files, _preloaded=line_cache)

    if memory:
        memory.set_project(targets[0])
        memory.set_form_factors(result.detected_form_factors)
        result.memory_path = memory.path

    kt_checkers = [
        HardcodedDpChecker(),
        ScrollabilityChecker(),
        WindowSizeClassApiChecker(),
        FormFactorComplianceChecker(),
        TextOverflowChecker(),
    ]
    xml_line_checkers = [HardcodedDpChecker(), OrientationLockChecker()]
    ff_checker = FormFactorComplianceChecker()
    scroll_checker = ScrollabilityChecker()

    for path in kt_files:
        if memory and memory.is_clean_and_unchanged(path):
            result.skipped_cached += 1
            continue
        lines = line_cache[path]
        sub = AuditResult()
        for checker in kt_checkers:
            checker.check_kt(path, lines, sub)
        for f in sub.findings:
            result.add(f)
        if memory:
            memory.record_file(path, sub.findings)
        result.scanned_kt += 1

    for path in xml_files:
        if memory and memory.is_clean_and_unchanged(path):
            result.skipped_cached += 1
            continue
        lines = line_cache[path]
        content = "".join(lines)
        sub = AuditResult()
        for checker in xml_line_checkers:
            checker.check_xml(path, lines, sub)
        ff_checker.check_xml(path, content, sub)
        if "layout" in path:
            scroll_checker.check_xml(path, sub)
        for f in sub.findings:
            result.add(f)
        if memory:
            memory.record_file(path, sub.findings)
        result.scanned_xml += 1

    if memory:
        memory.save()

    return result


# ─── Output formatters ────────────────────────────────────────────────────────

def format_text(result: AuditResult, show_info: bool = False) -> str:
    out: list[str] = []

    # Scan card
    skip_parts: list[str] = []
    if result.skipped_cached:
        skip_parts.append(f"{result.skipped_cached} cached")
    if result.skipped_non_ui:
        skip_parts.append(f"{result.skipped_non_ui} non-UI skipped")
    skip_note = f"  ({', '.join(skip_parts)})" if skip_parts else ""
    mem_note = f"\nMemory file  : {result.memory_path}" if result.memory_path else ""

    out.append(
        f"\nSCAN {'─' * 44}\n"
        f"Form factors : {', '.join(result.detected_form_factors)}\n"
        f"Files scanned: {result.scanned_kt} kt · {result.scanned_xml} xml{skip_note}"
        f"{mem_note}"
    )

    actionable = [f for f in result.findings if f.severity in ("CRITICAL", "WARNING")]
    info_items = [f for f in result.findings if f.severity == "INFO"]

    if actionable:
        # Findings index
        out.append(f"\nFINDINGS {'─' * 41}")
        out.append(f"{'#':<4} {'SEV':<10} {'FILE:LINE':<40} CATEGORY")
        for idx, f in enumerate(actionable, 1):
            loc = f"{os.path.basename(f.file)}:{f.line}"
            out.append(f"{idx:<4} {f.severity:<10} {loc:<40} {f.category}")

        # Before → After table
        out.append(f"\nBEFORE → AFTER {'─' * 35}")
        out.append(f"{'FILE':<30} {'BEFORE':<35} {'AFTER':<35} ACTION")
        for f in actionable:
            loc = f"{os.path.basename(f.file)}:{f.line}"
            before = _truncate(f.message.split("—")[0].strip(), 33)
            after = _truncate(f.fix, 33)
            action = "REPLACE" if "deprecated" in f.message.lower() or "Replace" in f.fix else "ADD/FIX"
            out.append(f"{loc:<30} {before:<35} {after:<35} {action}")
    else:
        out.append("\nNo CRITICAL or WARNING findings.")

    if info_items:
        if show_info:
            out.append(f"\nINFO DETAILS ({len(info_items)} items)")
            for f in info_items:
                out.append(f"  [{f.category}] {os.path.basename(f.file)}:{f.line} — {f.fix}")
        else:
            out.append(f"\nINFO: {len(info_items)} low-priority item{'s' if len(info_items) != 1 else ''} (--show-info to expand)")

    out.append(f"\n{'─' * 55}")
    out.append(f"PENDING: {result.critical_count} CRITICAL · {result.warning_count} WARNING · {result.info_count} INFO")
    if actionable:
        out.append("Apply all? [all / one-by-one / critical-only / skip]")

    return "\n".join(out)


def format_json(result: AuditResult) -> str:
    return json.dumps({
        "scanned_kt": result.scanned_kt,
        "scanned_xml": result.scanned_xml,
        "skipped_cached": result.skipped_cached,
        "skipped_non_ui": result.skipped_non_ui,
        "detected_form_factors": result.detected_form_factors,
        "memory_path": result.memory_path,
        "summary": {
            "critical": result.critical_count,
            "warning": result.warning_count,
            "info": result.info_count,
        },
        "findings": [asdict(f) for f in result.findings],
    }, indent=2)


def _truncate(s: str, max_len: int) -> str:
    return s if len(s) <= max_len else s[:max_len - 1] + "…"


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Android Adaptive UI Audit Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  audit a directory:     %(prog)s --src app/src/main\n"
            "  audit a single file:   %(prog)s --src app/src/main/java/ui/HomeScreen.kt\n"
            "  audit specific files:  %(prog)s --src ui/HomeScreen.kt res/layout/activity_main.xml\n"
            "  with memory cache:     %(prog)s --src app/src/main --memory .adaptive-ui-memory.json\n"
        ),
    )
    parser.add_argument(
        "--src", nargs="+", required=True, metavar="PATH",
        help="One or more file or directory paths to audit (.kt / .xml). "
             "Non-UI files are automatically skipped.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--memory", default=None, metavar="FILE",
        help="Path to JSON-LD memory file (e.g. /project/.adaptive-ui-memory.json). "
             "Enables file-hash caching and knowledge-base accumulation.",
    )
    parser.add_argument(
        "--show-info", action="store_true",
        help="Expand INFO-level findings in text output.",
    )
    args = parser.parse_args()

    # Validate each --src entry
    invalid = [p for p in args.src if not os.path.exists(p)]
    if invalid:
        for p in invalid:
            print(f"Error: path not found: {p}", file=sys.stderr)
        sys.exit(2)

    memory = MemoryStore(args.memory) if args.memory else None
    result = run_audit(args.src, memory=memory)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_text(result, show_info=args.show_info))

    sys.exit(1 if result.critical_count > 0 else 0)


if __name__ == "__main__":
    main()
