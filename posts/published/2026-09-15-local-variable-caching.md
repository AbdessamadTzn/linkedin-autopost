---
slug: local-variable-caching
area: Python performance
concept: Local variable caching
source: High Performance Python
created: '2026-09-15'
published_at: '2026-09-22T06:41:48.695247+00:00'
post_id: urn:li:share:7508052917342470144
---

Pull once, use many.

In Python, attribute lookups on objects are slower than local variables.
Assign the attribute to a local name before loops.
This reduces interpreter overhead and speeds tight loops.
Common in numeric code and data processing.
