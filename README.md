# Olympic Trap AI COACH RAG

Practical Olympic Trap / ESP32 Gyro coaching knowledge base, **v0.2 (2026-11-23)**.

## Contents

- `RAG.md`: **52 retained knowledge IDs** (K/C/T). Training principles, ballistic and IMU limits, analysis safeguards, and practical drills.
- `knowledge_index.json`: seven-field manual classification of all 52 IDs and 36 typed, curated relations.
- `retrieve.py`: offline **BM25** text retrieval, Lithuanian/English query routing and limited knowledge-link expansion. Standard-library only, no network calls.
- No embeddings, hosted vector database, automatic causal discovery or full Microsoft GraphRAG.

## Core coaching method

**CATCH → BODY TURN → CONTINUOUS FIRE → RHYTHM → CORRECT REPETITION → AUTOMATICITY.**

A possible training flow is LOOK/PREVIEW to learn the range of target flights, a short block of repeated directions to feel the torso-led motion, and mixed unpredictable H1 series to test transfer. H2 can be used for relaxed rhythm practice; H3 is recreational. **H1, H2 and H3 scores must not be pooled for mastery rankings.**

The Gyro observes orientation and angular speed; it **cannot tell whether the athlete actually turned the torso, focused their eyes or tensed the abdomen**. These remain practice cues / hypotheses rather than sensor-confirmed diagnoses.

Static/rifle breath-holding or heartbeat-trigger timing are **not part of this Olympic Trap coaching method**. Sources are kept as internal evidence, not names or historical quotations in normal shooter-facing coaching.

## Quick tests

```powershell
python retrieve.py --query "Kaip geriau pagauti lekste ir sukti korpusa?" --top 6
python retrieve.py --query "Pavargsta akys ir prarandu ritma" --top 6
python retrieve.py --query "Kodel H2 pataikau o H1 ne?" --top 6 --json
python retrieve.py --query "Ar reikia sulaikyti kvepavima?" --top 6
```

The last query should never turn rifle breathing practice into an Olympic Trap prescription.

## Limitations and integration

This is a **public** repository: its entire `RAG.md` and `knowledge_index.json` can be read by anyone. The repository contains no private series, firmware, personal profiles or secrets.

The separate private firmware project holds a **versioned copy** of its RAG; updating this public repository **does not change existing ESP32 firmware or already-exported COACH HTML**. A public offline COACH UI may distribute *prompt-only* context without bundling the corpus. Rebuilding any private copy or generated UI is a distinct integration step.

All coaching claims must keep measurement limitations and source provenance internally. If a user's recorded metrics are missing, report N/A rather than pretending the training hypothesis was confirmed.
