"""Small offline regression check; temporary fixtures are test data only."""
import contextlib
import io
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from measure import summary, CoffeeStub
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen


def test_summary():
    server = ThreadingHTTPServer(('127.0.0.1', 0), CoffeeStub)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with urlopen(f'http://127.0.0.1:{server.server_port}/hot') as response:
            assert response.status == 200 and json.load(response) == []
    finally:
        server.shutdown()
        server.server_close()
    with tempfile.TemporaryDirectory() as tmp:
        for variant in ('default', 'top1', 'top2', 'top-entry3'):
            p = Path(tmp, variant)
            p.mkdir()
            row = dict(variant=variant, builds={'cold': dict(seconds=1, exit_code=0)},
                       image_bytes=1048576, runtime='passed')
            if variant == 'top-entry3':
                row = dict(variant=variant, builds={'cold': dict(seconds=1, exit_code=1)}, runtime='not built')
            (p / 'result.json').write_text(json.dumps(row))
        with contextlib.redirect_stdout(io.StringIO()):
            summary(tmp)
        text = Path(tmp, 'comparison.md').read_text()
        assert 'FAILED / unavailable' in text
        assert len(json.loads(Path(tmp, 'comparison.json').read_text())) == 4
        Path(tmp, 'top1', 'result.json').unlink()
        try:
            summary(tmp)
        except AssertionError:
            pass
        else:
            raise AssertionError('Missing variant must not yield a valid comparison')
    print('PASS: four rows, failure preserved, missing artifact rejected')


if __name__ == '__main__':
    test_summary()
