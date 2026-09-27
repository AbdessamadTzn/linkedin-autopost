---
slug: consistent-hashing
area: system design
concept: Consistent hashing
source: Designing Data-Intensive Applications
created: '2026-09-27'
---

Map keys, not nodes.

Consistent hashing spreads keys across a ring of virtual nodes.
Adding or removing a physical server moves only a fraction of keys.
It prevents massive data reshuffling during scaling.
Used by DynamoDB, Cassandra, and many caching layers.
