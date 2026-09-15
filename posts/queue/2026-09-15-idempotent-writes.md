---
slug: idempotent-writes
area: system design
concept: Idempotent writes
source: Designing Data-Intensive Applications
created: '2026-09-15'
---

Write once, repeat safely.

Idempotent writes guarantee the same result no matter how many times they run.
They prevent duplicate records in distributed databases.
Without idempotency, retries can corrupt state and break downstream pipelines.
Implement with upserts or dedup keys.
