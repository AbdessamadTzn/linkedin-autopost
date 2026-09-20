---
slug: prompt-chaining
area: LLMs and RAG
concept: prompt chaining
source: AI Engineering
created: '2026-09-20'
---

One prompt can call another.

Prompt chaining links multiple LLM calls to build complex logic.
Each step refines context, reducing hallucination risk.
Over‑chaining without state passing blows token limits.
Use a deterministic template to pass outputs forward.
