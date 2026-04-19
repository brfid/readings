---
name: reading-tracker
description: "Track reading across all formats via natural language. Use when adding items, changing status, querying by status, or searching reading history."
argument-hint: "[natural language: add, start, finish, query, search, or update notes]"
---

# Reading Tracker

Manage a personal reading list stored as YAML in a GitHub repo. Supports books, articles, papers, podcasts, videos, and courses.

## Configuration

Target repo: !`echo "${READING_TRACKER_REPO:-$(cat ~/.config/reading-tracker/config.yaml 2>/dev/null | grep -E '^repo:' | head -1 | sed 's/repo: *//')}" | grep -v '^$' || echo '__NO_CONFIG__'`

If the resolved value above is `__NO_CONFIG__`, do not proceed. Instead, tell the user:

> No reading tracker repo configured. Set one of:
>
> **Option A (recommended):** Add to your shell profile:
> ```
> export READING_TRACKER_REPO=owner/repo
> ```
>
> **Option B:** Create `~/.config/reading-tracker/config.yaml`:
> ```yaml
> repo: owner/repo
> ```
>
> Then restart Claude Code.

Stop here if not configured. Do not attempt any API calls.

## User Request

<user_request> #$ARGUMENTS </user_request>

If the user request above is empty, ask: "What would you like to do with your reading list?"

## Intent Classification

Determine the operation from the user's natural language:

| Intent | Trigger examples | Operation |
|--------|-----------------|-----------|
| **Add** | "add DDIA", "track this article https://..." | Append new item |
| **Start** | "started DDIA", "reading DDIA now" | Set status → `reading` |
| **Finish** | "finished DDIA", "done with DDIA" | Set status → `done` |
| **Query by status** | "what am I reading?", "show my backlog" | Filter + display |
| **Search** | "what have I read about distributed systems?" | Search labels, URLs, notes |
| **Update notes** | "add note to DDIA: chapter 5 is great" | Append to notes field |

If intent is unclear, ask the user to clarify. Do not guess.

## Reading the Current State

Fetch the reading list:

```bash
gh api /repos/{REPO}/contents/reading.yaml
```

Where `{REPO}` is the configured repo value (e.g., `owner/repo`).

From the response JSON:
- Decode the `content` field (base64) to get the YAML text
- Parse the YAML to get the items list
- Save the `sha` field — required for writes

The branch is always `main`.

## YAML Schema

```yaml
version: 1
items:
  - label: "DDIA"
    url: "https://dataintensive.net"
    status: reading
    notes: "Chapter 5 is great"
  - url: "https://example.com/article"
    status: want-to-read
```

Field rules:
- `url` or `path` — at least one required. `url` for web resources, `path` for local files in `texts/`
- `label` — optional human-friendly name. Store when provided, omit when not
- `status` — one of: `want-to-read`, `reading`, `done`. Default `want-to-read` on add
- `notes` — optional freeform string

No date fields. Git history provides the timeline.

## Executing Operations

### Read-Only Operations (Query, Search)

For queries and searches, read the YAML and answer directly. No write needed.

- **Query by status:** Filter items by `status` field, display matching items
- **Search:** Match the user's terms against `label`, `url`, and `notes` fields. Use judgment to find best matches — fuzzy/semantic matching is fine

### Write Operations (Add, Start, Finish, Update Notes)

Every write follows this cycle:

**Step 1 — Read current state** (as described above). Extract `sha`.

**Step 2 — Modify in memory.**

For **Add**:
- Check if an item with the same URL already exists. If so, ask whether to update or skip
- Build the new item with only the fields the user provided. Do not prompt for missing optional fields
- Append to the `items` list
- Default status: `want-to-read`

For **Start/Finish**:
- Match the user's reference against labels, URLs, and notes
- If exactly one match: update its status (`reading` for start, `done` for finish)
- If multiple matches: ask the user to disambiguate
- If no match: ask if they want to add it as a new item

For **Update Notes**:
- Match the item as above
- Append to or replace the `notes` field based on user intent

**Step 3 — Write back.**

```bash
gh api -X PUT /repos/{REPO}/contents/reading.yaml \
  -f message="COMMIT_MESSAGE" \
  -f content="BASE64_ENCODED_YAML" \
  -f sha="SHA_FROM_GET"
```

The `content` field must be the full modified YAML, base64-encoded.

Commit messages follow these patterns:
- `Add: {label or url}`
- `Started: {label or url}`
- `Finished: {label or url}`
- `Update notes: {label or url}`

**Step 4 — Handle response.**
- Success: confirm what was done
- 409 Conflict: tell the user there was a conflict and to try again
- Other errors: surface the error message directly

## Matching Items

Use judgment to match the user's reference to items in the list. Check against `label`, `url`, and `notes`. The user might say "DDIA" to match label "Designing Data-Intensive Applications", or paste a partial URL.

- Exact match on label or URL → proceed
- Single fuzzy match → proceed
- Multiple plausible matches → ask user to pick
- No match → ask user if they want to add it
