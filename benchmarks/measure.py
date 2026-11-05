"""Measure unchanged contest Dockerfiles; failures are data, not repairs."""
import gzip
import hashlib
import json
import os
import statistics
from pathlib import Path
import platform
import subprocess
import sys
import time
import urllib.request
from typing import Any
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


class CoffeeStub(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path == '/hot' else 404)
        self.end_headers()
        self.wfile.write(b'[]')

    def log_message(self, format, *args):
        """Silence per-request logging; the stub is only a fixture."""


def run(args, **kwargs):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)


class ProbeError(Exception):
    """The container answered, but not with the expected content."""


def probe():
    with urllib.request.urlopen('http://127.0.0.1:5000/health/', timeout=1) as response:
        body = json.load(response)
        if body.get('heartbeat') != 'HEALTHY':
            raise ProbeError(f'unhealthy: {body}')
    with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=1) as response:
        if 'Dockerfile Contest 2025' not in response.read().decode():
            raise ProbeError('homepage marker missing')


def wait_ready(result, start):
    """Poll every 0.5 s until health + homepage pass or the container exits."""
    for _ in range(120):
        try:
            probe()
            result.update(runtime='passed', startup_seconds=round(time.monotonic()-start, 3))
            return
        except (OSError, ValueError, ProbeError) as exc:
            result['last_probe_error'] = str(exc)
        state = run(['docker', 'inspect', '--format', '{{.State.Running}}', 'benchmark-app'])
        if state.stdout.strip() != 'true':
            return
        time.sleep(0.5)


def measure(variant):
    out = Path('results')
    out.mkdir(exist_ok=True)
    dockerfile = f'benchmarks/dockerfiles/{variant}.Dockerfile'
    image = f'contest-benchmark:{variant}'
    result: dict[str, Any] = dict(variant=variant, repeat=int(os.environ.get('REPEAT', '1')),
                                  commit=os.environ.get('GITHUB_SHA'), platform='linux/amd64',
                                  runner=platform.platform(), cpu_count=os.cpu_count(), builds={})
    base = ['docker', 'buildx', 'build', '--platform', 'linux/amd64', '--load',
            '--progress=plain', '-f', dockerfile, '-t', image]
    stub = ThreadingHTTPServer(('0.0.0.0', 8765), CoffeeStub)
    Thread(target=stub.serve_forever, daemon=True).start()
    try:
        for mode in ('cold', 'warm', 'source-change'):
            if mode == 'source-change':
                with Path('src/python_service_template/app.py').open('a') as f:
                    f.write('\n# benchmark: nonfunctional source change\n')
            start = time.monotonic()
            p = run(base + (['--pull', '--no-cache'] if mode == 'cold' else []) + ['.'], timeout=1500)
            (out / f'{mode}.log').write_text(p.stdout)
            result['builds'][mode] = dict(seconds=round(time.monotonic()-start, 3), exit_code=p.returncode,
                                          cached_log_lines=sum(line.endswith(' CACHED') for line in p.stdout.splitlines()))
            if p.returncode:
                break
        if result['builds']['cold']['exit_code'] != 0:
            result['runtime'] = 'not built'
            return
        info = json.loads(run(['docker', 'image', 'inspect', image]).stdout)[0]
        (out / 'image-inspect.json').write_text(json.dumps(info, indent=2))
        result.update(image_id=info['Id'], image_bytes=info['Size'], layer_count=len(info['RootFS']['Layers']),
                      configured_user=info['Config'].get('User'), base_images=info.get('RepoDigests'))
        (out / 'history.jsonl').write_text(run(['docker', 'history', '--no-trunc', '--format', '{{json .}}', image]).stdout)
        packages = run(['docker', 'run', '--rm', '--network=none', '--entrypoint', 'python', image, '-c',
                        'import importlib.metadata,json; print(json.dumps(sorted((d.metadata["Name"],d.version) for d in importlib.metadata.distributions())))'])
        (out / 'packages.json').write_text(packages.stdout)
        result['packages_sha256'] = hashlib.sha256(packages.stdout.encode()).hexdigest()
        result['gzip_bytes'] = gzip_size(image)
        if os.environ.get('TRIVY_IMAGE'):
            result['cves'] = trivy(image, os.environ['TRIVY_IMAGE'], out)
        start = time.monotonic()
        p = run(['docker', 'run', '-d', '--name', 'benchmark-app', '--cpus=1', '--memory=512m',
                 '--add-host', 'host.docker.internal:host-gateway',
                 '-e', 'COFFEE_API__HOST=http://host.docker.internal:8765',
                 '-e', 'PORT=5000', '-e', 'WORKERS=1', '-p', '127.0.0.1:5000:5000', image])
        (out / 'container-start.txt').write_text(p.stdout)
        result['runtime'] = 'failed'
        if p.returncode == 0:
            wait_ready(result, start)
            (out / 'container-inspect.json').write_text(run(['docker', 'inspect', 'benchmark-app']).stdout)
            (out / 'container.log').write_text(run(['docker', 'logs', 'benchmark-app']).stdout)
            if result['runtime'] == 'passed':
                time.sleep(5)  # let startup work settle before sampling idle memory
                stats = run(['docker', 'stats', '--no-stream', '--format', '{{json .}}', 'benchmark-app']).stdout
                (out / 'stats.json').write_text(stats)
                result['idle_mem_mib'] = mem_mib(json.loads(stats)['MemUsage'].split('/')[0])
            start = time.monotonic()
            run(['docker', 'stop', '-t', '10', 'benchmark-app'])
            result['stop_seconds'] = round(time.monotonic()-start, 3)
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        stub.shutdown()
        stub.server_close()
        run(['docker', 'rm', '-f', 'benchmark-app'])
        (out / 'result.json').write_text(json.dumps(result, indent=2)+'\n')


