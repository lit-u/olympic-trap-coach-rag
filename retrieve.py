#!/usr/bin/env python3
"""Offline Olympic Trap RAG v0.2 retrieval: BM25 + curated ontology/links.

Uses only Python standard library. This is NOT an LLM, embedding model, or
automatic cause detector. No session data is transmitted.
Usage: python retrieve.py --query "Kaip atgauti korpuso ritma?" --top 6
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
DOCUMENT = ROOT / "RAG.md"
INDEX = ROOT / "knowledge_index.json"
HEADING = re.compile(r"^### \[(K-\d{3}|C-\d{2})\]\s*(.*)$")
T_ROW = re.compile(r"^\| `(T-\d{2})` \|")
STOP = {"ar", "ir", "kad", "tai", "mano", "jau", "kaip", "kodel", "is",
        "bei", "ten", "nuo", "the", "and", "for", "with", "have", "what"}
ROUTES = (
    (r"pagav|pagaun|catch|atpazin", ("K-101", "K-104", "T-02")),
    (r"korpus|liemen|pres|rank|posuk|turn|torso|inerc", ("K-104", "K-307", "T-01")),
    (r"ritm|automat|pakart|streak|serij", ("K-110", "C-03", "T-03")),
    (r"akis|akiu|zvilg|d[eė]mes|poils|pavarg|focus", ("K-109", "K-112", "T-07")),
    (r"pav[eė]lav|velai|vytis|staig|brak|stabd", ("K-103", "C-06", "K-303")),
    (r"pirm|antr|first|second|fire2", ("K-308", "C-10", "T-05")),
    (r"h1|h2|h3|master|pro|funny|fan", ("K-207", "C-02", "T-04")),
    (r"look|perziur|l[eė]kim|krypt|trajektor", ("K-107", "K-111", "T-06")),
    (r"greit|kampin|imu|gyro|speed", ("K-303", "C-06", "K-105")),
    (r"nepataik|miss|hit|pataik", ("C-04", "C-03", "K-207")),
    (r"kvep|puls|sird|breath|rifle", ("C-12",)),
    (r"json|export|tga|duomen|stat", ("K-305", "C-01")),
)


def normalize(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def words(s: str) -> list[str]:
    return [v for v in re.split(r"[^a-z0-9]+", normalize(s))
            if (len(v) >= 3 or (len(v) == 2 and v[1].isdigit()))
            and v not in STOP]


def load_chunks(path: Path = DOCUMENT) -> list[dict]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    chunks: list[dict] = []
    for i, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            id_, title = match.groups()
        elif line.startswith("## 0.") and "[K-000]" in line:
            id_, title = "K-000", "Trenerio filosofija ir vientisa judesio sistema"
        else:
            t = T_ROW.match(line)
            if t:
                cells = [v.strip() for v in line.strip("|").split("|")]
                if len(cells) >= 4:
                    chunks.append({"id": t.group(1), "title": cells[1],
                                   "text": " | ".join(cells[1:4]),
                                   "keywords": "training practice pratimas"})
            continue
        end = i + 1
        while end < len(lines) and not lines[end].startswith(("## ", "### ")):
            end += 1
        body = "\n".join(lines[i + 1:end]).strip()
        keys = re.search(r"\*\*Raktai:\*\*\s*(.+)", body)
        chunks.append({"id": id_, "title": title, "text": body,
                       "keywords": keys.group(1) if keys else ""})
    if len(chunks) != 52 or len({c["id"] for c in chunks}) != 52:
        raise ValueError(f"Expected 52 distinct RAG IDs, got {len(chunks)}")
    return chunks


def load_index(path: Path = INDEX) -> dict:
    index = json.loads(path.read_text(encoding="utf-8"))
    if index.get("schema") != "trap-gyro-knowledge-index":
        raise ValueError("Unrecognized ontology schema")
    ids = [item["id"] for item in index["items"]]
    if len(ids) != 52 or len(set(ids)) != 52:
        raise ValueError("Ontology must contain 52 distinct items")
    valid = set(ids)
    for edge in index["edges"]:
        if edge["from"] not in valid:
            raise ValueError(f"Orphan graph edge: {edge}")
        if edge["relation"] != "SUPPORTED_BY" and edge["to"] not in valid:
            raise ValueError(f"Orphan graph edge: {edge}")
    return index


def retrieve(query: str, top: int = 6) -> list[dict]:
    if not 4 <= top <= 8:
        raise ValueError("--top must be 4..8")
    chunks = load_chunks()
    index = load_index()
    corpus = {c["id"]: c for c in chunks}
    metadata = {i["id"]: i for i in index["items"]}
    if set(corpus) != set(metadata):
        raise ValueError("Knowledge index and RAG.md IDs differ")

    qwords = set(words(query))
    normalized = normalize(query)
    # BM25 on the small, local corpus. Extra weights improve short titles and
    # multilingual keywords without pretending to be semantic embeddings.
    docs = {c["id"]: words((c["title"] + " ") * 3 +
                           (c["keywords"] + " ") * 2 + c["text"]) for c in chunks}
    lengths = {k: len(v) for k, v in docs.items()}
    avg_len = sum(lengths.values()) / len(lengths)
    dfs = Counter(term for doc in docs.values() for term in set(doc))
    scores = {}
    for id_, terms in docs.items():
        tf = Counter(terms)
        score = 0.0
        for term in qwords:
            if not tf[term]:
                continue
            idf = math.log(1 + (len(docs) - dfs[term] + 0.5) / (dfs[term] + 0.5))
            score += idf * tf[term] * 2.2 / (
                tf[term] + 1.2 * (0.25 + 0.75 * lengths[id_] / avg_len))
        scores[id_] = score

    chosen: list[str] = []
    for required in ("K-000", "C-01"):
        if required in corpus:
            chosen.append(required)
    route_hits: list[str] = []
    for pattern, ids in ROUTES:
        if re.search(pattern, normalized):
            route_hits.extend(id_ for id_ in ids if id_ in corpus)
    # Apply route hints as ranking boosts, not permanent unbreakable slots.
    for id_ in route_hits:
        scores[id_] += 5.0
    linked = set(route_hits)
    for edge in index["edges"]:
        if edge["relation"] not in ("TESTED_WITH", "INTERPRETED_BY", "MEASURED_BY", "LIMITED_BY"):
            continue
        if edge["from"] in linked and edge["to"] in corpus:
            scores[edge["to"]] += 0.8
    for id_ in sorted(scores, key=lambda k: (-scores[k], k)):
        if len(chosen) >= top:
            break
        if id_ not in chosen:
            chosen.append(id_)
    return [{**corpus[id_], "classification": metadata[id_]} for id_ in chosen]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable excerpts with classification")
    args = parser.parse_args()
    matches = retrieve(args.query, args.top)
    if args.json:
        print(json.dumps({"source": DOCUMENT.name, "index": INDEX.name,
                          "query": args.query, "chunks": matches},
                         ensure_ascii=False, indent=2))
    else:
        for item in matches:
            print(f"\n[{item['id']}] {item['title']}\n{item['text']}\n")


if __name__ == "__main__":
    main()
