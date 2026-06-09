# Android Skills Repository

This repository hosts installable AI coding skills (Codex/Claude compatible).
Published repo: `https://github.com/r-sadat-sayem/android-agent-skills`

## Setup Guide

---

### Option A — Install via AI Agent (recommended)

**The fastest path.** Copy the prompt below and paste it directly into Claude Code or Codex chat. The agent will check your current installed version, compare it against the latest on GitHub, install (replacing any older version), and confirm the result — no terminal setup required on your part.

> **Requires:** `curl` and `git` on your machine. Claude Code or Codex must be able to run shell commands.

---

#### Install `android-adaptive-ui`

Copy this entire block and paste it into Claude Code or Codex:

```
Install the android-adaptive-ui skill from GitHub.

Do these steps in order:

1. Check whether ~/.claude/skills/android-adaptive-ui/VERSION exists.
   If it does, read it and report the currently installed version.
   If it doesn't, report "not installed".

2. Fetch the latest available version from:
   https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/skills/android-adaptive-ui/VERSION
   Report the latest version number.

3. Run this install command (it always replaces any existing version):
   curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/aau-install.sh && bash /tmp/aau-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill android-adaptive-ui --target claude && rm -f /tmp/aau-install.sh

4. Read ~/.claude/skills/android-adaptive-ui/VERSION and confirm the installed version.
```

---

#### What the agent does

| Step | What happens |
|---|---|
| Check current | Reads `~/.claude/skills/android-adaptive-ui/VERSION` — shows `none` if not installed |
| Check latest | Fetches the `VERSION` file from GitHub over HTTPS — no clone needed |
| Install | `bootstrap-install.sh` clones the repo to a temp directory, copies the skill files, writes a `.skill-source` record (used for future updates), then deletes the temp clone |
| Replace | The installer always runs `rm -rf` on the destination before copying — older versions are always replaced |
| Confirm | Reads the newly-written `VERSION` file to verify the install succeeded |

Expected output shape:

```
Installed : none  →  Latest : 1.1.0
[ok] Claude: android-adaptive-ui -> /Users/<you>/.claude/skills/android-adaptive-ui
Done. Version: 1.1.0 ✓
```

---

#### To also install to Codex

Replace `--target claude` with `--target both` in step 3 of the prompt above, or paste this variant:

```
Install the android-adaptive-ui skill to both Claude and Codex.

1. Check ~/.claude/skills/android-adaptive-ui/VERSION and ~/.codex/skills/android-adaptive-ui/VERSION — report each.
2. Fetch the latest version from:
   https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/skills/android-adaptive-ui/VERSION
3. Run:
   curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/aau-install.sh && bash /tmp/aau-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill android-adaptive-ui --target both && rm -f /tmp/aau-install.sh
4. Confirm both ~/.claude/skills/android-adaptive-ui/VERSION and ~/.codex/skills/android-adaptive-ui/VERSION.
```

---

#### To update an already-installed skill

Paste this into Claude Code or Codex at any time to pull the latest version:

```
Update the android-adaptive-ui skill to the latest version from GitHub.

1. Read ~/.claude/skills/android-adaptive-ui/VERSION — report the current version.
2. Fetch the latest version from:
   https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/skills/android-adaptive-ui/VERSION
   If current == latest, report "already up to date" and stop.
3. Run:
   curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/aau-install.sh && bash /tmp/aau-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill android-adaptive-ui --target claude && rm -f /tmp/aau-install.sh
4. Read ~/.claude/skills/android-adaptive-ui/VERSION and confirm the new version.
```

---

### Option B — Install manually

Use this if you prefer direct shell control, want `--mode link` for live development, or are setting up CI.

#### 1) Prerequisites

1. `git`
2. `bash`
3. `rsync` (used by installer in `copy` mode)

Optional:
1. Codex installed (uses `~/.codex/skills`)
2. Claude installed (uses `~/.claude/skills`)

#### 2) Clone repository

```bash
git clone https://github.com/r-sadat-sayem/android-agent-skills.git
cd android-agent-skills
```

#### 3) Verify available skills

```bash
./scripts/list-skills.sh
```

#### 4) Install skills

Install one skill:

```bash
./scripts/install-skill.sh --skill android-adaptive-ui --target both
```

Install all skills:

```bash
./scripts/install-skill.sh --all --target both
```

What `--target both` means:
1. Installs to Codex (`~/.codex/skills`)
2. Installs to Claude (`~/.claude/skills`)

Other target values:
1. `--target codex` installs only to Codex
2. `--target claude` installs only to Claude

Remote bootstrap install (download, inspect, then run):

```bash
curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/bootstrap-install.sh
less /tmp/bootstrap-install.sh
bash /tmp/bootstrap-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill android-adaptive-ui --target both
```

Development mode (symlink — live reload on file changes):

```bash
./scripts/install-skill.sh --skill android-adaptive-ui --mode link
```

#### 5) Verify installation

```bash
cat ~/.claude/skills/android-adaptive-ui/VERSION
ls -la ~/.claude/skills/android-adaptive-ui
```

#### 6) Update installed skills

```bash
# Update one skill (reads the .skill-source record written at install time):
./scripts/update-skill.sh --skill android-adaptive-ui

# Update all installed skills:
./scripts/update-skill.sh --all

# Dry-run: see installed vs remote version without changing anything:
./scripts/update-skill.sh --check --skill android-adaptive-ui

# Pull a specific tag:
./scripts/update-skill.sh --skill android-adaptive-ui --ref v1.2.0
```

**How `.skill-source` works:** `bootstrap-install.sh` writes a `.skill-source` file inside each installed skill directory recording the GitHub URL and ref. `update-skill.sh` reads that record to know where to pull from — no local clone needed. If you installed with `--mode link`, the symlink already points at the live source; `update-skill.sh` will remind you to `git pull` in the repo instead.

#### 7) Custom install directories (optional)

```bash
./scripts/install-skill.sh \
  --skill android-adaptive-ui \
  --codex-dir /custom/codex/skills \
  --claude-dir /custom/claude/skills
```

#### 8) Uninstall

```bash
./scripts/uninstall-skill.sh --skill android-adaptive-ui --target both
./scripts/uninstall-skill.sh --all --target both
```

## Repository Layout

```text
.
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── references/
│       ├── assets/
│       ├── templates/
│       ├── checklists/
│       └── scripts/
└── scripts/
    ├── install-skill.sh
    ├── update-skill.sh
    ├── bootstrap-install.sh
    └── uninstall-skill.sh
```

## Available skills

1. `xml-to-compose-architect`
2. `android-adaptive-ui`

Recommended first install:

```bash
./scripts/install-skill.sh --skill <skill-name> --target both
```

Default install targets:
1. Codex: `~/.codex/skills`
2. Claude: `~/.claude/skills`

## Skill Notes

1. Each skill has its own README under `skills/<skill-name>/README.md`.
2. Feature scope differs by skill; check the per-skill README before use.
