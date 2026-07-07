---
name: reads
description: "Use when tracking reading via brfid/reads GitHub Issues — add items, update status, query, search, discuss, capture facts, or drain the cross-profile queue."
version: 4.0.0
author: Brad Fidler
license: MIT
metadata:
  hermes:
    tags: [reading, tracking, github, issues]
    related_skills: [github-repo-management]
---

# Reads

Personal reading tracker: GitHub Issues on `brfid/reads`. Every reading item is an Issue.
Per-item context (CLAUDE.md, content.md) lives in `texts/{folder}/`. No custom code — everything
goes through `gh issue` and `gh api`.

**SoC: README = canonical schema + ops reference. This skill = intent→command mapping + pre-flight logic.**
If anything in this skill contradicts the README, the README wins. Other profiles only need the
README's "Queue item" command; they don't need this full skill.

## Setup (first-time)

Labels must exist on the repo before use. Run once:
```bash
for label in status:queued status:reading status:done status:abandoned \
             type:book type:article type:paper type:post \
             from:jinny from:manual; do
  gh label create "$label" --repo brfid/reads --force
done
```

## When to Use

Add, start, finish, note, search, query, discuss, or save reading items.
Drain the cross-profile queue. Query reading history via issue events.

**Do NOT use for:** general web research, literature reviews, note-taking outside the tracker.

## Architecture

- **GitHub Issues** — source of truth. Title = item name. Labels = status + type. Body = metadata frontmatter + links to texts/.
- **`texts/{folder}/`** — CLAUDE.md (agent context), content.md (saved content), conversations.md (discussion log; issue comments preferred for new discussions).
- **Cross-profile queue** — other profiles run `gh issue create --title "..." --label "status:queued,from:jinny" --repo brfid/reads`.
- **No custom code** — `gh issue` handles all CRUD.

## Pre-Flight

```bash
gh issue list --label "status:queued" --repo brfid/reads
```

If items with `from:` label exist, ask user to drain. Otherwise proceed.

**Most operations need no local clone** — `gh issue` and `gh api` work directly against the repo.
Only **Add** and **Queue Drain** create `texts/{folder}/` files and need the local clone:

```bash
cd ~/.hermes/profiles/bede/workspace/reads && git pull --rebase
```

## Intent → Command

Set `REPO=brfid/reads`. All commands run directly — no local clone needed except Add/Drain.
**The README is the canonical schema + ops reference.** Labels, body template,
and commands are at https://github.com/brfid/reads#readme — load it if unsure.
This skill adds only the intent→command mapping and pre-flight logic.

**Finding the issue number** for a given title — run this once at the start, store the number:
```bash
N=$(gh issue list --search "title" --repo "$REPO" --json number --jq '.[0].number')
```

| Intent | Command |
|--------|---------|
| **Add** | `gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "**Author(s):** AUTHORS\n**Type:** TYPE\n**Location:** URL\n\n[Agent context](texts/folder/CLAUDE.md)" --repo $REPO` |
| **Start** | `N=$(...); gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo $REPO` |
| **Finish** | `N=$(...); gh issue edit $N --add-label "status:done" --remove-label "status:reading" --repo $REPO && gh issue close $N --reason completed --repo $REPO` |
| **Note** | `N=$(...); gh issue comment $N --body "NOTE TEXT" --repo $REPO` |
| **Fact** | Update the issue body: `N=$(...); gh issue view $N --json body --jq .body ...` then `gh issue edit $N --body "..."`. Or just add a comment with the fact. |
| **Discuss** | `N=$(...); gh issue comment $N --body "DISCUSSION TEXT" --repo $REPO` |
| **Save** | Fetch URL → write `texts/{folder}/content.md`. No issue operation needed. |
| **Query** | `gh issue list --label "status:reading" --repo $REPO` (or `status:queued`, `status:done --state closed`) |
| **Search** | `gh issue list --search "keyword in:title,in:body" --repo $REPO` |
| **History** | `N=$(...); gh api "/repos/$REPO/issues/$N/events" --jq '.[] \| "\(.created_at)  \(.event)  \(.label.name // "")"'` |
| **README** | No README — browse GitHub Issues UI at `https://github.com/brfid/reads/issues` filtered by label |
| **Queue Add** | (other profile) `gh issue create --title "TITLE" --label "status:queued,from:PROFILE,type:TYPE" --repo brfid/reads` |
| **Queue Drain** | List `status:queued` issues. For each: create `texts/{folder}/` with CLAUDE.md + conversations.md (do NOT create a new issue — it already exists from Queue Add). Then git add/commit/push, and `gh issue edit N --add-label "status:reading" --remove-label "status:queued"`. |

## Labels & Body Template

See [README](https://github.com/brfid/reads#readme) — canonical reference. Quick reference below.

**Status labels:** `status:queued` (backlog), `status:reading`, `status:done` (close issue), `status:abandoned` (close --reason "not planned")
**Type labels:** `type:book`, `type:article`, `type:paper`, `type:post`
**Queue labels:** `from:jinny`, `from:manual`

Body template (see README for full format): Author, Type, Location, optional Published/Publisher/ISBN/Rating, then link to `texts/folder/CLAUDE.md`.

## Matching Items

`gh issue list --search` handles fuzzy matching natively. For exact title match:
```bash
N=$(gh issue list --search "TITLE in:title" --repo $REPO --json number --jq '.[0].number')
```

If empty/ambiguous, `gh issue list --search "partial match in:title"` shows candidates.

## Texts Folders

On Add, create `texts/{folder}/` with CLAUDE.md and conversations.md:
```bash
mkdir -p texts/{folder}
echo "# TITLE\n\n**Status:** queued\n**Location:** URL" > texts/{folder}/CLAUDE.md
touch texts/{folder}/conversations.md
git add texts/{folder} && git commit -m "add TITLE" && git push
```

Folder name: lowercase, hyphens, strip leading articles, max 40 chars. Collisions: `-2`, `-3`, etc.

## Reference Files

- `references/e2e-pipeline-readings.md` — Brad's canonical pipeline/CI/CD reading list. Load when user references "e2e readings" or asks about pipeline reading backlog.

## Notes

- `gh` CLI must be authenticated and have repo scope.
- Issue body edits for facts: `gh issue view N --json body` → modify → `gh issue edit N --body "..."`
- Timeline events show all label changes + comments with timestamps.
- `conversations.md` files serve as local discussion log; issue comments are preferred for new discussions.