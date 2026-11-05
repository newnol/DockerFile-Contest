"""Small offline regression check; temporary fixtures are test data only."""
import contextlib
import io
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from measure import summary, mem_mib, CoffeeStub, VARIANTS
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen


def test_stub():
    server = ThreadingHTTPServer(('127.0.0.1', 0), CoffeeStub)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with urlopen(f'http://127.0.0.1:{server.server_port}/hot') as response:
            assert response.status == 200 and json.load(response) == []
    finally:
        server.shutdown()
        server.server_close()


def test_mem_mib():
    assert mem_mib('55.41MiB ') == 55.41
    assert mem_mib('1.5GiB') == 1536
    assert mem_mib('512KiB') == 0.5


def _row(variant, repeat, cold, ok=True):
    builds = {m: dict(seconds=cold / (i + 1), exit_code=0) for i, m in enumerate(('cold', 'warm', 'source-change'))}
    row = dict(variant=variant, repeat=repeat, builds=builds, image_bytes=1048576 * 10, gzip_bytes=1048576 * 4,
               layer_count=5, packages_sha256='a' * 64, runtime='passed' if ok else 'failed',
               startup_seconds=2.0, stop_seconds=0.3, idle_mem_mib=50.0)
    if repeat == 1:
        row['cves'] = dict(CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3, UNKNOWN=0)
    return row


def test_summary_aggregates_repeats():
    with tempfile.TemporaryDirectory() as tmp:
        for v in VARIANTS:
            for r, cold in enumerate((10, 30, 20), 1):
                p = Path(tmp, f'{v}-{r}')
                p.mkdir()
                (p / 'result.json').write_text(json.dumps(_row(v, r, cold, ok=not (v == 'top2' and r == 2))))
        with contextlib.redirect_stdout(io.StringIO()):
            summary(tmp)
        agg = json.loads(Path(tmp, 'comparison.json').read_text())['aggregate']
        assert agg['default']['cold_s'] == dict(n=3, median=20, min=10, max=30)
        assert agg['top2']['runtime_passed'] == 2 and agg['top2']['startup_s']['n'] == 2
        assert agg['top1']['cves']['HIGH'] == 1
        assert '2/3' in Path(tmp, 'comparison.md').read_text()
        for p in Path(tmp).glob('top1-*'):
            (p / 'result.json').unlink()
        try:
            summary(tmp)
        except AssertionError:
            pass
        else:
            raise AssertionError('Missing variant must not yield a valid comparison')
