# Python contest comparison

| Variant | Image MiB | Cold s | Warm s | Source-change s | Runtime | Startup s |
|---|---:|---:|---:|---:|---|---:|
| default | 200.51 | 14.64 | 0.712 | 9.853 | passed | 2.37 |
| top-entry3 | 207.48 | 34.172 | 0.894 | 21.354 | passed | 1.897 |
| top1 | 101.82 | 11.85 | 0.307 | 0.491 | passed | 1.804 |
| top2 | 65.42 | 22.579 | 0.553 | 0.928 | passed | 2.849 |

## Size difference against default
- default: 0.00% smaller (negative means larger); runtime passed.
- top-entry3: -3.48% smaller (negative means larger); runtime passed.
- top1: 49.22% smaller (negative means larger); runtime passed.
- top2: 67.37% smaller (negative means larger); runtime passed.

## Interpretation
- Fresh rebuild, not historical contest results. top-entry3 is the third displayed Python TOP entry, NOT a confirmed rank 3.
- Same source commit, linux/amd64, ubuntu-24.04 runner class. Four independent runners: hardware/network timing variance remains; one sample, not a statistical benchmark.
- Cold uses a fresh BuildKit builder with --pull --no-cache. Warm repeats unchanged input; source-change appends only a Python comment. Timings include image load/export, exclude builder setup.
- Cold package cache mounts can warm later rebuilds within each job; no cache is shared between variants or restored from GHA.
- Image MiB is Docker inspect local uncompressed size, NOT registry download size. Inspect/history/packages and logs are retained as artifacts.
- Dockerfiles intentionally resolve different dependencies and bases. This compares whole recipes, not an isolated optimization. Mutable tags/dependency ranges may change on rerun.
- Smoke overrides PORT=5000 and WORKERS=1, 1 CPU/512 MiB. Checks /health/ JSON and homepage; not full functional equivalence or load testing.
- COFFEE_API__HOST points to a controlled local HTTP stub returning 200 and [] for /hot; this isolates packaging from external API availability. Not a live integration test.
- No CVE count claimed: no fresh security scan in this workflow. Labels/comments from original submissions are not verified security evidence.
- TOP 2 is adapted: FastAPI pinned to 0.120.4 to avoid the observed 0.162.0 incompatibility with instrumentator 7.1.0. Other recipes unchanged. Original run: 41990729849.
- Runtime failures remain visible in this report even when collection jobs succeed. See per-variant logs.
