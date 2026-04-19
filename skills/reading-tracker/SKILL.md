---
name: reading-tracker
description: "Track reading across all formats via natural language. Use when adding items, changing status, querying by status, searching reading history, or discussing a reading item."
argument-hint: "[natural language: add, start, finish, query, search, update notes, or discuss]"
---

# Reading Tracker

Manage a personal reading list stored as YAML in a GitHub repo. Every item gets a folder in `texts/` that acts as a standalone agent context — CLAUDE.md, conversation history, and optional reading material. The folder is the agent: same model, different folder, different specialist.

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
| **Add** | "add DDIA", "track this article https://..." | Append new item + create folder |
| **Start** | "started DDIA", "reading DDIA now" | Set status → `reading` |
| **Finish** | "finished DDIA", "done with DDIA" | Set status → `done` |
| **Query by status** | "what am I reading?", "show my backlog" | Filter + display |
| **Search** | "what have I read about distributed systems?" | Search labels, URLs, notes, conversation history |
| **Update notes** | "add note to DDIA: chapter 5 is great" | Append to notes field |
| **Discuss** | "let's talk about DDIA", "continue DDIA discussion" | Load folder context + converse |

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
    path: "texts/ddia"
    status: reading
    notes: "Chapter 5 is great"
  - url: "https://example.com/article"
    path: "texts/some-article"
    status: want-to-read
```

Field rules:
- `url` or `path` — at least one required. `url` for web resources, `path` for item folder in `texts/`
- `label` — optional human-friendly name. Store when provided, omit when not
- `status` — one of: `want-to-read`, `reading`, `done`. Default `want-to-read` on add
- `notes` — optional freeform string

No date fields. Git history provides the timeline.

## Folder-Agent Pattern

Each reading item gets a folder in `texts/` that serves as a self-contained agent context. When a model enters the folder, it becomes a specialist in that item.

Structure per item:

```
texts/ddia/
  CLAUDE.md           # agent identity — auto-loads when working in this directory
  conversations.md    # accumulated themes from discussions
  content.md          # reading material (user-managed, optional)
```

Read `references/folder-agent-template.md` for the CLAUDE.md template, conversations.md format, and folder naming rules.

### When to create a folder

Create the folder on **Add**. Every new item gets a folder with a generated CLAUDE.md and empty conversations.md.

### When to update the folder

After any **substantive interaction** about an item (discussion, notes update, status change with context), append a summary to `conversations.md` and update the `CLAUDE.md` Reading Context section. Do not update for trivial status changes with no discussion.

## Executing Operations

### Read-Only Operations (Query, Search)

For queries and searches, read the YAML and answer directly. No write needed.

- **Query by status:** Filter items by `status` field, display matching items
- **Search:** Match the user's terms against `label`, `url`, `notes`, and — if the item has a folder — its `conversations.md`. Use judgment for fuzzy/semantic matching

### Discuss

Load the item's folder context to resume a conversation about it:

1. Match the item in reading.yaml
2. Fetch `texts/{folder}/CLAUDE.md` and `texts/{folder}/conversations.md` via API
3. Present the current reading context, key themes, and open questions
4. Converse naturally — the folder context provides continuity
5. After the discussion, append a summary to `conversations.md` and update `CLAUDE.md`

### Write Operations (Add, Start, Finish, Update Notes)

Every write follows this cycle:

**Step 1 — Read current state** (as described above). Extract `sha`.

**Step 2 — Modify in memory.**

For **Add**:
- Check if an item with the same URL already exists. If so, ask whether to update or skip
- Build the new item with only the fields the user provided. Do not prompt for missing optional fields
- Derive a folder name (see `references/folder-agent-template.md` for naming rules)
- Set `path` to `texts/{folder-name}`
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

**Step 3 — Write back reading.yaml.**

```bash
gh api -X PUT /repos/{REPO}/contents/reading.yaml \
  -f message="COMMIT_MESSAGE" \
  -f content="BASE64_ENCODED_YAML" \
  -f sha="SHA_FROM_GET"
```

The `content` field must be the full modified YAML, base64-encoded.

Commit messages must be minimal — just the operation and identifier:
- `add {label or url}`
- `started {label or url}`
- `finished {label or url}`
- `note {label or url}`
- `context {label or url}` (for folder file creates/updates)

**Step 4 — Create or update folder** (for Add, Discuss, and substantive interactions).

For **Add**, create two files via separate PUT calls:

1. `texts/{folder-name}/CLAUDE.md` — generated from template in `references/folder-agent-template.md`
2. `texts/{folder-name}/conversations.md` — empty file

Each PUT to a new file omits the `sha` field (file doesn't exist yet):

```bash
gh api -X PUT /repos/{REPO}/contents/texts/{folder-name}/CLAUDE.md \
  -f message="context {label or url}" \
  -f content="BASE64_ENCODED_CONTENT"
```

For **updates to existing folder files**, GET the file first to obtain its `sha`, then PUT with the modified content and `sha`.

**Step 5 — Handle response.**
- Success: confirm what was done
- 409 Conflict: tell the user there was a conflict and to try again
- Other errors: surface the error message directly

## Matching Items

Use judgment to match the user's reference to items in the list. Check against `label`, `url`, and `notes`. The user might say "DDIA" to match label "Designing Data-Intensive Applications", or paste a partial URL.

- Exact match on label or URL → proceed
- Single fuzzy match → proceed
- Multiple plausible matches → ask user to pick
- No match → ask user if they want to add it