UNITS = {'B': 1/1048576, 'KiB': 1/1024, 'MiB': 1, 'GiB': 1024}


def mem_mib(text):
    text = text.strip()
    for unit in sorted(UNITS, key=len, reverse=True):
        if text.endswith(unit):
            return round(float(text[:-len(unit)]) * UNITS[unit], 2)
    raise ValueError(text)


def gzip_size(image):
    """Approximate registry transfer size: gzip of `docker save` (layers are gzip-compressed on push)."""
    proc = subprocess.Popen(['docker', 'save', image], stdout=subprocess.PIPE)
    counter = _Counter()
    with gzip.GzipFile(fileobj=counter, mode='wb', compresslevel=6, mtime=0) as z:
        while chunk := proc.stdout.read(1 << 20):
            z.write(chunk)
    proc.wait()
    return counter.n


class _Counter:
    n = 0

    def write(self, b):
        self.n += len(b)

    def flush(self):
        """Nothing is buffered; only the byte count is kept."""


def trivy(image, trivy_image, out):
    p = subprocess.run(['docker', 'run', '--rm', '-v', '/var/run/docker.sock:/var/run/docker.sock', trivy_image,
                        'image', '--quiet', '--scanners', 'vuln', '--format', 'json', image],
                       text=True, capture_output=True, timeout=900)
    (out / 'trivy.json').write_text(p.stdout)
    (out / 'trivy.log').write_text(p.stderr)
    if p.returncode:
        return {'error': p.returncode}
    report = json.loads(p.stdout)
    counts = dict.fromkeys(SEVERITIES, 0)
    for target in report.get('Results') or []:
        for v in target.get('Vulnerabilities') or []:
            counts[v['Severity']] = counts.get(v['Severity'], 0) + 1
    return counts


SEVERITIES = ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN')
VARIANTS = ('default', 'top1', 'top2')
LABELS = {'default': 'Default (docker-example.txt)', 'top1': 'TOP 1',
          'top2': 'TOP 2 - bài của em (FastAPI pin 0.120.4)'}


