#!/usr/bin/env python3
"""Compile reading.yaml items into per-item Schema.org JSON-LD (meta.json).

Reads the single reading.yaml (v2 — all metadata in one file).
Writes texts/<slug>/meta.json per item.

Run from repo root with no args. Idempotent. Safe to commit results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

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
    "abandoned": "FailedActionStatus",
}


def author_node(author: Any) -> Any:
    if author is None:
        return None
    if isinstance(author, list):
        return [author_node(a) for a in author if a]
    return {"@type": "Person", "name": str(author)}


def build_jsonld(item: dict) -> dict:
    schema_type = SCHEMA_TYPE.get(
        (item.get("type") or "").lower(), "CreativeWork"
    )
    doc: dict = {"@context": "https://schema.org", "@type": schema_type}

    if title := item.get("title"):
        doc["name"] = str(title)
    if location := item.get("location"):
        if str(location).startswith("http"):
            doc["url"] = str(location)
    if a := author_node(item.get("authors")):
        doc["author"] = a
    if pub := item.get("publisher"):
        doc["publisher"] = {"@type": "Organization", "name": str(pub)}
    if pd := item.get("published"):
        doc["datePublished"] = str(pd)
    if isbn := item.get("isbn"):
        doc["isbn"] = str(isbn)
    if doi := item.get("doi"):
        doc["identifier"] = {
            "@type": "PropertyValue",
            "propertyID": "doi",
            "value": str(doi),
        }
    if (rating := item.get("rating")) is not None:
        doc["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "bestRating": 5,
            "worstRating": 1,
            "ratingCount": 1,
        }

    # Extra map → additionalProperty
    extra = item.get("extra") or {}
    extras = []
    if isinstance(extra, dict):
        for k, v in extra.items():
            extras.append(
                {
                    "@type": "PropertyValue",
                    "name": str(k),
                    "value": v
                    if isinstance(v, (str, int, float, bool))
                    else json.dumps(v),
                }
            )
    if extras:
        doc["additionalProperty"] = extras

    # ReadAction reflects current status
    if status := item.get("status"):
        action_status = ACTION_STATUS.get(status, "PotentialActionStatus")
        doc["potentialAction"] = {
            "@type": "ReadAction",
            "actionStatus": action_status,
        }

    return doc


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    reading_path = root / "reading.yaml"
    with reading_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    items = data.get("items") or []
    written = 0
    skipped = 0

    for item in items:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if not path:
            skipped += 1
            continue
        item_dir = root / path
        item_dir.mkdir(parents=True, exist_ok=True)
        doc = build_jsonld(item)
        out_path = item_dir / "meta.json"
        out_path.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written += 1
        print(f"wrote {out_path.relative_to(root)}")

    print(f"\ncompiled {written} item(s); {skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())