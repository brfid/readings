---
name: reads
description: "Track reading via natural language. Add items, change status, query, search, discuss."
argument-hint: "[add, start, finish, query, search, notes, discuss, save, or anything about a tracked item]"
---

# Reads

Personal reading list as YAML in a GitHub repo. Each item gets a folder in `texts/` — standalone agent context with CLAUDE.md, conversation history, optional reading material. Folder is the agent: same model, different folder, different specialist.

## Configuration

Resolve target repo — check in order:

1. Environment variable `READS_REPO` (check via Bash: `echo $READS_REPO`)
2. Config file `~/.config/reads/config.yaml` (read with Read tool, extract `repo:` value)

Use the first non-empty value found. Validate format: `owner/repo` (e.g., `brfid/reads`).

If invalid format, stop. Tell user:

> Invalid repo format. Expected `owner/repo` (e.g., `brfid/reads`). Check config for typos.

If no value found, stop. Tell user:

> No repo configured. Set one:
>
> **Option A (recommended):** Shell profile:
> ```
> export READS_REPO=owner/repo
> ```
>
> **Option B:** Create `~/.config/reads/config.yaml`:
> ```yaml
> repo: owner/repo
> ```
>
> Restart Claude Code.

Stop here if not configured. No API calls.

## User Request

<user_request> #$ARGUMENTS </user_request>

If empty, ask: "What do you want to do with your reads?"

## Intent Classification

Determine operation from natural language:

| Intent | Triggers | Operation |
|--------|----------|-----------|
| **Add** | "add DDIA", "track https://..." | Append item + create folder |
| **Start** | "started DDIA", "reading now" | Status → `reading` |
| **Finish** | "finished DDIA", "done with DDIA" | Status → `done` |
| **Query** | "what am I reading?", "show backlog" | Filter + display |
| **Search** | "what about distributed systems?" | Search labels, URLs, notes, conversations |
| **Notes** | "note on DDIA: chapter 5 great" | Append to notes field |
| **Discuss** | "discuss DDIA", "continue DDIA" | Load folder context + converse |
| **Save** | "save compound engineering", "download DDIA", "capture article", "make a copy" | Fetch URL content → write `content.md` |
| **General** | anything else about a tracked item | Use tools + judgment to fulfill the request |

Unclear intent with no identifiable item → ask. Don't guess.

**General intent:** When user request doesn't fit a predefined intent but relates to a tracked item or the reading system, use available tools (Bash, WebFetch, Read, Write, gh API) and judgment to fulfill it. Examples: "download a local copy", "summarize what I've read", "compare two items", "show me the folder". Don't reject requests just because they lack a named intent.

## Reading Current State

Fetch reading list:

```bash
gh api /repos/{REPO}/contents/reading.yaml
```

`{REPO}` = configured repo value.

**404** → file doesn't exist. Create with PUT (no `sha`):
```yaml
version: 1
items: []
```
Then proceed with operation.

**Success** → from response JSON:
- Decode `content` (base64) → YAML text
- Parse YAML → items list
- Save `sha` — required for writes

Branch: always `main`.

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
- `url` or `path` — at least one required
- `label` — optional. Store when provided, omit when not
- `status` — `want-to-read` | `reading` | `done`. Default `want-to-read`. Normalize synonyms: `in-progress`/`currently-reading` → `reading`, `completed`/`finished` → `done`, `backlog`/`queued`/`tbr` → `want-to-read`
- `notes` — optional freeform string

No date fields. Git history = timeline.

**YAML string safety:** Double-quote values containing `: { } [ ] , & * # ? | - < > = ! % @ \`. When in doubt, quote.

## Folder as Agent

Each item gets folder in `texts/` — self-contained agent context. Model enters folder, becomes specialist.

`reading.yaml` = source of truth for status. `Status:` in folder CLAUDE.md is derived — update to match on write, but on conflict `reading.yaml` wins.

Structure:

```
texts/ddia/
  CLAUDE.md           # agent identity — auto-loads in directory
  conversations.md    # discussion themes
  content.md          # reading material (saved by skill or manual)
