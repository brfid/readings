#!/usr/bin/env python3
"""reads.py — single-file CLI for the brfid/reads reading tracker.

All commands funnel through load() → mutate → save().  save() calls
validate() before writing, then git-adds/commits/pushes.  No shell=True,
no string interpolation into Python source — all values arrive as argv.

Stdlib only (json, re, sys, os, argparse, subprocess, pathlib, urllib).
PyYAML is the sole third-party dep — installed system-wide on this Pi.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from datetime import date
from typing import Any

import yaml

# ── paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
READING_YAML = ROOT / "reading.yaml"
QUEUE_YAML = ROOT / "queue.yaml"
README_MD = ROOT / "README.md"
TEXTS_DIR = ROOT / "texts"
TEXTS_README = TEXTS_DIR / "README.md"

# ── schema ─────────────────────────────────────────────────────────────────
VERSION = 2
VALID_STATUS = {"want-to-read", "reading", "done", "abandoned"}
VALID_TYPE = {"book", "article", "paper", "post", None}
# Fields that live in reading.yaml (the single source of truth)
KNOWN_FIELDS = {
    "title", "authors", "type", "location", "path", "status",
    "publisher", "published", "isbn", "doi", "rating", "notes",
    "extra",
}
REQUIRED_FIELDS = {"title", "path", "status"}

# ── DRY core ───────────────────────────────────────────────────────────────

def load() -> dict:
    """Load reading.yaml, return the data dict."""
    with READING_YAML.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"version": VERSION, "items": []}


def validate(data: dict) -> list[str]:
    """Return a list of error messages (empty list = valid)."""
    errors = []
    if not isinstance(data, dict):
        return ["root is not a mapping"]
    if data.get("version") != VERSION:
        errors.append(f"version must be {VERSION}, got {data.get('version')!r}")
    items = data.get("items", [])
    if not isinstance(items, list):
        return ["items is not a list"]
    paths_seen = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{i}] is not a mapping")
            continue
        for field in REQUIRED_FIELDS:
            if field not in item or item[field] is None:
                errors.append(f"items[{i}] missing required field '{field}'")
        if "status" in item and item["status"] not in VALID_STATUS:
            errors.append(f"items[{i}] bad status {item['status']!r} (must be {VALID_STATUS})")
        if "type" in item and item["type"] not in VALID_TYPE:
            errors.append(f"items[{i}] bad type {item['type']!r}")
        if "rating" in item and item["rating"] is not None:
            try:
                r = int(item["rating"])
                if not 1 <= r <= 5:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append(f"items[{i}] bad rating {item['rating']!r} (must be 1-5)")
        # path uniqueness
        p = item.get("path")
        if p:
            if p in paths_seen:
                errors.append(f"items[{i}] duplicate path {p!r}")
            paths_seen.add(p)
            # path must start with texts/
            if not str(p).startswith("texts/"):
                errors.append(f"items[{i}] path {p!r} must start with 'texts/'")
        # unknown fields
        for key in item:
            if key not in KNOWN_FIELDS:
                errors.append(f"items[{i}] unknown field {key!r}")
    return errors


def save(data: dict, msg: str, push: bool = True) -> None:
    """Validate, write reading.yaml, git add + commit + push."""
    errors = validate(data)
    if errors:
        for e in errors:
            sys.stderr.write(f"  ✗ {e}\n")
        sys.error("Refusing to write invalid data.") if hasattr(sys, 'error') else None
        sys.exit(1)
    yaml_text = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    READING_YAML.write_text(yaml_text, encoding="utf-8")
    _git_commit(["reading.yaml"], msg, push)


def _git_commit(paths: list[str], msg: str, push: bool = True) -> None:
    """git add <paths> → commit → (optional) pull --rebase + push."""
    for p in paths:
        subprocess.run(["git", "add", p], cwd=ROOT, check=True)
    r = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0 and "nothing to commit" not in r.stdout:
        sys.stderr.write(r.stdout + r.stderr)
        sys.exit(1)
    if push:
        # pull --rebase, then push — retry once on conflict
        for attempt in range(2):
            r = subprocess.run(["git", "pull", "--rebase"], cwd=ROOT,
                               capture_output=True, text=True)
            if r.returncode == 0:
                break
            if attempt == 0:
                # abort rebase, try once more
                subprocess.run(["git", "rebase", "--abort"], cwd=ROOT,
                               capture_output=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)


def resolve(data: dict, ref: str) -> dict:
    """Resolve a user reference to a single item.  Error if ambiguous/not found."""
    items = data["items"]
    # 1. exact path match
    for item in items:
        if item.get("path") == ref or item.get("path", "").endswith("/" + ref):
            return item
    # 2. exact title match
    for item in items:
        if item.get("title", "").lower() == ref.lower():
            return item
    # 3. fuzzy substring
    matches = [i for i in items if ref.lower() in i.get("title", "").lower()]
    matches += [i for i in items if ref.lower() in i.get("path", "").lower()]
    # dedupe
    seen = set()
    unique = []
    for m in matches:
        if id(m) not in seen:
            seen.add(id(m))
            unique.append(m)
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        sys.stderr.write(f"Ambiguous reference {ref!r}. Candidates:\n")
        for m in unique:
            sys.stderr.write(f"  {m['path']}  —  {m.get('title', '?')}\n")
        sys.exit(1)
    sys.stderr.write(f"No match for {ref!r}\n")
    sys.exit(1)


def slugify(text: str) -> str:
    """Derive folder name from a title."""
    t = text.lower()
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'[\s_]+', '-', t)
    t = t.strip('-')
    # strip leading articles
    for art in ('a-', 'an-', 'the-'):
        if t.startswith(art):
            t = t[len(art):]
    # truncate at 40 chars, at word boundary
    if len(t) > 40:
        t = t[:40].rsplit('-', 1)[0]
    return t or "untitled"


def ensure_unique_path(data: dict, slug: str) -> str:
    """Ensure texts/<slug> doesn't exist; append -2, -3, etc."""
    existing = {i.get("path", "") for i in data["items"]}
    candidate = f"texts/{slug}"
    n = 2
    while candidate in existing or (ROOT / candidate).exists():
        candidate = f"texts/{slug}-{n}"
        n += 1
    return candidate


