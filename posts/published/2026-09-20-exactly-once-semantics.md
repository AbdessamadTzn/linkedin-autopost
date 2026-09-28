---
slug: exactly-once-semantics
area: data engineering
concept: exactly-once semantics
source: Designing Data-Intensive Applications
created: '2026-09-20'
published_at: '2026-09-28T06:57:11.382249+00:00'
post_id: urn:li:share:7510231114326929408
---

Process each event a single time.

Exactly‑once semantics guarantees no duplicate or missing records in pipelines.
Implemented with idempotent sinks and transactional checkpoints.
Without it, downstream aggregates become biased and state diverges.
Choose a stream platform that supports atomic commits.
