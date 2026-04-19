---
title: "feat: Add save intent to reads skill"
type: feat
status: active
date: 2026-04-19
---

# feat: Add save intent to reads skill

## Overview

Add **Save** intent to reads skill. Fetches text-based web content from item URL, converts to markdown, commits as `content.md` in item's `texts/{label}/` folder. Closes gap between content.md being referenced in docs and nothing creating it.

## Problem Frame

Folder-agent model references `content.md` as reading material for discussions. Nothing in skill creates it — users must manually fetch, convert, commit. For text-based web media (articles, blog posts, essays, guides), skill can do this — already has URL + GitHub API write path.

## Requirements Trace

- R1. New "save" intent fetches URL content → writes `content.md` to item folder
- R2. Works for text-based web media (articles, essays, blog posts, papers, guides)
- R3. Handles gracefully: no URL on item, content already exists, non-text/inaccessible content
- R4. Save always explicit — never auto-triggered by add
- R5. Folder template + README document `content.md` as skill-created file
- R6. Commit message follows minimal convention: `save {label or url}`

## Scope Boundaries

- Text-based web content only. Books, videos, podcasts, PDFs out of scope
- No readability/extraction heuristics — LLM fetches page, uses judgment to extract article body → markdown
- No local-mode implementation — skill operates via GitHub API only (matches existing pattern)
- No auto-save on add (user decision)

## Context & Research

### Relevant Code and Patterns

- `skills/reads/SKILL.md` — all intents follow same structure: intent table entry → matching → read/write cycle via `gh api`
- `skills/reads/references/folder-agent-template.md` — folder structure, CLAUDE.md template, conversations.md format, naming rules
- `README.md` — already mentions `content.md` in folder structure
- Write operations: GET for sha → modify in memory → PUT with base64 + sha
- Commit convention: `{verb} {label or url}` — add, started, finished, note, init, discuss, context

### Content Conversion Approach

Skill runs inside Claude Code → `WebFetch` available. LLM can:
1. Fetch URL via WebFetch
2. Extract article body (skip nav, ads, sidebars, footers)
3. Convert to clean markdown (headings, paragraphs, lists, links, emphasis)
4. Preserve author attribution + publication date if visible
5. Add source URL header

Consistent with "LLM-native" philosophy — no external toolchain (pandoc, readability-cli), model uses judgment on raw HTML.

## Key Technical Decisions

- **New intent in SKILL.md, not separate skill**: Same matching, API, folder patterns. Separate skill = duplicate plumbing.
- **LLM-native conversion over toolchain**: Dependency-free. Model already processing page — extract + format simultaneously. Trade-off: may struggle with JS-heavy pages. Acceptable limitation.
- **Source header in content.md**: Every saved file starts with `Source: {url}` + `Saved: {date}`. Provenance always clear.
- **Overwrite requires confirmation**: content.md exists → ask before replacing. No silent overwrites.

## Open Questions

### Resolved During Planning

- **New intent or separate skill?** New intent — same patterns, same API, same matching.
- **Auto-save on add?** No — explicit only.
- **Fetching tool?** WebFetch — available in Claude Code, no deps.

### Deferred to Implementation

- **WebFetch paywall handling?** Runtime-dependent. Attempt fetch, report clearly if inaccessible/empty.
- **Max content length for GitHub API PUT?** ~100MB limit. Articles won't hit it. Real risk = LLM context window during conversion. Accept truncation for very long content.

## Implementation Units

