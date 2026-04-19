# Reading Tracker

LLM-driven personal reading tracker. Add books, articles, papers, podcasts, videos, and courses via natural language through Claude Code.

Data lives in `reading.yaml`. Each item gets a folder in `texts/` that serves as a self-contained agent context — drop into any folder and the LLM picks up where you left off. Git history provides the timeline.

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
/reading-tracker let's discuss DDIA
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
    path: "texts/ddia"
    status: reading
    notes: "Chapter 5 is great"
  - url: "https://example.com/article"
    path: "texts/some-article"
    status: want-to-read
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `url` | one of `url`/`path` | Web URL |
| `path` | one of `url`/`path` | Item folder in `texts/` |
| `label` | no | Human-friendly name |
| `status` | yes | `want-to-read`, `reading`, or `done` |
| `notes` | no | Freeform notes |

### Statuses

- `want-to-read` — default when adding
- `reading` — in progress
- `done` — finished

## Design Principles

**Folder as agent.** An agent is not a framework or an orchestration layer — it's a model pointed at a folder with enough context that you don't have to re-explain everything each time. Different folder, same model, different specialist. Each reading item's folder is a self-contained agent context. See [The Folder Is the Agent](https://every.to/source-code/the-folder-is-the-agent) by Kieran Klaassen.

**Git as metadata.** No date fields, no timestamps in YAML. Git history is the timeline — commit messages record what happened, commit timestamps record when.

**LLM-native matching.** No algorithmic search or fuzzy matching code. The skill reads the data, the LLM uses judgment to match user references to items. Ambiguity is resolved by asking, not by heuristics.

**Two interaction modes.** Every feature works both remotely (via skill + GitHub API) and locally (via `cd` + CLAUDE.md auto-load). Both paths read and write the same files.

## Folder-Agent Pattern

Each reading item gets a folder in `texts/` that acts as an agent context:

```
texts/ddia/
  CLAUDE.md           # agent identity — auto-loads when you cd here
  conversations.md    # accumulated themes from discussions
  content.md          # reading material (user-managed, optional)
```

**Via skill:** `/reading-tracker let's discuss DDIA` loads the folder context remotely and resumes the conversation. After discussion, the skill updates `conversations.md` with themes and refreshes `CLAUDE.md`.

**Via folder:** `cd texts/ddia` in Claude Code — `CLAUDE.md` auto-loads and you're in context. No skill invocation needed.

Both paths converge on the same files.

## How It Works

The skill uses the GitHub REST Contents API for all reads and writes — no local clone needed. Each operation:

1. GET `reading.yaml` → decode base64 → parse YAML → save SHA
2. Modify in memory
3. PUT with modified content + SHA from step 1
4. Descriptive commit message (e.g., "Add: DDIA", "Finished: DDIA")
5. Create or update item folder (`CLAUDE.md`, `conversations.md`) as needed

## License

MIT
