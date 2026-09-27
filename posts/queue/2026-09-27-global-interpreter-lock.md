---
slug: global-interpreter-lock
area: Python performance
concept: Global Interpreter Lock
source: Fluent Python
created: '2026-09-27'
---

One lock, many threads.

Python's Global Interpreter Lock allows only one thread to execute bytecode.
CPU‑bound code sees no parallel speedup with threading.
Use multiprocessing or C extensions to bypass the GIL.
Ignoring it leads to wasted cores on data‑parallel workloads.
