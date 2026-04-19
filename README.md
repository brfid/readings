# Reads

Personal reading tracker for Claude Code. Add books, articles, papers, podcasts, videos, courses — natural language, one command.

Data lives in `reading.yaml`. Each item gets a folder in `texts/` — self-contained agent context. Drop into any folder, LLM picks up where you left off. Git history is the timeline.

## Install

Add repo as Claude Code plugin marketplace, then install:

```sh
claude plugins marketplace add https://github.com/brfid/reads
claude plugins install reads
```

## Configure

Set target repo. Pick one:

**Option A** — env var (recommended):

```sh
export READS_REPO=brfid/reads
```

Add to shell profile (`.zshrc`, `.bashrc`), restart Claude Code.

**Option B** — config file:

Create `~/.config/reads/config.yaml`:

```yaml
repo: brfid/reads
```

## Usage

Natural language via Claude Code:

```
/reads add DDIA https://dataintensive.net
/reads started DDIA
/reads finished DDIA
/reads what am I reading?
/reads what have I read about distributed systems?
/reads add note to DDIA: chapter 5 is great
/reads let's discuss DDIA
/reads save compound engineering
```

Or just a URL:

```
/reads add https://example.com/interesting-article
```

## Schema

`reading.yaml` at repo root tracks all items. Each item: `url`, `path` (folder in `texts/`), optional `label` and `notes`, `status` (`want-to-read`, `reading`, `done`). Full schema in `skills/reads/SKILL.md`.

## Design

**Folder as Agent.** Agent = model + folder with enough context. Different folder, same model, different specialist. Each item's folder is self-contained agent context. See [The Folder Is the Agent](https://every.to/source-code/the-folder-is-the-agent) by Kieran Klaassen.

**Git as metadata.** No date fields, no timestamps in YAML. Git history is the timeline — commits record what happened and when.

**LLM-native matching.** No fuzzy-match algorithm. Skill reads data, LLM uses judgment to match references to items. Ambiguity → ask, not heuristics.

**Two interaction modes.** Every feature works remotely (skill + GitHub API) and locally (`cd` + CLAUDE.md auto-load). Both paths read and write same files.

## Folder as Agent

Each item gets a folder in `texts/`:

```
texts/ddia/
  CLAUDE.md           # agent identity — auto-loads on cd
  conversations.md    # accumulated discussion themes
  content.md          # reading material (saved by skill or added manually)
```

**Via skill:** `/reads let's discuss DDIA` loads folder context remotely, resumes conversation. After discussion, skill updates `conversations.md` and refreshes `CLAUDE.md`.

**Via folder:** `cd texts/ddia` in Claude Code — `CLAUDE.md` auto-loads. No skill needed.

Both paths converge on same files.

## How It Works

Skill uses GitHub REST Contents API for all reads/writes — no local clone needed. Each operation:

1. GET `reading.yaml` → decode base64 → parse YAML → save SHA
2. Modify in memory
3. PUT with modified content + SHA
4. Minimal commit message (e.g., `add DDIA`, `finished DDIA`)
5. Create/update item folder as needed

## License

MIT
