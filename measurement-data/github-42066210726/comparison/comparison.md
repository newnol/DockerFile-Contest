# Python contest comparison

Median (min–max) over repeats. Each repeat is an independent GitHub-hosted runner.

| Recipe | Runtime pass | Image MiB | gzip MiB | Cold s | Warm s | Source-change s | Startup s | Idle RAM MiB | Stop s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 5/5 | 200.59 (200.59–200.59) | 87.92 (87.92–87.92) | 11.91 (11.66–12.96) | 0.900 (0.505–0.954) | 9.498 (8.235–9.929) | 2.84 (1.74–3.02) | 55.3 (55.2–55.4) | 0.39 (0.33–0.42) |
| TOP 1 | 5/5 | 101.82 (101.82–101.82) | 32.88 (32.88–32.89) | 9.33 (8.78–14.81) | 0.387 (0.230–0.477) | 0.439 (0.418–0.550) | 2.30 (1.70–2.33) | 54.6 (54.3–54.6) | 0.38 (0.27–0.40) |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 5/5 | 65.46 (65.46–65.46) | 22.93 (22.93–22.94) | 22.45 (20.97–25.51) | 0.546 (0.489–0.581) | 0.929 (0.842–1.684) | 3.37 (2.30–6.46) | 48.4 (48.2–48.6) | 0.38 (0.37–0.45) |
| Production (gộp lợi thế, lock mới) | 5/5 | 68.59 (68.59–68.59) | 24.24 (24.23–24.24) | 10.19 (8.68–11.09) | 0.440 (0.370–0.588) | 0.567 (0.502–1.249) | 1.82 (1.19–1.88) | 47.0 (46.9–47.4) | 0.36 (0.31–0.51) |

## Trivy (vulnerability scanner only, one scan per recipe)

| Recipe | CRITICAL | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---:|---:|---:|---:|---:|
| Default (docker-example.txt) | 2 | 17 | 29 | 22 | 0 |
| TOP 1 | 3 | 19 | 60 | 50 | 3 |
| TOP 2 - bài của em (FastAPI pin 0.120.4) | 2 | 27 | 34 | 52 | 2 |
| Production (gộp lợi thế, lock mới) | 0 | 5 | 2 | 1 | 0 |

## Reproducibility

- Default (docker-example.txt): 1 distinct installed-package set(s), 5 distinct image size(s) across 5 repeats.
- TOP 1: 1 distinct installed-package set(s), 1 distinct image size(s) across 5 repeats.
- TOP 2 - bài của em (FastAPI pin 0.120.4): 1 distinct installed-package set(s), 1 distinct image size(s) across 5 repeats.
- Production (gộp lợi thế, lock mới): 1 distinct installed-package set(s), 2 distinct image size(s) across 5 repeats.

## Interpretation
- Same source commit, linux/amd64, ubuntu-24.04 runner class; runner hardware/network still vary between jobs.
- Cold: fresh BuildKit builder, --pull --no-cache. Warm: unchanged input. Source-change: one appended Python comment. Timings include --load export.
- Image MiB = docker inspect .Size (uncompressed). gzip MiB = gzip of docker save, an approximation of registry transfer size.
- Startup = docker run until /health/ is HEALTHY and homepage renders, polled every 0.5 s. Idle RAM sampled 5 s after startup.
- Whole recipes are compared: bases and dependency versions differ, so no single technique is isolated.
- TOP 2 is adapted by one line (fastapi==0.120.4) because unpinned FastAPI 0.162 breaks the instrumentator; original failure: run 41990729849.
- Production recipe uses its own hashed lock (benchmarks/prod/requirements.txt) with current dependency versions, so its CVE counts reflect newer dependencies as well as Dockerfile technique.
- Coffee API points to a local stub; this is a packaging smoke test, not a functional or load test.
