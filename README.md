# Reading Tracker

GitHub Issues are the source of truth.

## Schema

- **Title** — item name
- **Labels** — `status:{queued,reading,done,abandoned}` + `type:{book,article,paper,post}`
- **Body** — key:value frontmatter, then links to `texts/{folder}/`
- **Comments** — discussion log
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
# Add item (bede profile only — creates texts/{folder}/)
mkdir -p texts/<folder>
printf '# TITLE\n\n**Status:** queued\n**Location:** URL' > texts/<folder>/CLAUDE.md
touch texts/<folder>/conversations.md
git add texts/<folder> && git commit -m "add TITLE" && git push
gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "**Author(s):** NAME
**Type:** TYPE
**Location:** URL

[Agent context](texts/<folder>/CLAUDE.md)" --repo brfid/reads

# Queue item (any profile)
gh issue create --title "TITLE" --label "status:queued,from:jinny,type:book" --repo brfid/reads

# Query
gh issue list --label "status:reading" --repo brfid/reads

# Search
gh issue list --search "keyword in:title,in:body" --repo brfid/reads

# Start reading
N=$(gh issue list --search "TITLE in:title" --repo brfid/reads --json number --jq '.[0].number')
gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo brfid/reads

# Finish
gh issue edit $N --add-label "status:done" --remove-label "status:reading" --repo brfid/reads
gh issue close $N --reason completed --repo brfid/reads

# Note / discuss
gh issue comment $N --body "NOTE" --repo brfid/reads

# Timeline
gh api "/repos/brfid/reads/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```

## Repo layout

```
texts/{folder}/
  CLAUDE.md         # agent identity + reading context
  content.md        # saved article (optional)
  conversations.md  # discussion log (issue comments preferred for new discussions)
```