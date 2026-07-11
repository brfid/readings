# Reading Tracker

GitHub Issues are the source of truth.

## Schema

- **Title** — item name
- **Labels** — `status:{queued,reading,done,abandoned}` + `type:{book,article,paper,post}` + optional `reread` flag
- **Body** — key:value frontmatter, then links to `texts/{folder}/`
- **Comments** — discussion log
- **Queue** — other agents create issues with label `from:{profile}`. `from:` marks *source*, not handler — bede adding an item directly (including a reread) gets no `from:` label at all; `from:bede` is reserved for items sourced from the Miniflux collector.
- **`reread`** — orthogonal flag, any medium (not just books). Tense comes from the paired `status:` label (`status:queued`+`reread` = planning to reread, `status:reading`+`reread` = mid-reread, `status:done`+`reread` = have reread), not from the flag itself. Persists through close so reread history stays queryable.
- **No unsolicited notes** — Add/Reread bodies hold only the frontmatter fields supplied; no summaries or commentary unless asked for as a separate Note.

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
# Add item (bede profile only — creates texts/{folder}/ via Contents API, no local clone)
gh api --method PUT "repos/brfid/readings/contents/texts/<folder>/CLAUDE.md" \
  -f message="add TITLE" \
  -f content="$(printf '# TITLE\n\n**Status:** queued\n**Location:** URL' | base64 -w0)"
gh api --method PUT "repos/brfid/readings/contents/texts/<folder>/conversations.md" \
  -f message="add TITLE" \
  -f content="$(printf '' | base64 -w0)"
gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "**Author(s):** NAME
**Type:** TYPE
**Location:** URL

[Agent context](texts/<folder>/CLAUDE.md)" --repo brfid/readings

# Queue item (any profile)
gh issue create --title "TITLE" --label "status:queued,from:veblen,type:book" --repo brfid/readings

# Query
gh issue list --label "status:reading" --repo brfid/readings

# Search
gh issue list --search "keyword in:title,in:body" --repo brfid/readings

# Start reading
N=$(gh issue list --search "TITLE in:title" --repo brfid/readings --json number --jq '.[0].number')
gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo brfid/readings

# Finish
gh issue edit $N --add-label "status:done" --remove-label "status:reading" --repo brfid/readings
gh issue close $N --reason completed --repo brfid/readings

# Reread — already tracked (issue exists, status:done): reopen + relabel
gh issue reopen $N --repo brfid/readings
gh issue edit $N --add-label "reread,status:reading" --remove-label "status:done" --repo brfid/readings
# ... then Finish as normal; "reread" persists through close

# Reread — not yet tracked (no prior issue, e.g. read before this tracker existed)
# No from: label, no texts/{folder}/ scaffolding, no [Agent context] link, no editorializing.
gh issue create --title "TITLE" --label "status:queued,type:TYPE,reread" --body "**Author(s):** NAME
**Type:** TYPE
**Location:** URL" --repo brfid/readings

# Note / discuss
gh issue comment $N --body "NOTE" --repo brfid/readings

# Timeline
gh api "/repos/brfid/readings/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```

## Repo layout

```
texts/{folder}/
  CLAUDE.md         # agent identity + reading context
  content.md        # saved article (optional)
  conversations.md  # discussion log (issue comments preferred for new discussions)
```