def stat(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return dict(n=len(values), median=round(statistics.median(values), 3),
                min=round(min(values), 3), max=round(max(values), 3))


def fmt(s, scale=1.0, digits=2):
    if not s:
        return 'N/A'
    return f"{s['median']*scale:.{digits}f} ({s['min']*scale:.{digits}f}–{s['max']*scale:.{digits}f})"


def summary(directory):
    rows = [json.loads(p.read_text()) for p in sorted(Path(directory).rglob('result.json'))]
    found = {r['variant'] for r in rows}
    assert found == set(VARIANTS), f'Expected variants {VARIANTS}, got {sorted(found)}'
    agg = {}
    for v in VARIANTS:
        rs = [r for r in rows if r['variant'] == v]
        ok = [r for r in rs if r.get('runtime') == 'passed']
        def build(mode):
            return stat([r['builds'][mode]['seconds'] for r in rs
                         if r['builds'].get(mode, {}).get('exit_code') == 0])
        cves = next((r['cves'] for r in rs if isinstance(r.get('cves'), dict) and 'error' not in r['cves']), None)
        agg[v] = dict(label=LABELS[v], repeats=len(rs), runtime_passed=len(ok),
                      image_mib=stat([r['image_bytes']/1048576 for r in rs if 'image_bytes' in r]),
                      gzip_mib=stat([r['gzip_bytes']/1048576 for r in rs if 'gzip_bytes' in r]),
                      layers=stat([r.get('layer_count') for r in rs]),
                      cold_s=build('cold'), warm_s=build('warm'), source_change_s=build('source-change'),
                      startup_s=stat([r.get('startup_seconds') for r in ok]),
                      stop_s=stat([r.get('stop_seconds') for r in ok]),
                      idle_mem_mib=stat([r.get('idle_mem_mib') for r in ok]),
                      distinct_package_sets=len({r.get('packages_sha256') for r in rs}),
                      distinct_image_sizes=len({r.get('image_bytes') for r in rs}), cves=cves)
    lines = ['# Python contest comparison', '',
             'Median (min–max) over repeats. Each repeat is an independent GitHub-hosted runner.', '',
             '| Recipe | Runtime pass | Image MiB | gzip MiB | Cold s | Warm s | Source-change s | Startup s | Idle RAM MiB | Stop s |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for v, a in agg.items():
        lines.append(f"| {a['label']} | {a['runtime_passed']}/{a['repeats']} | {fmt(a['image_mib'])} | {fmt(a['gzip_mib'])} | "
                     f"{fmt(a['cold_s'])} | {fmt(a['warm_s'], digits=3)} | {fmt(a['source_change_s'], digits=3)} | "
                     f"{fmt(a['startup_s'])} | {fmt(a['idle_mem_mib'], digits=1)} | {fmt(a['stop_s'])} |")
    lines += ['', '## Trivy (vulnerability scanner only, one scan per recipe)', '',
              '| Recipe | ' + ' | '.join(SEVERITIES) + ' |', '|---|' + '---:|' * len(SEVERITIES)]
    for a in agg.values():
        c = a['cves'] or {}
        lines.append(f"| {a['label']} | " + ' | '.join(str(c.get(s, 'N/A')) for s in SEVERITIES) + ' |')
    lines += ['', '## Reproducibility', '']
    for a in agg.values():
        lines.append(f"- {a['label']}: {a['distinct_package_sets']} distinct installed-package set(s), "
                     f"{a['distinct_image_sizes']} distinct image size(s) across {a['repeats']} repeats.")
    lines += ['', '## Interpretation',
              '- Same source commit, linux/amd64, ubuntu-24.04 runner class; runner hardware/network still vary between jobs.',
              '- Cold: fresh BuildKit builder, --pull --no-cache. Warm: unchanged input. Source-change: one appended Python comment. Timings include --load export.',
              '- Image MiB = docker inspect .Size (uncompressed). gzip MiB = gzip of docker save, an approximation of registry transfer size.',
              '- Startup = docker run until /health/ is HEALTHY and homepage renders, polled every 0.5 s. Idle RAM sampled 5 s after startup.',
              '- Whole recipes are compared: bases and dependency versions differ, so no single technique is isolated.',
              '- TOP 2 is adapted by one line (fastapi==0.120.4) because unpinned FastAPI 0.162 breaks the instrumentator; original failure: run 41990729849.',
              '- Coffee API points to a local stub; this is a packaging smoke test, not a functional or load test.', '']
    text = '\n'.join(lines)
    Path(directory, 'comparison.md').write_text(text)
    Path(directory, 'comparison.json').write_text(json.dumps(dict(aggregate=agg, runs=rows), indent=2, ensure_ascii=False)+'\n')
    with open(os.environ.get('GITHUB_STEP_SUMMARY', os.devnull), 'a') as f:
        f.write(text)
    print(text)


SUMMARY_DIR = 'collected'

if __name__ == '__main__':
    # Map CLI input onto known constants so no argument reaches paths or commands verbatim.
    if sys.argv[1] == 'summary':
        if sys.argv[2:] not in ([], [SUMMARY_DIR]):
            raise SystemExit(f'summary only reads ./{SUMMARY_DIR}')
        summary(SUMMARY_DIR)
    else:
        known = {v: v for v in VARIANTS}
        if sys.argv[1] not in known:
            raise SystemExit(f'unknown variant {sys.argv[1]!r}; expected one of {VARIANTS}')
        measure(known[sys.argv[1]])
