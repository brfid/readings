# Folder-Agent Template

When the skill creates a folder for a reading item, generate these files.

## CLAUDE.md

```markdown
# {label or url}

Status: {status}
{url_line}
{path_line}

## Reading Context

{Initial context — empty on first create, updated by skill after interactions.}

## Key Themes

{Accumulated themes from conversations. Bullet list.}

## Open Questions

{Questions surfaced during reading/discussion. Bullet list.}

## Connections

{Links to other items in the reading list. Format: `texts/{other-item}/`}
```

### Generation rules

- `{label or url}`: use label as heading if available, otherwise URL
- `{url_line}`: `URL: {url}` — omit line entirely if no url
- `{path_line}`: `Path: texts/{folder-name}/content.md` — always present
- Status: copy from reading.yaml item
- Reading Context: "No context yet." on first create
- Key Themes, Open Questions, Connections: empty on first create, just the heading

## conversations.md

Start empty. Each entry appended by the skill uses this format:

```markdown
## {YYYY-MM-DD}

{2-4 sentence summary: what was discussed, decisions made, questions raised, connections noticed.}
```

### Append rules

- One entry per substantive interaction (not per status change or trivial update)
- Capture: topics discussed, insights, decisions, open questions, connections to other items
- Do not include the full conversation — themes and decisions only
- Date is the current date, not a timestamp

## Folder naming

Derive folder name from label or URL:
- Lowercase, hyphens for spaces
- Strip articles (a/an/the) from start
- Max 40 characters
- Examples: `ddia`, `raft-paper`, `building-microservices`, `some-interesting-article`
