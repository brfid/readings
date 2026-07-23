---
name: readings
description: "Use when adding to or updating the brfid/readings GitHub Issues reading tracker — add items, change status, comment, correct a fact, query, or search. Not for research or notes kept outside the tracker."
version: 6.0.0
author: Brad Fidler
license: MIT
metadata:
  tags: [reading, tracking, github, issues]
---

# Reads

Personal reading tracker: every item is a GitHub Issue on `brfid/readings`. No custom code and
**no files** — `gh issue` and `gh api` do everything. Metadata lives in the issue body,
commentary in issue comments; there is no per-item folder and no saved copy of any text.

**Separation of concerns.** The [README](../../README.md) is the canonical reference — labels,
body fields, the archiving recipe, and the publisher/identifier rules all live there. **This
skill is only the intent → command mapping.** Load the README (local path above, or
<https://github.com/brfid/readings#readme>) for any schema detail, and if the two ever
disagree, **the README wins.** Keeping schema in one place is deliberate: it's what stops this
skill from drifting out of date.

## When to use

Add / start / finish / abandon a reading item; comment or discuss; correct a metadata fact;
query or search the list; review an item's timeline.

**Do not use for:** general web research, literature reviews, or notes kept outside the tracker.

## Conventions

Run once per shell so every command can omit `--repo`:

```bash
export GH_REPO=brfid/readings
```

Find an item's issue number, then store and reuse it:

```bash
N=$(gh issue list --search "TITLE in:title" --json number --jq '.[0].number')
```

If that's empty or ambiguous, `gh issue list --search "partial in:title"` lists candidates.
First-time only: create the labels per README → **Setup**.

## Add an item

Web item (article / paper / post) — snapshot the URL first, then create:

```bash
# 1. Capture a verified snapshot (procedure + fallback: README → Archiving).
#    SNAP is a web.archive.org URL, or the original URL if the source can't be archived.
# 2. Create the issue. Full field rules (DOI for papers, when to include Publisher):
#    README → Schema ▸ Body. Minimum is Author + Location + Archived.
gh issue create --title "TITLE" --label "status:queued,type:post" --body "**Author(s):** NAME
**Published:** YEAR
**Location:** URL
**Archived:** $SNAP"
```

Book — no URL, no archive; include ISBN (and Publisher):

```bash
gh issue create --title "TITLE" --label "status:queued,type:book" --body "**Author(s):** NAME
**Published:** YEAR
**Publisher:** NAME
**ISBN:** 978-..."
```

## Status changes & other intents

| Intent | Command |
|--------|---------|
| **Start** | `gh issue edit $N --add-label status:reading --remove-label status:queued` |
| **Finish** | `gh issue edit $N --add-label status:done --remove-label status:reading && gh issue close $N --reason completed` |
| **Abandon** | `gh issue edit $N --add-label status:abandoned --remove-label status:queued && gh issue close $N --reason "not planned"` (use `--remove-label status:reading` if you'd started it) |
| **Comment / discuss** | `gh issue comment $N --body "COMMENT"` |
| **Correct a fact** | `gh issue view $N --json body --jq .body` → edit the text → `gh issue edit $N --body "..."` |
| **Query** | `gh issue list --label status:reading` (also `--label status:done --state closed`, `--label type:paper --state all`, …) |
| **Search** | `gh issue list --search "keyword in:title,in:body"` |

## Reread

- **Already tracked** (issue exists, `status:done`): `gh issue reopen $N && gh issue edit $N --add-label "reread,status:reading" --remove-label status:done`, then Finish as normal. `reread` persists through close.
- **Not tracked** (read before this tracker existed):

  ```bash
  gh issue create --title "TITLE" --label "status:queued,type:TYPE,reread" --body "**Author(s):** NAME
  **Location:** URL"
  ```

## Timeline

The "when" (logged / started / finished) comes from issue and label-change timestamps, never a
body field:

```bash
gh api "/repos/brfid/readings/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```

## Notes

- `gh` must be authenticated with `repo` scope.
- Never create a file or folder, and never save a copy of a text — the issue is the whole record.