```

See `references/folder-agent-template.md` for templates and naming rules.

### Folder Creation

Create on **Add**. Every new item gets identity-only CLAUDE.md (title, status, URL) + empty conversations.md. No empty sections.

### Folder Updates

Update when interaction produces resumable content:

- **Discuss** — always update both files
- **Notes** with context/commentary — update conversations.md
- **Start/Finish** with reasoning/reflection — update conversations.md

Bare status changes (`started X`, `finished X`) with no discussion → no folder update.

1. **conversations.md** — append entry: what discussed, key points, where left off, open threads. Primary resumability mechanism. Enough specifics for cold-start pickup.

2. **CLAUDE.md** — add/update sections from available set (see template). Only add sections with real content. Never empty sections.

## Executing Operations

### Read-Only (Query, Search)

Read YAML, answer directly. No write.

- **Query:** Filter by `status`, display matches
- **Search:** Match terms against `label`, `url`, `notes`, and folder `conversations.md`. 404 on conversations.md → skip, search YAML fields only. Use judgment for fuzzy/semantic matching

### Discuss

Load folder context, resume conversation:

1. Match item in reading.yaml
2. Fetch `texts/{folder}/CLAUDE.md`, `texts/{folder}/conversations.md`, `texts/{folder}/content.md` via API
3. Present reading context, themes, open questions. If content.md exists, use as grounded material
4. Converse — folder context provides continuity
5. After discussion, append summary to `conversations.md`, update `CLAUDE.md`

Missing content.md → skip silently.

### Save

Fetch text content from item URL, convert to markdown, commit as `content.md` in item folder.

1. Match item in reading.yaml
2. Verify item has `url` — if not, tell user save requires URL
3. Check if `texts/{folder}/content.md` exists (GET) — if exists, save `sha` from response, ask update or skip
4. Fetch URL content and convert to markdown
5. Prepend source header:
   ```
   Source: {url}
   Saved: {YYYY-MM-DD}
   ```
6. PUT `content.md` via GitHub API (new file omit sha, existing file include sha)
7. Commit: `save {label or url}`

**Markdown quality:** CommonMark / GFM. Preserve heading hierarchy, links, emphasis, lists, code blocks, tables, blockquotes, footnotes. Strip nav, ads, sidebars, footers, newsletter prompts. Preserve author attribution + publication date if visible. No script-based HTML→markdown conversion — read the page and write clean markdown directly.

Scope: text-based web content (articles, essays, guides, blog posts). Non-text (video, podcast) → tell user. Fetch failure → surface error, suggest checking URL. Paywall/login page → detect and report.

### General

For requests that don't match a predefined intent: use available tools and judgment. Read files, fetch URLs, run commands, write locally — whatever fulfills the request. Match the item first if one is referenced, then operate on its data.

### Write Operations (Add, Start, Finish, Notes)

Every write follows this cycle:

**Step 1 — Read current state.** Extract `sha`.

**Step 2 — Modify in memory.**

**Add:**
- Check duplicate URL → ask update or skip
- Derive folder name (see `references/folder-agent-template.md`)
- Check `path` collision → append suffix (`-2`, `-3`)
- Build item with provided fields only. Don't prompt for missing optionals
- Set `path` to `texts/{folder-name}`
- Append to items list
- Default status: `want-to-read`

**Start/Finish:**
- Match reference against labels, URLs, notes
- One match → update status (`reading` / `done`)
- Multiple → ask to disambiguate
- None → ask if they want to add

**Notes:**
- Match item
- Default: **append** with newline separator
- **Replace** only on explicit "replace", "set notes to", "clear and add"

**Step 3 — Write reading.yaml.**

```bash
gh api -X PUT /repos/{REPO}/contents/reading.yaml \
  -f message="COMMIT_MESSAGE" \
  -f content="BASE64_ENCODED_YAML" \
  -f sha="SHA_FROM_GET"
```

`content` = full modified YAML, base64-encoded.

Commit messages — minimal, operation + identifier:
- `add {label or url}`
- `started {label or url}`
- `finished {label or url}`
- `note {label or url}`
- `init {label or url}` — folder creation
- `discuss {label or url}` — folder updates after discussion
- `context {label or url}` — other folder updates
- `save {label or url}` — content.md creation

**Step 4 — Create/update folder** (Add, Discuss, substantive interactions).

**Add** — two PUT calls:

1. `texts/{folder-name}/CLAUDE.md` — from template
2. `texts/{folder-name}/conversations.md` — empty file

New file PUTs omit `sha`:

```bash
gh api -X PUT /repos/{REPO}/contents/texts/{folder-name}/CLAUDE.md \
  -f message="context {label or url}" \
  -f content="BASE64_ENCODED_CONTENT"
```

Existing folder file updates → GET for `sha` first, then PUT with modified content + `sha`.

**Step 5 — Handle response.**
- Success → confirm
- 409 on reading.yaml → re-GET, re-apply, retry (up to 2)
- 409 on folder file → file exists, GET sha, PUT as update
- 422 → surface error
- 5xx → surface error, suggest retry

## Matching Items

Match reference against `label`, `url`, `path`, `notes`. Priority:

1. **Exact** on label or URL → proceed
2. **Substring/abbreviation** — "DDIA" matches "Designing Data-Intensive Applications", "raft" matches `texts/raft-paper`
3. **Semantic** — "that distributed systems book" matches DDIA if only item on topic

Resolution:
- Single confident match → proceed
- Multiple plausible → ask user, show labels + URLs
- No match → ask if they want to add
