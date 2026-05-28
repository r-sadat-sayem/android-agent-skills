# XML to Compose Architect Skill

Architecture-first XML-to-Compose migration skill with strict guardrails:
- Ask clarifying questions first
- Recommend architecture patterns before implementation
- Enforce state-hoisting and recomposition best practices
- Require meaningful `@Preview` coverage

## Install (from repository root)

```bash
./scripts/install-skill.sh --skill xml-to-compose-architect --target both
```

Targets:
- `codex`
- `claude`
- `both` (default)

Modes:
- `copy` (default, safest)
- `link` (symlink for live edits)

Examples:

```bash
./scripts/install-skill.sh --skill xml-to-compose-architect --target codex
./scripts/install-skill.sh --skill xml-to-compose-architect --target claude --mode link
```

## Install locations

- Codex: `~/.codex/skills/xml-to-compose-architect`
- Claude: `~/.claude/skills/xml-to-compose-architect`

You can override either path:

```bash
./scripts/install-skill.sh --skill xml-to-compose-architect --codex-dir /custom/codex/skills --claude-dir /custom/claude/skills
```

## Uninstall

```bash
./scripts/uninstall-skill.sh --skill xml-to-compose-architect --target both
```

## Validate analysis output template

```bash
./skills/xml-to-compose-architect/scripts/validate_output.sh ./skills/xml-to-compose-architect/templates/analysis-report-template.md
```
