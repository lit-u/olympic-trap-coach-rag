#!/usr/bin/env python3
"""Retrieve relevant Olympic Trap coaching excerpts from local RAG.md.

Offline, deterministic, standard-library only. Retrieval is NOT an LLM.
Usage: python retrieve.py --query "Ar per velai pajudejau?" --top 6
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unicodedata

DOCUMENT = Path(__file__).with_name("RAG.md")
HEADING = re.compile(r"^### \[(K-\d{3}|C-\d{2})\]\s*(.*)$")
T_ROW = re.compile(r"^\| \`(T-\d{2})\` \|")
STOP = {"ar", "ir", "kad", "tai", "mano", "jau", "kaip", "kodel", "is", "bei",
        "ten", "nuo", "the", "and", "for", "with", "have", "what"}


def words(s: str) -> set[str]:
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower())
                if unicodedata.category(c) != "Mn")
    return {v for v in re.split(r"[^a-z0-9]+", s) if len(v) >= 3 and v not in STOP}


def load_chunks(path: Path = DOCUMENT) -> list[dict]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    chunks = []
    for i, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            id_, title = match.groups()
        elif line.startswith("## 0.") and "[K-000]" in line:
            id_, title = "K-000", "Vienintelė trenerio filosofija"
        else:
            t = T_ROW.match(line)
            if not t:
                continue
            cells = [v.strip() for v in line.strip("|").split("|")]
            if len(cells) >= 4:
                chunks.append({"id": t.group(1), "title": cells[1],
                               "text": " | ".join(cells[1:4]), "keywords": "practice training pratimas"})
            continue
        end = i + 1
        while end < len(lines) and not lines[end].startswith(("## ", "### ")):
            end += 1
        body = "\n".join(lines[i + 1:end]).strip()
        keys = re.search(r"\*\*Raktai:\*\*\s*(.+)", body)
        chunks.append({"id": id_, "title": title, "text": body,
                       "keywords": keys.group(1) if keys else ""})
    if len({c["id"] for c in chunks}) != len(chunks):
        raise ValueError("Duplicate RAG IDs")
    return chunks


def retrieve(query: str, top: int = 6) -> list[dict]:
    if not 4 <= top <= 8:
        raise ValueError("--top must be 4..8")
    corpus = {c["id"]: c for c in load_chunks()}
    tokens = words(query)
    picked = []
    for required in ("K-000", "C-01", "K-305"):
        if required in corpus:
            picked.append(required)
    normalized = " ".join(words(query))
    routes = [
        (r"reak|pajud|move|visible|velai", ["K-301", "K-302", "C-05"]),
        (r"greit|stabd|speed|imu|gyro", ["K-303", "C-06"]),
        (r"nepataik|miss|hit|25", ["K-207", "C-04"]),
        (r"pirm|antr|first|second", ["K-308", "C-10"]),
        (r"stot|issf|trajektor", ["K-107", "C-02"]),
        (r"puls|kvep|sird|breath", ["K-112", "C-12"]),
    ]
    for expr, ids in routes:
        if re.search(expr, normalized):
            for id_ in ids:
                if id_ in corpus and id_ not in picked and len(picked) < top:
                    picked.append(id_)
    ranked = []
    for c in corpus.values():
        if c["id"] in picked:
            continue
        title, keys, text = words(c["title"]), words(c["keywords"]), words(c["text"])
        score = sum(6 * (t in title) + 4 * (t in keys) + (t in text) for t in tokens)
        ranked.append((score, c["id"]))
    for score, id_ in sorted(ranked, key=lambda x: (-x[0], x[1])):
        if len(picked) >= top:
            break
        if score or len(picked) < 4:
            picked.append(id_)
    return [corpus[id_] for id_ in picked]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--json", action="store_true", help="Machine-readable excerpts")
    args = parser.parse_args()
    matches = retrieve(args.query, args.top)
    if args.json:
        print(json.dumps({"source": str(DOCUMENT.name), "query": args.query,
                          "chunks": matches}, ensure_ascii=False, indent=2))
    else:
        for item in matches:
            print(f"\n[{item['id']}] {item['title']}\n{item['text']}\n")


if __name__ == "__main__":
    main()
