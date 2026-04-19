# Folder-Agent Template

When the skill creates a folder for a reading item, generate these files.

## CLAUDE.md

On create, CLAUDE.md is identity only — no empty sections:

```markdown
# {label or url}

Status: {status}
{url_line}
```

### Generation rules

- `{label or url}`: use label as heading if available, otherwise URL
- `{url_line}`: `URL: {url}` — omit line entirely if no url
- Status: copy from reading.yaml item
- No other sections on create. Sections are added when there is content for them.

### Available sections

Add these to CLAUDE.md only when substantive content exists for them. Never add an empty section.

| Section | When to add | Content |
|---------|-------------|---------|
| `## Reading Context` | After first substantive discussion | Where the reader is, what they're focused on, what they plan to read next |
| `## Key Themes` | When themes emerge from discussion | Bullet list of recurring or significant themes |
| `## Open Questions` | When questions are raised | Bullet list of unresolved questions the reader wants to return to |
| `## Connections` | When links to other items surface | References to other items: `texts/{other-item}/` |
| `## Key Takeaways` | When the reader identifies conclusions or insights | Bullet list of durable insights worth remembering |
| `## Disagreements` | When the reader pushes back on the material | Points where the reader disagrees or is skeptical |

### Update rules

When updating CLAUDE.md after a conversation:
- Add new sections with content as they become relevant
- Update existing sections — replace stale content, append new bullets
- Keep sections concise. Each section should be scannable, not exhaustive
- Remove a section if its content is no longer relevant (rare)
- Always update `Status:` if it changed

## conversations.md

Start empty. This is the primary conversation continuity mechanism — it must capture enough context that a new session can resume meaningfully.

Each entry appended by the skill uses this format:

```markdown
## {YYYY-MM-DD}

**What we discussed:** {1-2 sentences on the topic and scope of the conversation.}

**Key points:** {Bullet list of specific claims, arguments, insights, or decisions. Include enough detail that someone reading this entry alone could follow the reasoning.}

**Where we left off:** {What was the last topic? What was about to be explored next? Any unresolved thread?}

**Open threads:** {Optional. Questions raised but not answered, tensions identified but not resolved, tangents worth returning to.}
```

### Append rules

- One entry per substantive interaction (not per status change or trivial update)
- Prioritize resumability: a new session reading this entry should know what to pick up and where
- Include specific details — names, chapter numbers, argument summaries, not just "discussed themes"
- When a conversation resolves a previously open thread, note that explicitly
- Date is the current date, not a timestamp

### Growth management

When conversations.md exceeds ~50 entries or becomes unwieldy:
- Summarize older entries (keeping the 10 most recent intact) into a `## Summary (before {date})` section at the top
- Preserve all open threads from summarized entries
- The goal is to keep the file useful for cold-start resumption without unbounded growth

## Folder naming

Derive folder name from the label if provided, otherwise from the URL.

**From label:**
- Lowercase, hyphens for spaces
- Strip leading articles (a/an/the)
- Max 40 characters, truncate at word boundary
- Examples: `ddia`, `raft-paper`, `building-microservices`

**From URL (when no label):**
- Use the last meaningful path segment, stripping file extensions
- Drop query strings, fragments, and common prefixes like `www.`
- If path is empty or just `/`, use the domain minus TLD
- Lowercase, hyphens for separators
- Max 40 characters, truncate at word boundary
- Examples:
  - `https://example.com/blog/raft-explained` → `raft-explained`
  - `https://arxiv.org/abs/2103.04992` → `2103-04992`
  - `https://every.to/guides/compound-engineering` → `compound-engineering`
  - `https://example.com/` → `example`
