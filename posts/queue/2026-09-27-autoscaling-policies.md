---
slug: autoscaling-policies
area: cloud infrastructure
concept: Autoscaling policies
source: AWS Well-Architected Framework
created: '2026-09-27'
---

Scale right, pay light.

Autoscaling policies define metrics and thresholds for adding/removing instances.
Target tracking keeps CPU or request latency near a set point.
Cool‑down periods avoid thrashing during traffic spikes.
Bad policies either overload services or waste money.
