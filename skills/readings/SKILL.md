---
name: readings
description: "Use when tracking reading via brfid/readings GitHub Issues — add items, update status, query, search, discuss, or capture facts."
version: 5.0.0
author: Brad Fidler
license: MIT
metadata:
  tags: [reading, tracking, github, issues]
---

# Reads

Personal reading tracker: GitHub Issues on `brfid/readings`. Every reading item is an Issue.
Per-item context (CLAUDE.md, content.md) lives in `texts/{folder}/`. No custom code — everything
goes through `gh issue` and `gh api`.

**SoC: README = canonical schema + ops reference. This skill = intent→command mapping.**
If anything in this skill contradicts the README, the README wins.

## Setup (first-time)

Labels must exist on the repo before use. Run once:
```bash
for label in status:queued status:reading status:done status:abandoned \
             type:book type:article type:paper type:post; do
  gh label create "$label" --repo brfid/readings --force
done
```

## When to Use

Add, start, finish, note, search, query, discuss, or save reading items.
Query reading history via issue events.

**Do NOT use for:** general web research, literature reviews, note-taking outside the tracker.

## Architecture

- **GitHub Issues** — source of truth. Title = item name. Labels = status + type. Body = metadata frontmatter + link to texts/.
- **`texts/{folder}/`** — CLAUDE.md (agent context), content.md (saved content), conversations.md (discussion log; issue comments preferred for new discussions).
- **No custom code** — `gh issue` and `gh api` handle all CRUD, including folder creation via the Contents API. No local clone is required for any operation.

## Intent → Command

Set `REPO=brfid/readings`. All commands run directly against GitHub — no local clone needed.
**The README is the canonical schema + ops reference.** Labels, body template, folder-naming
rules, and full commands are at https://github.com/brfid/readings#readme — load it if unsure.
This skill adds only the intent→command mapping.

**Finding the issue number** for a given title — run this once at the start, store the number:
```bash
N=$(gh issue list --search "title" --repo "$REPO" --json number --jq '.[0].number')
```

| Intent | Command |
|--------|---------|
| **Add** | See README "Operations" — creates `texts/<folder>/` via Contents API, then `gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "..."` |
| **Start** | `N=$(...); gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo $REPO` |
| **Finish** | `N=$(...); gh issue edit $N --add-label "status:done" --remove-label "status:reading" --repo $REPO && gh issue close $N --reason completed --repo $REPO` |
| **Note** | `N=$(...); gh issue comment $N --body "NOTE TEXT" --repo $REPO` |
| **Fact** | Update the issue body: `N=$(...); gh issue view $N --json body --jq .body ...` then `gh issue edit $N --body "..."`. Or just add a comment with the fact. |
| **Discuss** | `N=$(...); gh issue comment $N --body "DISCUSSION TEXT" --repo $REPO` |
| **Save** | Fetch URL → write `texts/{folder}/content.md` via the Contents API. No issue operation needed. |
| **Query** | `gh issue list --label "status:reading" --repo $REPO` (or `status:queued`, `status:done --state closed`) |
| **Search** | `gh issue list --search "keyword in:title,in:body" --repo $REPO` |
| **History** | `N=$(...); gh api "/repos/$REPO/issues/$N/events" --jq '.[] \| "\(.created_at)  \(.event)  \(.label.name // "")"'` |

## Labels & Body Template

See [README](https://github.com/brfid/readings#readme) — canonical reference. Quick reference below.

**Status labels:** `status:queued` (backlog), `status:reading`, `status:done` (close issue), `status:abandoned` (close --reason "not planned")
**Type labels:** `type:book`, `type:article`, `type:paper`, `type:post`

Body template (see README for full format): Author, Type, Location, optional Published/Publisher/ISBN/Rating, then link to `texts/folder/CLAUDE.md`.

## Matching Items

`gh issue list --search` handles fuzzy matching natively. For exact title match:
```bash
N=$(gh issue list --search "TITLE in:title" --repo $REPO --json number --jq '.[0].number')
```

If empty/ambiguous, `gh issue list --search "partial match in:title"` shows candidates.

## Texts Folders

See README "Folder naming" for the naming rule and README "Operations" → Add for the exact
`gh api` commands that create `texts/{folder}/CLAUDE.md` and `conversations.md`.

## Reference Files

- `references/folder-agent-template.md` — CLAUDE.md/conversations.md generation and update rules for `texts/{folder}/`.

## Notes

- `gh` CLI must be authenticated and have `repo` scope.
- Issue body edits for facts: `gh issue view N --json body` → modify → `gh issue edit N --body "..."`
- Timeline events show all label changes + comments with timestamps.
- `conversations.md` files serve as local discussion log; issue comments are preferred for new discussions.
