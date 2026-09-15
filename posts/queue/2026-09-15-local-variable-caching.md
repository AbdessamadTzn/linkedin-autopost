---
slug: local-variable-caching
area: Python performance
concept: Local variable caching
source: High Performance Python
created: '2026-09-15'
---

Pull once, use many.

In Python, attribute lookups on objects are slower than local variables.
Assign the attribute to a local name before loops.
This reduces interpreter overhead and speeds tight loops.
Common in numeric code and data processing.
