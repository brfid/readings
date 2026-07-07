# Reading Tracker

GitHub Issues are the source of truth. No custom code, no YAML, no CI.

## Schema

- **Title** — item name (e.g. "Designing Data-Intensive Applications")
- **Labels** — `status:{queued,reading,done,abandoned}` + `type:{book,article,paper,post}`
- **Body** — key:value frontmatter, then links to `texts/{folder}/`
- **Comments** — discussion log (replaces conversations.md)
- **Queue** — other agents create issues with label `from:{profile}`

## Issue body template

```
**Author(s):** Name
**Type:** book | article | paper | post
**Location:** URL or "Books app"
**Published:** YYYY
**Publisher:** Name
**ISBN:** 978-...
**Rating:** N/5

[Agent context](texts/folder/CLAUDE.md)
```

## Operations (gh CLI)

```
# Query
gh issue list --label "status:reading" --repo brfid/reads

# Start reading
N=$(gh issue list --search "TITLE in:title" --repo brfid/reads --json number --jq '.[0].number')
gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo brfid/reads

# Finish
gh issue edit $N --add-label "status:done" --remove-label "status:reading" --repo brfid/reads
gh issue close $N --reason completed --repo brfid/reads

# Timeline
gh api "/repos/brfid/reads/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```

## Repo layout

```
texts/{folder}/
  CLAUDE.md         # agent identity + reading context
  content.md        # saved article (optional)
  conversations.md  # legacy discussion log (prefer issue comments)
```

No `reading.yaml`, `reads.py`, `compile_meta.py`, `queue.yaml`, or CI workflows.