# ── commands ────────────────────────────────────────────────────────────────

def cmd_add(args):
    data = load()
    slug = slugify(args.title)
    path = ensure_unique_path(data, slug)
    item = {
        "title": args.title,
        "path": path,
        "status": args.status or "want-to-read",
    }
    if args.author:
        item["authors"] = list(args.author)
    if args.type:
        item["type"] = args.type
    if args.location:
        item["location"] = args.location
    # Create folder files first (orphan folder is harmless)
    item_dir = ROOT / path
    item_dir.mkdir(parents=True, exist_ok=True)
    # CLAUDE.md
    lines = [f"# {args.title}", "", f"**Status:** {item['status']}"]
    if args.location:
        lines.append(f"**Location:** {args.location}")
    if args.author:
        lines.append(f"**Author(s):** {', '.join(args.author)}")
    (item_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # conversations.md — empty
    (item_dir / "conversations.md").write_text("", encoding="utf-8")
    # Add to reading.yaml last
    data["items"].append(item)
    save(data, f"add {args.title}")
    print(f"Added: {path}")


def cmd_start(args):
    data = load()
    item = resolve(data, args.ref)
    old = item["status"]
    item["status"] = "reading"
    save(data, f"started {item['title']}")
    print(f"{item['title']}: {old} → reading")


def cmd_finish(args):
    data = load()
    item = resolve(data, args.ref)
    item["status"] = "done"
    if args.rating is not None:
        item["rating"] = args.rating
    save(data, f"finished {item['title']}")
    print(f"{item['title']}: → done")


def cmd_note(args):
    data = load()
    item = resolve(data, args.ref)
    notes = item.get("notes")
    if notes is None:
        item["notes"] = []
    if not isinstance(item["notes"], list):
        item["notes"] = [item["notes"]]  # migrate from old string format
    item["notes"].append(args.text)
    save(data, f"note {item['title']}")
    print(f"Noted on {item['title']}")


def cmd_fact(args):
    data = load()
    item = resolve(data, args.ref)
    field = args.field
    if field not in KNOWN_FIELDS:
        sys.stderr.write(f"Unknown field {field!r}. Known: {', '.join(sorted(KNOWN_FIELDS))}\n")
        sys.exit(1)
    value = args.value
    # Type coercion
    if field == "rating":
        try:
            value = int(value)
        except ValueError:
            sys.stderr.write("rating must be an integer 1-5\n")
            sys.exit(1)
    elif field == "authors":
        value = [a.strip() for a in value.split(",")]
    elif field in ("isbn", "published", "doi", "publisher", "location", "title", "type"):
        value = value  # keep as string
    item[field] = value
    save(data, f"fact {item['title']}: {field}")
    print(f"Set {field} = {value!r} on {item['title']}")


def cmd_discuss(args):
    data = load()
    item = resolve(data, args.ref)
    conv_path = ROOT / item["path"] / "conversations.md"
    existing = conv_path.read_text(encoding="utf-8") if conv_path.exists() else ""
    today = date.today().isoformat()
    slug = re.sub(r'[^\w-]', '', args.topic.lower().replace(" ", "-"))[:50]
    entry = f"\n## {today} · {slug}\n\n{args.text}\n"
    conv_path.write_text(existing + entry, encoding="utf-8")
    _git_commit([str(conv_path.relative_to(ROOT))], f"discuss {item['title']}")
    print(f"Discussion logged on {item['title']}")


def cmd_save(args):
    data = load()
    item = resolve(data, args.ref)
    location = item.get("location", "")
    if not location or not location.startswith("http"):
        sys.stderr.write(f"No URL location for {item['title']!r}\n")
        sys.exit(1)
    try:
        req = urllib.request.Request(location, headers={"User-Agent": "reads-tracker/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        sys.stderr.write(f"Fetch failed: {e}\n")
        sys.exit(1)
    content_path = ROOT / item["path"] / "content.md"
    header = f"Source: {location}\nSaved: {date.today().isoformat()}\n\n"
    content_path.write_text(header + raw, encoding="utf-8")
    _git_commit([str(content_path.relative_to(ROOT))], f"save {item['title']}")
    print(f"Saved content for {item['title']}")


def cmd_queue_add(args):
    with QUEUE_YAML.open("r", encoding="utf-8") as f:
        q = yaml.safe_load(f) or {"pending": []}
    entry = {"location": args.location, "from": args.from_ or "manual",
             "added": date.today().isoformat()}
    if args.title:
        entry["title"] = args.title
    if args.type:
        entry["type"] = args.type
    q.setdefault("pending", []).append(entry)
    yaml_text = yaml.dump(q, allow_unicode=True, default_flow_style=False, sort_keys=False)
    QUEUE_YAML.write_text(yaml_text, encoding="utf-8")
    _git_commit(["queue.yaml"], f"queue {args.title or args.location}")
    print(f"Queued: {args.title or args.location}")


def cmd_queue_drain(args):
    with QUEUE_YAML.open("r", encoding="utf-8") as f:
        q = yaml.safe_load(f) or {"pending": []}
    pending = q.get("pending", [])
    if not pending:
        print("Queue is empty.")
        return
    print(f"Processing {len(pending)} queued item(s)...")
    for entry in pending:
        # Add each as a new item
        data = load()
        title = entry.get("title") or entry.get("location", "untitled")
        slug = slugify(title)
        path = ensure_unique_path(data, slug)
        item = {"title": title, "path": path, "status": "want-to-read"}
        if entry.get("location"):
            item["location"] = entry["location"]
        if entry.get("type"):
            item["type"] = entry["type"]
        item_dir = ROOT / path
        item_dir.mkdir(parents=True, exist_ok=True)
        lines = [f"# {title}", "", f"**Status:** want-to-read"]
        if entry.get("location"):
            lines.append(f"**Location:** {entry['location']}")
        (item_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (item_dir / "conversations.md").write_text("", encoding="utf-8")
        data["items"].append(item)
        save(data, f"drain queue: {title}")
        print(f"  Added: {path}")
    # Clear queue
    q["pending"] = []
    yaml_text = yaml.dump(q, allow_unicode=True, default_flow_style=False, sort_keys=False)
    QUEUE_YAML.write_text(yaml_text, encoding="utf-8")
    _git_commit(["queue.yaml"], "drain queue — cleared")
    print("Queue drained.")


def cmd_query(args):
    data = load()
    items = data["items"]
    if args.status:
        items = [i for i in items if i.get("status") == args.status]
    if args.type:
        items = [i for i in items if i.get("type") == args.type]
    if args.author:
        items = [i for i in items
                 if any(args.author.lower() in str(a).lower()
                        for a in i.get("authors", []) if a)]
    if not items:
        print("No items match.")
        return
    for item in items:
        status_icon = {"reading": "📖", "done": "✓", "want-to-read": "▢",
                        "abandoned": "✗"}.get(item["status"], "?")
        authors = ", ".join(item.get("authors", [])) if item.get("authors") else ""
        line = f"{status_icon} {item['title']}"
        if authors:
            line += f" ({authors})"
        if item.get("location") and not item["location"] == "Books app":
            line += f"  {item['location']}"
        print(line)


def cmd_search(args):
    data = load()
    term = args.keyword.lower()
    matches = []
    for item in data["items"]:
        haystack = " ".join(str(v) for v in [
            item.get("title", ""), item.get("location", ""),
            item.get("notes", ""),
            " ".join(item.get("authors", []) if isinstance(item.get("authors"), list) else []),
        ]).lower()
        if term in haystack:
            matches.append(item)
    if not matches:
        print("No matches.")
        return
    for item in matches:
        print(f"  {item['path']}  —  {item['title']}  [{item['status']}]")


def cmd_history(args):
    data = load()
    if args.ref:
        item = resolve(data, args.ref)
        path = item["path"]
        cmd = ["git", "log", "--oneline", "--follow", "--", path]
        label = item["title"]
    else:
        cmd = ["git", "log", "--oneline", "--", "reading.yaml"]
        label = "all items"
    if args.since:
        cmd += [f"--since={args.since}"]
    print(f"History for {label}:")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout)


def cmd_readme(args):
    data = load()
    items = data["items"]
    reading = [i for i in items if i["status"] == "reading"]
    done = [i for i in items if i["status"] == "done"]
    want = [i for i in items if i["status"] == "want-to-read"]

    def fmt(item):
        title = item["title"]
        authors = ", ".join(item.get("authors", [])) if item.get("authors") else ""
        if authors:
            title += f" ({authors})"
        notes = item.get("notes")
        note_str = ""
        if isinstance(notes, list) and notes:
            note_str = f" — {notes[-1][:60]}"
        elif isinstance(notes, str) and notes:
            note_str = f" — {notes[:60]}"
        return f"- [{title}]({item['path']}/){note_str}"

    lines = ["# Reading Tracker", "",
             f"**Currently reading:** {len(reading)}",
             f"**Finished:** {len(done)}",
             f"**Backlog:** {len(want)}", ""]

    if reading:
        lines.append("## Currently Reading")
        lines += [fmt(i) for i in reading]
        lines.append("")
    if done:
        lines.append("## Recently Finished")
        lines += [fmt(i) for i in done]
        lines.append("")
    if want:
        lines.append(f"## Backlog ({len(want)})")
        lines += [f"- {i['title']}" for i in want]
        lines.append("")

    README_MD.write_text("\n".join(lines), encoding="utf-8")

    # texts/README.md
    texts_lines = ["# Texts Index", ""]
    for item in sorted(items, key=lambda i: i.get("title", "")):
        folder = item["path"].replace("texts/", "")
        texts_lines.append(f"- [{folder}]({folder}/) — {item['title']} [{item['status']}]")
    texts_lines.append("")
    TEXTS_README.write_text("\n".join(texts_lines), encoding="utf-8")

    _git_commit(["README.md", "texts/README.md"], "update README")
    print("README regenerated.")


def cmd_validate(args):
    data = load()
    errors = validate(data)
    if errors:
        for e in errors:
            sys.stderr.write(f"  ✗ {e}\n")
        print(f"INVALID: {len(errors)} error(s)")
        sys.exit(1)
    print(f"OK: {len(data.get('items', []))} item(s) valid")


# ── CLI ────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(prog="reads.py", description="Reading tracker CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # add
    sp = sub.add_parser("add", help="Add a new item")
    sp.add_argument("--title", required=True)
    sp.add_argument("--author", action="append", help="Author (repeatable)")
    sp.add_argument("--type", choices=["book", "article", "paper", "post"])
    sp.add_argument("--location", help="URL or 'Books app'")
    sp.add_argument("--status", default="want-to-read",
                    choices=sorted(VALID_STATUS - {"abandoned"}))
    sp.set_defaults(func=cmd_add)

    # start
    sp = sub.add_parser("start", help="Set status to reading")
    sp.add_argument("ref", help="Title, path, or search string")
    sp.set_defaults(func=cmd_start)

    # finish
    sp = sub.add_parser("finish", help="Set status to done")
    sp.add_argument("ref")
    sp.add_argument("--rating", type=int, choices=range(1, 6))
    sp.set_defaults(func=cmd_finish)

    # note
    sp = sub.add_parser("note", help="Append a note")
    sp.add_argument("ref")
    sp.add_argument("text", help="Note text")
    sp.set_defaults(func=cmd_note)

    # fact
    sp = sub.add_parser("fact", help="Set a metadata field")
    sp.add_argument("ref")
    sp.add_argument("field", help="Field name (title, authors, type, location, publisher, published, isbn, rating, doi)")
    sp.add_argument("value", help="Field value (comma-sep for authors)")
    sp.set_defaults(func=cmd_fact)

    # discuss
    sp = sub.add_parser("discuss", help="Append to conversations.md")
    sp.add_argument("ref")
    sp.add_argument("text", help="Discussion summary")
    sp.add_argument("--topic", required=True, help="Short topic slug")
    sp.set_defaults(func=cmd_discuss)

    # save
    sp = sub.add_parser("save", help="Fetch URL content → content.md")
    sp.add_argument("ref")
    sp.set_defaults(func=cmd_save)

    # queue-add
    sp = sub.add_parser("queue-add", help="Append to queue.yaml")
    sp.add_argument("--title")
    sp.add_argument("--location", required=True)
    sp.add_argument("--type", choices=["book", "article", "paper", "post"])
    sp.add_argument("--from", dest="from_", help="Source profile name")
    sp.set_defaults(func=cmd_queue_add)

    # queue-drain
    sp = sub.add_parser("queue-drain", help="Process pending queue items")
    sp.set_defaults(func=cmd_queue_drain)

    # query
    sp = sub.add_parser("query", help="Filter and display items")
    sp.add_argument("--status", choices=sorted(VALID_STATUS))
    sp.add_argument("--type", choices=["book", "article", "paper", "post"])
    sp.add_argument("--author")
    sp.set_defaults(func=cmd_query)

    # search
    sp = sub.add_parser("search", help="Search across items")
    sp.add_argument("keyword")
    sp.set_defaults(func=cmd_search)

    # history
    sp = sub.add_parser("history", help="Git log for an item or all")
    sp.add_argument("ref", nargs="?")
    sp.add_argument("--since", help="Date (e.g. 2025-01-01)")
    sp.set_defaults(func=cmd_history)

    # readme
    sp = sub.add_parser("readme", help="Regenerate README.md files")
    sp.set_defaults(func=cmd_readme)

    # validate
    sp = sub.add_parser("validate", help="Validate reading.yaml (CI check)")
    sp.set_defaults(func=cmd_validate)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()