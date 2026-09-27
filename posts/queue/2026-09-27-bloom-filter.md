---
slug: bloom-filter
area: data engineering
concept: Bloom filter
source: Designing Data-Intensive Applications
created: '2026-09-27'
---

Ask the filter before the DB.

Bloom filter is a probabilistic set with false positives only.
It fits in memory and answers membership in O(1).
Great for caching existence checks, like duplicate detection.
Misses trigger a full lookup; false positives just waste a read.
