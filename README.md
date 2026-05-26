# Android Skills Repository

This repository hosts installable AI coding skills (Codex/Claude compatible).

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
git clone <YOUR_GITHUB_REPO_URL>
cd <repo-name>
```

### 3) Verify available skills

```bash
./scripts/list-skills.sh
```

### 4) Install skills

Install one skill:

```bash
./scripts/install-skill.sh --skill xml-to-compose-architect --target both
```

Install all skills:

```bash
./scripts/install-skill.sh --all --target both
```

One-line install via `curl` (after publish):

Install one skill:

```bash
curl -fsSL https://raw.githubusercontent.com/<ORG>/<REPO>/main/scripts/bootstrap-install.sh | bash -s -- --repo https://github.com/<ORG>/<REPO>.git --skill xml-to-compose-architect --target both
```

Install all skills:

```bash
curl -fsSL https://raw.githubusercontent.com/<ORG>/<REPO>/main/scripts/bootstrap-install.sh | bash -s -- --repo https://github.com/<ORG>/<REPO>.git --all --target both
```

Install mode options:
1. `copy` (default): copies skill files into target directories.
2. `link`: symlinks skill folders for live development.

```bash
./scripts/install-skill.sh --skill xml-to-compose-architect --mode link
```

### 5) Verify installation

```bash
ls -la ~/.codex/skills/xml-to-compose-architect
ls -la ~/.claude/skills/xml-to-compose-architect
```

### 6) Uninstall

```bash
./scripts/uninstall-skill.sh --skill xml-to-compose-architect --target both
./scripts/uninstall-skill.sh --all --target both
```

### 7) Custom install directories (optional)

```bash
./scripts/install-skill.sh \
  --skill xml-to-compose-architect \
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

Default install targets:
1. Codex: `~/.codex/skills`
2. Claude: `~/.claude/skills`

## Publish to GitHub

1. Create a new GitHub repository (for example: `android-skills`).
2. Initialize and commit locally:
```bash
git init
git add .
git commit -m "feat: add multi-skill repository with xml-to-compose-architect skill"
```
3. Connect remote and push:
```bash
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```
4. Share usage docs from this README and per-skill README.
