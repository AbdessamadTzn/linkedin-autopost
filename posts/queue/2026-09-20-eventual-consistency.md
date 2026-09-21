---
slug: eventual-consistency
area: data engineering
concept: eventual consistency
source: Designing Data-Intensive Applications
created: '2026-09-20'
---

All replicas agree… eventually.

Eventual consistency lets writes succeed without waiting for all nodes.
Reads may return stale data until replication finishes.
It enables high availability but requires conflict resolution logic.
Ignoring it leads to surprising mismatches in distributed reads.
