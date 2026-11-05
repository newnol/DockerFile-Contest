# Python contest comparison

| Variant | Image MiB | Cold s | Warm s | Source-change s | Runtime | Startup s |
|---|---:|---:|---:|---:|---|---:|
| default | 200.51 | 11.778 | 0.858 | 9.349 | failed | N/A |
| top-entry3 | 207.48 | 33.664 | 0.953 | 20.801 | failed | N/A |
| top1 | 101.82 | 11.663 | 0.41 | 0.656 | failed | N/A |
| top2 | 65.74 | 22.119 | 0.472 | 0.751 | failed | N/A |

## Size difference against default
- default: 0.00% smaller (negative means larger); runtime failed.
- top-entry3: -3.48% smaller (negative means larger); runtime failed.
- top1: 49.22% smaller (negative means larger); runtime failed.
- top2: 67.21% smaller (negative means larger); runtime failed.

## Interpretation
- Fresh rebuild, not historical contest results. top-entry3 is the third displayed Python TOP entry, NOT a confirmed rank 3.
- Same source commit, linux/amd64, ubuntu-24.04 runner class. Four independent runners: hardware/network timing variance remains; one sample, not a statistical benchmark.
- Cold uses a fresh BuildKit builder with --pull --no-cache. Warm repeats unchanged input; source-change appends only a Python comment. Timings include image load/export, exclude builder setup.
- Cold package cache mounts can warm later rebuilds within each job; no cache is shared between variants or restored from GHA.
- Image MiB is Docker inspect local uncompressed size, NOT registry download size. Inspect/history/packages and logs are retained as artifacts.
- Dockerfiles intentionally resolve different dependencies and bases. This compares whole recipes, not an isolated optimization. Mutable tags/dependency ranges may change on rerun.
- Smoke overrides PORT=5000 and WORKERS=1, 1 CPU/512 MiB. Checks /health/ JSON and homepage; not full functional equivalence or load testing.
- No CVE count claimed: no fresh security scan in this workflow. Labels/comments from original submissions are not verified security evidence.
- Failed recipes are preserved without dependency or source repairs. See per-variant logs.
