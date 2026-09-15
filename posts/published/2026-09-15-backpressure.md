---
slug: backpressure
area: system design
concept: Backpressure
source: Designing Data-Intensive Applications
created: '2026-09-15'
published_at: '2026-09-15T12:49:40.577218+00:00'
post_id: urn:li:share:7505608778973618176
---

Never let a fast producer drown the consumer.

Backpressure signals the consumer to slow the upstream flow.
It keeps memory bounded in streaming pipelines.
Ignoring backpressure leads to out‑of‑memory crashes.
Use bounded queues or reactive streams to enforce it.
