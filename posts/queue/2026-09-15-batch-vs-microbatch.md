---
slug: batch-vs-microbatch
area: data engineering
concept: Batch vs microbatch
source: Fundamentals of Data Engineering
created: '2026-09-15'
---

Batch big, microbatch fast.

Batch processing groups all data before a job runs.
Microbatch splits data into small windows for near‑real‑time.
Large batches improve throughput, microbatches improve latency.
Choose based on SLA: latency‑sensitive pipelines use microbatch.