- [ ] **Unit 1: Add Save intent to SKILL.md**

  **Goal:** Add Save to intent classification, matching, execution sections.

  **Requirements:** R1, R2, R3, R4, R6

  **Dependencies:** None

  **Files:**
  - Modify: `skills/reads/SKILL.md`

  **Approach:**
  - Add `Save` row to Intent Classification table. Triggers: "save compound engineering", "capture this article", "archive DDIA"
  - Add Save to Executing Operations under Write Operations
  - Save flow:
    1. Match item in reading.yaml
    2. Verify item has `url` — if not, tell user save requires URL
    3. Check if `texts/{folder}/content.md` exists (GET) — if so, ask update or skip
    4. Fetch URL via WebFetch
    5. Extract article body → markdown
    6. Prepend source header: `Source: {url}` + `Saved: {date}`
    7. PUT `content.md` via GitHub API
    8. Commit: `save {label or url}`
  - Error guidance: non-text content → tell user save is for text; fetch failure → surface error, suggest checking URL
  - Add `save {label or url}` to commit message list

  **Patterns to follow:**
  - Existing Write Operations flow (read → modify → write → handle response)
  - Intent table format
  - Error handling (409, 422, 5xx)

  **Test scenarios:**
  - Happy path: save item with URL → content.md created with source header + markdown body
  - Edge case: item has no URL → reports save requires URL
  - Edge case: content.md exists → asks update or skip
  - Error path: URL inaccessible/non-HTML → reports couldn't fetch
  - Error path: URL points to video/podcast → suggests save for text content

  **Verification:**
  - Save in intent table with triggers
  - Save operation documented with full cycle
  - Commit convention includes `save`

- [ ] **Unit 2: Document content.md in folder-agent template**

  **Goal:** Update template reference — content.md is skill-created, not just user-managed.

  **Requirements:** R5

  **Dependencies:** Unit 1

  **Files:**
  - Modify: `skills/reads/references/folder-agent-template.md`

  **Approach:**
  - Add content.md to folder structure docs alongside CLAUDE.md + conversations.md
  - Document format: source header (`Source:`, `Saved:`) + markdown article body
  - Note: created by Save intent, also manually addable/editable
  - During Discuss, model references content.md when present

  **Patterns to follow:**
  - Existing CLAUDE.md + conversations.md documentation style

  **Test expectation:** none — documentation only

  **Verification:**
  - Template describes content.md format + creation path
  - Folder structure example includes content.md

- [ ] **Unit 3: Update README**

  **Goal:** Document save command, update content.md description.

  **Requirements:** R5

  **Dependencies:** Unit 1

  **Files:**
  - Modify: `README.md`

  **Approach:**
  - Add save example to Usage: `/reads save compound engineering`
  - Update folder structure — content.md "saved by skill or added manually"

  **Patterns to follow:**
  - Existing usage examples

  **Test expectation:** none — documentation only

  **Verification:**
  - Save in usage examples
  - content.md description updated

- [ ] **Unit 4: Update Discuss to leverage content.md**

  **Goal:** Discuss loads content.md when present — grounded material for conversations.

  **Requirements:** R1 (indirect — save useful when discuss references content)

  **Dependencies:** Unit 1

  **Files:**
  - Modify: `skills/reads/SKILL.md`

  **Approach:**
  - Discuss step 2: add content.md to fetch list alongside CLAUDE.md + conversations.md
  - content.md exists → include as reading material context
  - Missing → skip silently (same 404 pattern as conversations.md in Search)

  **Patterns to follow:**
  - Search 404 handling on conversations.md

  **Test scenarios:**
  - Happy path: discuss with content.md → content loaded as context
  - Edge case: discuss without content.md → proceeds normally

  **Verification:**
  - Discuss fetches content.md
  - Missing content.md handled silently

## System-Wide Impact

- **Interaction graph:** Save creates content.md → Discuss reads it. Pure file create/read.
- **Error propagation:** WebFetch failure local to save. No cascade.
- **State lifecycle risks:** Overwrite without confirmation → lost manual edits. Mitigated by ask-before-replace.
- **API surface parity:** Local mode (`cd` into folder) reads content.md if present. No changes needed.
- **Unchanged invariants:** reading.yaml schema unchanged. Existing intents unchanged. Folder creation on add unchanged — content.md NOT created on add.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| WebFetch unavailable in some environments | Document as requirement; skill already depends on `gh` |
| Paywall → login page saved | LLM detects, reports "content behind paywall" |
| Very long articles | GitHub API ~100MB limit fine. LLM context = real limit. Accept truncation |
| JS-rendered pages → empty HTML | Report clearly; suggest different URL or manual content.md |

## Sources & References

- Skill: `skills/reads/SKILL.md`
- Template: `skills/reads/references/folder-agent-template.md`
- README: `README.md`
