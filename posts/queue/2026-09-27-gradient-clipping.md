---
slug: gradient-clipping
area: machine learning
concept: Gradient clipping
source: Hands-On Machine Learning
created: '2026-09-27'
---

Clamp gradients before they explode.

Gradient clipping caps the norm of back‑propagated gradients.
Prevents exploding updates in deep or recurrent nets.
Common thresholds: 1.0 or 5.0 L2 norm.
Without clipping training can diverge or become unstable.
