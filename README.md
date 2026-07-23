# Reading Tracker

GitHub Issues are the source of truth. Any agent with the `gh` CLI, authenticated
with `repo` scope against this repository, can run every operation below directly —
no local clone required.

## Design principles

- **A dimension you query on is a label; everything else is body text.** Never store the
  same fact in both. Status and type are labels — they don't appear in the body.
- **Store only what you can't derive.** If the URL's domain already tells you the publisher,
  don't record the publisher.
- **Record enough to survive link rot.** Author + year make a dead item re-findable; an
  archive snapshot preserves the actual text. Capture both when the source is on the web.
- **No files.** No per-reading files or folders, no saved copies. Frontmatter lives in the
  issue body; commentary lives in issue comments (see below).
- **A field exists only when it has a value.** Never write a blank or placeholder field —
  omit it. This is why commentary is an issue comment, not a body field: no comment, no field.
- **Dates come from the issue, not the body.** Created = logged, closed = finished; the
  archive URL carries its own capture datetime. Don't add date fields.

## Schema

### Labels (the queryable dimensions)

- `status:{queued,reading,done,abandoned}`
- `type:{book,article,paper,post}`
- `reread` — optional flag, any medium. Tense comes from the paired `status:` label
  (`queued`+`reread` = planning to reread, `reading`+`reread` = mid-reread,
  `done`+`reread` = have reread). Persists through close so reread history stays queryable.

### Body (frontmatter only — no `Type` or `Status`; those are labels)

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
  against link rot. Web items only. Always try to capture one; if the source can't be
  archived (see below), fall back to the current URL so the field still points somewhere.

### Comments

Your own commentary — a reaction, a note, a quote worth keeping — goes in the issue's
**comment thread**, never in the body. A comment exists only once you write one, so there's
nothing blank to maintain. Discussion and follow-ups are just more comments on the same issue.

## Setup (one-time)

```
for label in status:queued status:reading status:done status:abandoned \
             type:book type:article type:paper type:post reread; do
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
not archivable via Wayback — try archive.today manually, or fall back to the current URL as
the `**Archived:**` value (`SNAP="$URL"`) so the field still resolves to something.

## Operations (gh CLI)

```
# Add item — archive first (web items), then create the issue with the snapshot URL
gh issue create --title "TITLE" --label "status:queued,type:TYPE" --body "**Author(s):** NAME
**Location:** URL
**Archived:** SNAPSHOT" --repo brfid/readings

# Query
gh issue list --label "status:reading" --repo brfid/readings
gh issue list --label "type:paper" --state all --repo brfid/readings

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
gh issue create --title "TITLE" --label "status:queued,type:TYPE,reread" --body "**Author(s):** NAME
**Location:** URL" --repo brfid/readings

# Comment / discuss (your commentary lives in comments, never in the body or a file)
gh issue comment $N --body "COMMENT" --repo brfid/readings

# Timeline (the "when" — logged / started / finished)
gh api "/repos/brfid/readings/issues/$N/events" --jq '.[] | "\(.created_at)  \(.event)  \(.label.name // "")"'
```
