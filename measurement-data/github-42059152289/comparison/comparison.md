# Python contest comparison

Median (min–max) over repeats. Each repeat is an independent GitHub-hosted runner.

| Recipe | Runtime pass | Image MiB | gzip MiB | Cold s | Warm s | Source-change s | Startup s | Idle RAM MiB | Stop s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 5/5 | 200.50 (200.50–200.50) | 87.88 (87.88–87.89) | 15.07 (11.57–15.56) | 0.797 (0.630–0.913) | 10.269 (9.008–11.897) | 2.82 (2.25–2.84) | 55.2 (54.9–55.9) | 0.35 (0.33–0.48) |
| TOP 1 | 5/5 | 101.82 (101.82–101.82) | 32.88 (32.88–32.88) | 9.77 (8.01–11.37) | 0.393 (0.305–0.416) | 0.495 (0.447–0.544) | 2.28 (1.75–2.31) | 54.4 (54.1–54.7) | 0.35 (0.30–0.40) |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 5/5 | 65.46 (65.46–65.46) | 22.94 (22.93–22.94) | 21.08 (18.97–22.04) | 0.431 (0.344–0.534) | 0.806 (0.716–0.904) | 2.24 (1.72–2.85) | 48.2 (48.2–48.5) | 0.35 (0.33–0.45) |

## Trivy (vulnerability scanner only, one scan per recipe)

| Recipe | CRITICAL | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 2 | 17 | 29 | 22 | 0 |
| TOP 1 | 3 | 19 | 60 | 50 | 3 |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 2 | 27 | 34 | 52 | 2 |

## Reproducibility

- Default (docker-example.txt): 1 distinct installed-package set(s), 4 distinct image size(s) across 5 repeats.
- TOP 1: 1 distinct installed-package set(s), 1 distinct image size(s) across 5 repeats.
- TOP 2 - bài của em (FastAPI pin 0.120.4): 1 distinct installed-package set(s), 1 distinct image size(s) across 5 repeats.

## Interpretation
- Same source commit, linux/amd64, ubuntu-24.04 runner class; runner hardware/network still vary between jobs.
- Cold: fresh BuildKit builder, --pull --no-cache. Warm: unchanged input. Source-change: one appended Python comment. Timings include --load export.
- Image MiB = docker inspect .Size (uncompressed). gzip MiB = gzip of docker save, an approximation of registry transfer size.
- Startup = docker run until /health/ is HEALTHY and homepage renders, polled every 0.5 s. Idle RAM sampled 5 s after startup.
- Whole recipes are compared: bases and dependency versions differ, so no single technique is isolated.
- TOP 2 is adapted by one line (fastapi==0.120.4) because unpinned FastAPI 0.162 breaks the instrumentator; original failure: run 41990729849.
- Coffee API points to a local stub; this is a packaging smoke test, not a functional or load test.
