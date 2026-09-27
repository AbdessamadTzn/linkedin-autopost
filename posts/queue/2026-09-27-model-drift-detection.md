---
slug: model-drift-detection
area: MLOps
concept: Model drift detection
source: Designing Machine Learning Systems
created: '2026-09-27'
---

Watch the data, not just the loss.

Model drift monitors changes in input feature distribution over time.
Statistical tests like KS or PSI flag when drift exceeds a threshold.
Trigger retraining pipelines before performance degrades.
Ignoring drift keeps serving stale predictions.
