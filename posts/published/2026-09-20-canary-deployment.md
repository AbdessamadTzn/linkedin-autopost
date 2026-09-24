---
slug: canary-deployment
area: cloud infrastructure
concept: canary deployment
source: AWS Well-Architected Framework
created: '2026-09-20'
published_at: '2026-09-24T06:42:20.481322+00:00'
post_id: urn:li:share:7508777825764831232
---

Roll out to a few, watch, then expand.

Canary deployment routes a fraction of traffic to a new version.
Monitors key metrics before full promotion.
Skipping canary lets bugs reach all users instantly.
Automate rollback based on SLA breach thresholds.
