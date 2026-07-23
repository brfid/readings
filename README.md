# Reading Tracker

GitHub Issues are the source of truth. Any agent with the `gh` CLI, authenticated
with `repo` scope against this repository, can run every operation below directly —
no local clone required.

## Design principles

- **A dimension you query on is a label; everything else is body text.** Never store the
  same fact in both. Status, type, and rating are labels — they don't appear in the body.
- **Store only what you can't derive.** If the URL's domain already tells you the publisher,
  don't record the publisher.
- **Record enough to survive link rot.** Author + year make a dead item re-findable; an
  archive snapshot preserves the actual text. Capture both when the source is on the web.
- **No files.** No per-reading files or folders, no saved copies. Frontmatter lives in the
  issue body; notes and discussion live in issue comments.
- **Dates come from the issue, not the body.** Created = logged, closed = finished; the
  archive URL carries its own capture datetime. Don't add date fields.

## Schema

### Labels (the queryable dimensions)

- `status:{queued,reading,done,abandoned}`
- `type:{book,article,paper,post}`
- `rating:{1,2,3,4,5}` — optional, added when finished
- `reread` — optional flag, any medium. Tense comes from the paired `status:` label
  (`queued`+`reread` = planning to reread, `reading`+`reread` = mid-reread,
  `done`+`reread` = have reread). Persists through close so reread history stays queryable.

### Body (frontmatter only — no `Type`, no `Status`, no `Rating`; those are labels)

Record only the fields that apply and that aren't already implied by the link:

- **Author(s)** — always (it's what makes a dead link re-findable)
- **Published** — year (or full date), optional
- **Persistent identifier** — the rot-proof handle for the work:
  - book → **ISBN** (13-digit)
  - paper → **DOI** or arXiv ID (omit if it genuinely has none)
- **Publisher** — books, and web items **only when the host isn't the publisher**
  (a self-hosted PDF, mirror, or republication — e.g. a *Datamation* paper served from a
  personal site). Skip it when the domain already is the publisher (`github.blog` → GitHub).
- **Location** — the URL, or `Books app` for physical/ebook copies
- **Archived** — a verified Wayback (or archive.today) snapshot of the URL; the guard
  against link rot. Web items only. Omit if the source can't be archived (see below).

## Setup (one-time)

```
for label in status:queued status:reading status:done status:abandoned \
             type:book type:article type:paper type:post \
             rating:1 rating:2 rating:3 rating:4 rating:5 reread; do
  gh label create "$label" --repo brfid/readings --force
done
```

## Issue body templates

```
# Web item (article / paper / post)
**Author(s):** Name
**Published:** YYYY
**DOI:** 10.xxxx/...            # papers with a DOI only
**Location:** https://...
**Archived:** https://web.archive.org/web/<timestamp>/https://...

# Book
**Author(s):** Name
**Published:** YYYY
**Publisher:** Name
**ISBN:** 978-...
**Location:** Books app
```

## Archiving (link-rot guard)

Capture a snapshot when logging a web item, and **verify it actually captured** — a silent
failure (Cloudflare block, soft 404, paywall wall) is worse than none.

```
URL="https://example.com/post"
# Reuse an existing snapshot if there is one...
SNAP=$(curl -s "https://archive.org/wayback/available?url=$URL" \
  | python3 -c 'import sys,json;s=json.load(sys.stdin).get("archived_snapshots",{}).get("closest",{});print(s["url"] if s.get("available") and str(s.get("status"))=="200" else "")')
# ...otherwise trigger a fresh capture, then re-check availability:
[ -z "$SNAP" ] && curl -s "https://web.archive.org/save/$URL" -o /dev/null
```

If `$SNAP` is still empty (e.g. every.to returns HTTP 520 behind Cloudflare), the URL is
not archivable via Wayback — try archive.today manually, or accept that the original link
is the only copy and omit `**Archived:**`.

## Operations (gh CLI)

```
# Add item — archive first (web items), then create the issue with the snapshot URL
gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "**Author(s):** NAME
**Location:** URL
**Archived:** SNAPSHOT" --repo brfid/readings

# Query
gh issue list --label "status:reading" --repo brfid/readings
gh issue list --label "rating:5" --state all --repo brfid/readings   # by rating

# Search
gh issue list --search "keyword in:title,in:body" --repo brfid/readings

# Start reading
N=$(gh issue list --search "TITLE in:title" --repo brfid/readings --json number --jq '.[0].number')
gh issue edit $N --add-label "status:reading" --remove-label "status:queued" --repo brfid/readings

# Finish (add rating if you have one)
gh issue edit $N --add-label "status:done,rating:4" --remove-label "status:reading" --repo brfid/readings
gh issue close $N --reason completed --repo brfid/readings

# Reread — already tracked (issue exists, status:done): reopen + relabel
gh issue reopen $N --repo brfid/readings
gh issue edit $N --add-label "reread,status:reading" --remove-label "status:done" --repo brfid/readings
# ... then Finish as normal; "reread" persists through close

# Reread — not yet tracked (no prior issue, e.g. read before this tracker existed)
gh issue create --title "TITLE" --label "status:queued,type:TYPE,reread" --body "**Author(s):** NAME
**Location:** URL" --repo brfid/readings

# Note / discuss (notes live in comments, never in files)
gh issue comment $N --body "NOTE" --repo brfid/readings

# Timeline (the "when" — logged / started / finished)
gh api "/repos/brfid/readings/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```
