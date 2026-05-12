#!/usr/bin/env python3
"""Compile per-item meta.yaml + reading.yaml status into Schema.org JSON-LD.

Reads:
  reading.yaml          (root)              — list of items with status
  texts/<slug>/meta.yaml                    — per-item facts

Writes:
  texts/<slug>/meta.json                    — Schema.org JSON-LD snapshot

Run from repo root with no args. Idempotent. Safe to commit results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write("Need PyYAML. pip install pyyaml\n")
    sys.exit(1)


SCHEMA_TYPE = {
    "book": "Book",
    "article": "Article",
    "paper": "ScholarlyArticle",
    "post": "BlogPosting",
}

ACTION_STATUS = {
    "want-to-read": "PotentialActionStatus",
    "reading": "ActiveActionStatus",
    "done": "CompletedActionStatus",
}

CORE_FIELDS = {
    "title", "type", "url", "author", "publisher", "published",
    "isbn", "doi", "rating", "tags", "extra",
}


def author_node(author: Any) -> Any:
    if author is None:
        return None
    if isinstance(author, list):
        return [author_node(a) for a in author if a]
    return {"@type": "Person", "name": str(author)}


def build_jsonld(meta: dict, status: str | None) -> dict:
    schema_type = SCHEMA_TYPE.get(meta.get("type", "").lower(), "CreativeWork")
    doc: dict = {
        "@context": "https://schema.org",
        "@type": schema_type,
    }

    if title := meta.get("title"):
        doc["name"] = str(title)
    if url := meta.get("url"):
        doc["url"] = str(url)
    if a := author_node(meta.get("author")):
        doc["author"] = a
    if pub := meta.get("publisher"):
        doc["publisher"] = {"@type": "Organization", "name": str(pub)}
    if pd := meta.get("published"):
        doc["datePublished"] = str(pd)
    if isbn := meta.get("isbn"):
        doc["isbn"] = str(isbn)
    if doi := meta.get("doi"):
        doc["identifier"] = {
            "@type": "PropertyValue",
            "propertyID": "doi",
            "value": str(doi),
        }
    if (rating := meta.get("rating")) is not None:
        doc["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "bestRating": 5,
            "worstRating": 1,
            "ratingCount": 1,
        }
    if tags := meta.get("tags"):
        if isinstance(tags, list):
            doc["keywords"] = ", ".join(str(t) for t in tags)
        else:
            doc["keywords"] = str(tags)

    # Extra map → additionalProperty
    extra = meta.get("extra") or {}
    extras = []
    if isinstance(extra, dict):
        for k, v in extra.items():
            extras.append({
                "@type": "PropertyValue",
                "name": str(k),
                "value": v if isinstance(v, (str, int, float, bool)) else json.dumps(v),
            })
    # Anything else outside CORE_FIELDS, but not at top of meta — skip silently
    if extras:
        doc["additionalProperty"] = extras

    # ReadAction reflects current status
    if status:
        action_status = ACTION_STATUS.get(status, "PotentialActionStatus")
        doc["potentialAction"] = {
            "@type": "ReadAction",
            "actionStatus": action_status,
        }

    return doc


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    reading_yaml = root / "reading.yaml"
    reading = load_yaml(reading_yaml) or {}
    items = reading.get("items") or []

    # Map item path -> status for quick lookup
    status_by_path: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        status = item.get("status") or "want-to-read"
        if path:
            status_by_path[path] = status

    written = 0
    skipped_no_meta = 0
    for path, status in status_by_path.items():
        item_dir = root / path
        meta_path = item_dir / "meta.yaml"
        if not meta_path.exists():
            skipped_no_meta += 1
            continue
        meta = load_yaml(meta_path) or {}
        if not isinstance(meta, dict):
            sys.stderr.write(f"warn: {meta_path} is not a mapping; skipping\n")
            continue
        doc = build_jsonld(meta, status)
        out_path = item_dir / "meta.json"
        out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
        print(f"wrote {out_path.relative_to(root)}")

    print(f"\ncompiled {written} item(s); {skipped_no_meta} without meta.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
