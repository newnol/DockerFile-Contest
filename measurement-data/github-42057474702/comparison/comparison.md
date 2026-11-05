# Python contest comparison

Median (min–max) over repeats. Each repeat is an independent GitHub-hosted runner.

| Recipe | Runtime pass | Image MiB | gzip MiB | Cold s | Warm s | Source-change s | Startup s | Idle RAM MiB | Stop s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 5/5 | 200.50 (200.50–200.50) | 87.89 (87.88–87.89) | 12.86 (11.84–14.26) | 0.752 (0.661–0.860) | 9.499 (8.949–12.384) | 2.39 (2.23–2.84) | 55.1 (54.9–55.6) | 0.36 (0.31–0.38) |
| TOP 1 | 5/5 | 101.82 (101.82–101.82) | 32.89 (32.88–32.89) | 9.23 (8.68–10.61) | 0.412 (0.228–0.477) | 0.475 (0.453–0.493) | 2.32 (1.69–2.50) | 54.3 (54.1–54.4) | 0.34 (0.32–0.42) |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 5/5 | 65.46 (65.46–65.46) | 22.94 (22.93–22.94) | 23.30 (20.04–26.62) | 0.486 (0.358–0.599) | 0.839 (0.748–0.923) | 3.08 (2.25–3.38) | 48.4 (48.1–48.6) | 0.35 (0.34–0.39) |

## Trivy (vulnerability scanner only, one scan per recipe)

| Recipe | CRITICAL | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 2 | 17 | 29 | 22 | 0 |
| TOP 1 | 3 | 19 | 60 | 50 | 3 |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 2 | 27 | 34 | 52 | 2 |

## Reproducibility

- Default (docker-example.txt): 1 distinct installed-package set(s), 5 distinct image size(s) across 5 repeats.
- TOP 1: 1 distinct installed-package set(s), 2 distinct image size(s) across 5 repeats.
- TOP 2 - bài của em (FastAPI pin 0.120.4): 1 distinct installed-package set(s), 1 distinct image size(s) across 5 repeats.

## Interpretation
- Same source commit, linux/amd64, ubuntu-24.04 runner class; runner hardware/network still vary between jobs.
- Cold: fresh BuildKit builder, --pull --no-cache. Warm: unchanged input. Source-change: one appended Python comment. Timings include --load export.
- Image MiB = docker inspect .Size (uncompressed). gzip MiB = gzip of docker save, an approximation of registry transfer size.
- Startup = docker run until /health/ is HEALTHY and homepage renders, polled every 0.5 s. Idle RAM sampled 5 s after startup.
- Whole recipes are compared: bases and dependency versions differ, so no single technique is isolated.
- TOP 2 is adapted by one line (fastapi==0.120.4) because unpinned FastAPI 0.162 breaks the instrumentator; original failure: run 41990729849.
- Coffee API points to a local stub; this is a packaging smoke test, not a functional or load test.

## Repeat runs (same recipes, later commits)
- Run 42058703830 and 42059152289 (`measurement-data/github-42058703830/`, `measurement-data/github-42059152289/`): image size and Trivy counts identical, gzip and idle RAM within 0.2 MiB; cold/source-change ordering unchanged; startup medians reorder between runs (TOP 2: 3.08 → 2.84 → 2.24 s), so startup is not ranked.
