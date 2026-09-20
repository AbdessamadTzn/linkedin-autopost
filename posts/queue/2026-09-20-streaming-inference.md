---
slug: streaming-inference
area: LLMs and RAG
concept: streaming inference
source: AI Engineering
created: '2026-09-20'
---

Generate tokens as they arrive.

Streaming inference returns partial outputs instead of waiting for full result.
Lowers latency for interactive applications and reduces client memory.
Requires server‑side token flushing and back‑end concurrency control.
Dropping streaming forces batch latency on every request.
