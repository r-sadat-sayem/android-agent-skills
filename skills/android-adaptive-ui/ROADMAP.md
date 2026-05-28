# Roadmap

## Current State

`solutions-playbook.json` is skill-local. Every developer who installs this skill gets the seed patterns bundled in `references/solutions-playbook.json`. New patterns are appended locally and stay on that developer's machine.

---

## Planned: Centralized Playbook Collection

### Goal

Collect locally-evolved playbooks from all skill users into a central server (owned by the skill author), learn from aggregate submissions, and push a curated best-of version back out to all users.

### Architecture

Two separate, non-overlapping flows:

```
COLLECTION  (developer → your server, write-only, anonymous)
  dev runs: python scripts/sync_playbook.py contribute
  → POST to Firebase RTDB: /android-adaptive-ui/submissions/{uuid}
  → Each submission is a fully isolated document — never overwrites another

DISTRIBUTION  (your server → all developers, read-only)
  you review Firebase submissions → cherry-pick patterns → push curated set to Gist
  dev runs: python scripts/sync_playbook.py pull
  → Fetches curated playbook from your public Gist raw URL
```

### Firebase Security Rules

```json
{
  "rules": {
    "android-adaptive-ui": {
      "submissions": {
        "$submission_id": {
          ".write": true,
          ".read": false
        }
      },
      "playbook": {
        ".read":  true,
        ".write": "auth != null"
      }
    }
  }
}
```

- Anyone can submit without a token (anonymous write to `submissions/`)
- Only you (authenticated) can read submissions or write to the curated playbook
- Developers pull the curated playbook without authentication

### `sync_playbook.py` Commands (to be built)

| Command | Who runs it | What it does |
|---|---|---|
| `contribute` | Any developer | Submits local playbook to Firebase as a new UUID document |
| `pull` | Any developer | Fetches owner-curated playbook from public Gist |
| `merge` | Any developer | Merges pulled remote patterns into local playbook |
| `owner-pull` | Skill owner only | Aggregates all Firebase submissions into a local review file |
| `push` | Skill owner only | Pushes curated local playbook to Gist for distribution |

### Submission Document Schema

```json
{
  "submitted_at": "ISO-8601",
  "skill_version": "1.0.0",
  "platform": "darwin|linux|windows",
  "contributor_handle": "github-handle or null",
  "patterns": [ /* full patterns array from local solutions-playbook.json */ ]
}
```

### Key Design Decisions

- **Firebase over Gist as primary collection endpoint** — Gist is peer-to-peer (any dev can overwrite any pattern). Firebase with append-only rules is a true collection server.
- **UUID per submission** — eliminates silent overwrites. Two devs submitting the same pattern ID = two separate documents you review, not a collision.
- **No `?auth=token` in URLs** — tokens must go in `Authorization: Bearer` header to avoid leaking into server logs and shell history.
- **`success_count` is local only** — not used for server-side conflict resolution. Server aggregation (pattern frequency across submissions) replaces it.
- **Opt-in consent UX** — `contribute` prompts the developer before sending anything; `--yes` flag for CI bypass.

### Files to Create When Building This

- `scripts/sync_playbook.py` — implement all commands above
- Firebase project + security rules (one-time setup)
- GitHub Gist (one-time setup) for distribution endpoint

### What Stays Unchanged

- `references/solutions-playbook.json` — local file, no server dependency
- `layout_audit.py` — not affected
- `SKILL.md` playbook rules — local read/index/increment stays as-is; only add `contribute` instruction
