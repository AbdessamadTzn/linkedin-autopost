---
slug: feature-store-versioning
area: MLOps
concept: feature store versioning
source: Designing Machine Learning Systems
created: '2026-09-20'
---

Feature pipelines need immutable snapshots.

Feature store versioning pins a feature set to a model release.
Guarantees reproducible inference when training data evolves.
Missing version control causes drift between training and serving.
Store schema and transformation code alongside version tags.
