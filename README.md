# Reading Tracker

LLM-driven personal reading tracker. Add books, articles, papers, podcasts, videos, and courses via natural language through Claude Code.

Data lives in `reading.yaml`. Git history provides the timeline — no date fields needed.

## Install

Add this repo as a Claude Code plugin marketplace, then install:

```sh
claude plugins marketplace add https://github.com/brfid/reading-tracker
claude plugins install reading-tracker
```

## Configure

Set the target repo. Pick one:

**Option A** — environment variable (recommended):

```sh
export READING_TRACKER_REPO=brfid/reading-tracker
```

Add to your shell profile (`.zshrc`, `.bashrc`, etc.) and restart Claude Code.

**Option B** — config file:

Create `~/.config/reading-tracker/config.yaml`:

```yaml
repo: brfid/reading-tracker
```

## Usage

Invoke the skill in Claude Code with natural language:

```
/reading-tracker add DDIA https://dataintensive.net
/reading-tracker started DDIA
/reading-tracker finished DDIA
/reading-tracker what am I reading?
/reading-tracker what have I read about distributed systems?
/reading-tracker add note to DDIA: chapter 5 is great
```

Or add an item with just a URL:

```
/reading-tracker add https://example.com/interesting-article
```

## Schema

`reading.yaml` at the repo root:

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

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `url` | one of `url`/`path` | Web URL |
| `path` | one of `url`/`path` | Path to local file in `texts/` |
| `label` | no | Human-friendly name |
| `status` | yes | `want-to-read`, `reading`, or `done` |
| `notes` | no | Freeform notes |

### Statuses

- `want-to-read` — default when adding
- `reading` — in progress
- `done` — finished

## `texts/` Directory

Store local copies of reading material (markdown, plain text) in `texts/`. This directory is user-managed — the skill does not write to it. Reference files here using the `path` field on items.

## How It Works

The skill uses the GitHub REST Contents API for all reads and writes — no local clone needed. Each operation:

1. GET `reading.yaml` → decode base64 → parse YAML → save SHA
2. Modify in memory
3. PUT with modified content + SHA from step 1
4. Descriptive commit message (e.g., "Add: DDIA", "Finished: DDIA")

## License

MIT
