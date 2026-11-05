# Python contest comparison

Median (min–max) over repeats. Each repeat is an independent GitHub-hosted runner.

| Recipe | Runtime pass | Image MiB | gzip MiB | Cold s | Warm s | Source-change s | Startup s | Idle RAM MiB | Stop s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 5/5 | 200.50 (200.50–200.50) | 87.88 (87.88–87.89) | 12.61 (11.38–12.68) | 0.823 (0.492–0.996) | 9.074 (8.938–9.517) | 2.82 (2.30–2.85) | 55.3 (54.9–55.5) | 0.39 (0.38–0.45) |
| TOP 1 | 5/5 | 101.82 (101.82–101.82) | 32.88 (32.88–32.88) | 9.98 (7.95–14.27) | 0.393 (0.267–0.462) | 0.508 (0.443–0.663) | 2.26 (2.09–8.19) | 54.5 (54.2–54.7) | 0.34 (0.29–0.42) |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 5/5 | 65.46 (65.46–65.46) | 22.94 (22.93–22.94) | 23.01 (20.65–25.26) | 0.571 (0.475–0.975) | 0.890 (0.842–1.878) | 2.84 (2.30–2.97) | 48.3 (48.0–48.5) | 0.35 (0.34–0.55) |

## Trivy (vulnerability scanner only, one scan per recipe)

| Recipe | CRITICAL | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 2 | 17 | 29 | 22 | 0 |
| TOP 1 | 3 | 19 | 60 | 50 | 3 |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 2 | 27 | 34 | 52 | 2 |

## Reproducibility

- Default (docker-example.txt): 1 distinct installed-package set(s), 4 distinct image size(s) across 5 repeats.
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
