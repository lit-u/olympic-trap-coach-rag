# Olympic Trap AI COACH RAG

Public knowledge base for the [TRAP COACH project](https://github.com/lit-u/olympic-trap-coach-rag/blob/main/RAG.md).

## What it does

- `RAG.md` is the human-readable, evidence-labelled coaching corpus.
- `retrieve.py` is a **working offline text retriever** (Python standard library, no API key). It selects 4–8 relevant K/C/T sections for a question.
- Retrieval does **not** generate an AI answer. The selected excerpts and real session data still need to be given to an LLM. Neither the repository nor this script sends user data to an AI service.
- A snapshot of this RAG is embedded directly in locally generated `coach.html` by the TRAP TRAINER project's `tools/coach-html` generator, so the COACH can prepare a cited prompt without internet access. This snapshot is not updated live when GitHub changes.

## Quick test

Download or clone the repository and run:

```powershell
python retrieve.py --query "Ar per velai pajudejau?" --top 6
python retrieve.py --query "Kodel nepataikiau?" --top 6 --json
```

You should see sections such as `K-301`, `K-302`, `C-04`. The result is a retrieval suggestion, not a diagnosis.

## Using with an AI assistant

Paste the question, the specific retrieved excerpts (with their section IDs), and your **actual** series data into the assistant. Ask it to distinguish observed facts, hypotheses and unknowns, and to give one testable coaching change. Do not claim the assistant consulted the RAG unless it was actually included or opened.

Direct text: https://raw.githubusercontent.com/lit-u/olympic-trap-coach-rag/main/RAG.md

## Limitations

This repository intentionally contains no private sessions, firmware or secret credentials. Search is deterministic keyword retrieval, not embeddings/vector search or a hosted chat endpoint. The initial corpus is curated rather than an exhaustive copy of every conversation. Reference links and ISSF revisions must be checked independently before strong factual claims. ESP32 gyro recordings cannot reveal eye gaze, neural perception time or the human cause of a MISS.

## Sync / versioning

COACH can report the embedded corpus SHA256. To update the snapshot after changes to `RAG.md`, update the private project's `tools/coach-html/rag/RAG.md` copy and regenerate the standalone `coach.html`; existing saved series must be preserved by the converter. Do not silently overwrite users' records.
