"""Measure unchanged contest Dockerfiles; failures are data, not repairs."""
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import urllib.request
from typing import Any


def run(args, **kwargs):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)


def measure(variant):
    out = Path('results')
    out.mkdir(exist_ok=True)
    dockerfile = f'benchmarks/dockerfiles/{variant}.Dockerfile'
    image = f'contest-benchmark:{variant}'
    result: dict[str, Any] = dict(variant=variant, commit=os.environ.get('GITHUB_SHA'), platform='linux/amd64',
                  runner=platform.platform(), cpu_count=os.cpu_count(), builds={})
    base = ['docker', 'buildx', 'build', '--platform', 'linux/amd64', '--load',
            '--progress=plain', '-f', dockerfile, '-t', image]
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
        start = time.monotonic()
        p = run(['docker', 'run', '-d', '--name', 'benchmark-app', '--cpus=1', '--memory=512m',
                 '-e', 'PORT=5000', '-e', 'WORKERS=1', '-p', '127.0.0.1:5000:5000', image])
        (out / 'container-start.txt').write_text(p.stdout)
        result['runtime'] = 'failed'
        if p.returncode == 0:
            for _ in range(120):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:5000/health/', timeout=1) as response:
                        body = json.load(response)
                        assert body.get('heartbeat') == 'HEALTHY', body
                    with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=1) as response:
                        assert 'Dockerfile Contest 2025' in response.read().decode()
                    result.update(runtime='passed', startup_seconds=round(time.monotonic()-start, 3))
                    break
                except Exception:
                    state = run(['docker', 'inspect', '--format', '{{.State.Running}}', 'benchmark-app'])
                    if state.stdout.strip() != 'true':
                        break
                    time.sleep(0.5)
            (out / 'container-inspect.json').write_text(run(['docker', 'inspect', 'benchmark-app']).stdout)
            (out / 'container.log').write_text(run(['docker', 'logs', 'benchmark-app']).stdout)
            if result['runtime'] == 'passed':
                (out / 'stats.json').write_text(run(['docker', 'stats', '--no-stream', '--format', '{{json .}}', 'benchmark-app']).stdout)
            start = time.monotonic()
            run(['docker', 'stop', '-t', '10', 'benchmark-app'])
            result['stop_seconds'] = round(time.monotonic()-start, 3)
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        run(['docker', 'rm', '-f', 'benchmark-app'])
        (out / 'result.json').write_text(json.dumps(result, indent=2)+'\n')


def summary(directory):
    rows = [json.loads(p.read_text()) for p in sorted(Path(directory).rglob('result.json'))]
    assert len(rows) == 4 and len({r['variant'] for r in rows}) == 4, 'Expected all four variants'
    lines = ['# Python contest comparison', '',
             '| Variant | Image MiB | Cold s | Warm s | Source-change s | Runtime | Startup s |',
             '|---|---:|---:|---:|---:|---|---:|']
    for r in rows:
        builds = r['builds']
        def seconds(mode):
            v = builds.get(mode, {})
            return str(v['seconds']) if v.get('exit_code') == 0 else 'FAILED / unavailable'
        lines.append(f"| {r['variant']} | {round(r['image_bytes']/1048576, 2) if 'image_bytes' in r else 'N/A'} | {seconds('cold')} | {seconds('warm')} | {seconds('source-change')} | {r.get('runtime', 'error')} | {r.get('startup_seconds', 'N/A')} |")
    baseline = next(r for r in rows if r['variant'] == 'default')
    lines += ['', '## Size difference against default']
    for r in rows:
        if r.get('image_bytes') and baseline.get('image_bytes'):
            delta = (1-r['image_bytes']/baseline['image_bytes'])*100
            lines.append(f"- {r['variant']}: {delta:.2f}% smaller (negative means larger); runtime {r.get('runtime')}.")
    lines += ['', '## Interpretation',
              '- Fresh rebuild, not historical contest results. top-entry3 is the third displayed Python TOP entry, NOT a confirmed rank 3.',
              '- Same source commit, linux/amd64, ubuntu-24.04 runner class. Four independent runners: hardware/network timing variance remains; one sample, not a statistical benchmark.',
              '- Cold uses a fresh BuildKit builder with --pull --no-cache. Warm repeats unchanged input; source-change appends only a Python comment. Timings include image load/export, exclude builder setup.',
              '- Cold package cache mounts can warm later rebuilds within each job; no cache is shared between variants or restored from GHA.',
              '- Image MiB is Docker inspect local uncompressed size, NOT registry download size. Inspect/history/packages and logs are retained as artifacts.',
              '- Dockerfiles intentionally resolve different dependencies and bases. This compares whole recipes, not an isolated optimization. Mutable tags/dependency ranges may change on rerun.',
              '- Smoke overrides PORT=5000 and WORKERS=1, 1 CPU/512 MiB. Checks /health/ JSON and homepage; not full functional equivalence or load testing.',
              '- No CVE count claimed: no fresh security scan in this workflow. Labels/comments from original submissions are not verified security evidence.',
              '- Failed recipes are preserved without dependency or source repairs. See per-variant logs.', '']
    text = '\n'.join(lines)
    Path(directory, 'comparison.md').write_text(text)
    Path(directory, 'comparison.json').write_text(json.dumps(rows, indent=2)+'\n')
    with open(os.environ.get('GITHUB_STEP_SUMMARY', os.devnull), 'a') as f:
        f.write(text)
    print(text)


if __name__ == '__main__':
    if sys.argv[1] == 'summary':
        summary(sys.argv[2])
    else:
        measure(sys.argv[1])
