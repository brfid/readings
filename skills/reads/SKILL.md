---
name: reads
description: "Use when tracking reading via the brfid/reads GitHub repo — add items, update status, query, search, discuss, capture facts, save content, or drain the cross-profile queue."
version: 3.0.0
author: Brad Fidler
license: MIT
metadata:
  hermes:
    tags: [reading, tracking, github, yaml, books, articles]
    related_skills: [github-repo-management]
---

# Reads

Personal reading tracker: `brfid/reads` on GitHub, cloned locally at
`~/.hermes/profiles/bede/workspace/reads`. All operations go through
`reads.py` — a stdlib-only CLI that handles YAML loading, validation,
git commit/push, and README regeneration.

## When to Use

Add, start, finish, note, search, query, discuss, or save reading items.
Drain the cross-profile queue. Query reading history via git log.

**Do NOT use for:** general web research, literature reviews, note-taking outside the tracker.

## Pre-Flight

1. `cd ~/.hermes/profiles/bede/workspace/reads && git pull --rebase`
2. Check queue: `python3 reads.py queue-drain` (if items pending, ask user first)
3. Run the command (see table below)
4. If `reads.py` reports ambiguous match, show candidates and ask user to disambiguate

## Architecture (v3 — July 2026)

- **`reading.yaml`** — single source of truth. All metadata in one file (v2 schema). No per-item meta.yaml.
- **`texts/{folder}/`** — CLAUDE.md (agent context), conversations.md (discussion log), content.md (saved content), meta.json (CI-generated, don't edit).
- **`queue.yaml`** — cross-profile inbox. Other agents append via `reads.py queue-add`.
- **`reads.py`** — CLI that replaces all bash templates. Validates schema on every write.
- **CI** — `reads.py validate` + `compile_meta.py` on push.

## YAML Schema (v2)

```yaml
version: 2
items:
  - title: "DDIA"
    authors: [Martin Kleppmann]    # optional list
    type: book                     # book | article | paper | post
    location: "https://..."        # URL or "Books app"
    path: texts/ddia               # required, must start with texts/
    status: reading                # want-to-read | reading | done | abandoned
    publisher: "O'Reilly"          # optional
    published: "2017"               # optional, string
    isbn: "978-..."                 # optional
    rating: 4                       # optional, 1-5
    notes: []                       # optional list of strings
```

No date fields. Git history = timeline. CI extracts dates from commits.

## Intent → Command

| Intent | Trigger examples | Command |
|--------|-----------------|----------|
| **Add** | "add DDIA", "track https://..." | `python3 reads.py add --title "T" --author "A" --type book --location "URL"` |
| **Start** | "started DDIA", "reading now" | `python3 reads.py start "ref"` |
| **Finish** | "finished DDIA", "done with DDIA" | `python3 reads.py finish "ref" --rating 5` |
| **Note** | "note on DDIA: chapter 5 great" | `python3 reads.py note "ref" "text"` |
| **Fact** | "author is Kleppmann", "isbn 978-..." | `python3 reads.py fact "ref" field value` |
| **Discuss** | "discuss DDIA", "continue DDIA" | `python3 reads.py discuss "ref" "text" --topic "slug"` |
| **Save** | "save compound engineering" | `python3 reads.py save "ref"` |
| **Query** | "what am I reading?", "show backlog" | `python3 reads.py query --status reading` |
| **Search** | "what about distributed systems?" | `python3 reads.py search "keyword"` |
| **History** | "when did I finish DDIA?" | `python3 reads.py history "ref"` |
| **README** | "update readme" | `python3 reads.py readme` |
| **Queue Add** | (from other profiles) | `python3 reads.py queue-add --location "URL" --title "T" --from jinny` |
| **Queue Drain** | "process queue" | `python3 reads.py queue-drain` |
| **Validate** | (CI only) | `python3 reads.py validate` |

`<ref>` is a title, path, or fuzzy search string. If ambiguous, reads.py lists candidates and exits 1.

## Matching Items

`reads.py resolve()` matches: exact path → exact title (case-insensitive) → fuzzy substring. If multiple matches, it prints candidates and exits — show them to the user and ask.

## Folder Naming

Derived from title: lowercase, hyphens, strip leading articles (a/an/the), max 40 chars. Collisions get `-2`, `-3` suffixes.

## Reference Files

- `references/e2e-pipeline-readings.md` — Brad's canonical pipeline/CI/CD reading list. Load when user references "e2e readings" or asks about pipeline reading backlog.

## Notes

- All git operations use SSH (`git@github.com:brfid/reads.git`) — the HTTPS OAuth token lacks `workflow` scope.
- `reads.py` handles folder file creation (CLAUDE.md, conversations.md) automatically on `add`.
- `notes` is a list of strings — each note is its own entry.
- `authors` is comma-separated on the CLI: `--author "A" --author "B"` or `fact authors "A, B"`.