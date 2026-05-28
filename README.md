# Android Skills Repository

This repository hosts installable AI coding skills (Codex/Claude compatible).
Published repo: `https://github.com/r-sadat-sayem/android-agent-skills`

## Setup Guide

### 1) Prerequisites

1. `git`
2. `bash`
3. `rsync` (used by installer in `copy` mode)

Optional:
1. Codex installed (uses `~/.codex/skills`)
2. Claude installed (uses `~/.claude/skills`)

### 2) Clone repository

```bash
git clone https://github.com/r-sadat-sayem/android-agent-skills.git
cd android-agent-skills
```

### 3) Verify available skills

```bash
./scripts/list-skills.sh
```

### 4) Install skills

Install one skill:

```bash
./scripts/install-skill.sh --skill <skill-name> --target both
```

Example:

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

Remote bootstrap install (safer flow: download, inspect, then run):

Install one skill:

```bash
curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/bootstrap-install.sh
less /tmp/bootstrap-install.sh
bash /tmp/bootstrap-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill <skill-name> --target both
```

Install all skills:

```bash
curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/bootstrap-install.sh
less /tmp/bootstrap-install.sh
bash /tmp/bootstrap-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --all --target both
```

Install mode options:
1. `copy` (default): copies skill files into target directories.
2. `link`: symlinks skill folders for live development.

```bash
./scripts/install-skill.sh --skill <skill-name> --mode link
```

### 5) Verify installation

```bash
ls -la ~/.codex/skills/<skill-name>
ls -la ~/.claude/skills/<skill-name>
```

### 6) Uninstall

```bash
./scripts/uninstall-skill.sh --skill <skill-name> --target both
./scripts/uninstall-skill.sh --all --target both
```

### 7) Custom install directories (optional)

```bash
./scripts/install-skill.sh \
  --skill <skill-name> \
  --codex-dir /custom/codex/skills \
  --claude-dir /custom/claude/skills
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
