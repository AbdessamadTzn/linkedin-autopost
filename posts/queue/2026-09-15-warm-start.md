---
slug: warm-start
area: cloud infrastructure
concept: Warm start vs cold start
source: AWS Well-Architected Framework
created: '2026-09-15'
---

Cold start kills latency.

Cold start spins a new container before handling a request.
Warm start reuses an already initialized instance, cutting response time.
In serverless, frequent cold starts increase tail latency.
Keep functions hot with provisioned concurrency or keep‑alive pools.
