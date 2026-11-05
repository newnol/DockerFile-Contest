"""Run with the same Playwright interpreter/libraries as ../validate-deck.py."""
from pathlib import Path
import json
import re
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1280, 'height': 720}, reduced_motion='reduce')
    remote = []
    page.on('request', lambda r: remote.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    page.goto((root / '9router-proposal.html').as_uri())
    page.evaluate('document.fonts.ready')
    images = page.evaluate('''async()=>{let out=[];for(const e of document.querySelectorAll('image.official-mark')){const img=new Image();img.src=e.getAttribute('href');await img.decode();out.push({brand:e.dataset.brand,loaded:img.naturalWidth>0})}return out}''')
    assert len(images) == 12 and all(x['loaded'] for x in images)
    collisions = page.evaluate('''()=>{let bad=[];for(const [i,s] of [...document.querySelectorAll('.slide')].entries()){for(const e of s.querySelectorAll('image.official-mark')){let a=e.getBBox();if(a.x<0||a.y<280||a.x+a.width>1920||a.y+a.height>985)bad.push([i+1,'bounds']);for(const t of s.querySelectorAll('svg text')){let c=t.getBBox();if(a.x<c.x+c.width&&a.x+a.width>c.x&&a.y<c.y+c.height&&a.y+a.height>c.y)bad.push([i+1,t.textContent])}}}return bad}''')
    assert not collisions, collisions
    titles = page.locator('h1').all_text_contents()
    assert len(titles) == 16 and all(2 <= len(t.split()) <= 3 for t in titles)
    assert re.findall(r'^## Slide \d+ — (.+)$', (root / 'speaker-notes.md').read_text(), re.M) == titles
    assert not remote, remote
    result = {'images': images, 'external_requests': remote, 'image_text_collisions': collisions, 'title_notes_alignment': '16/16 PASS'}
    (root / 'assets' / 'image-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    browser.close()
