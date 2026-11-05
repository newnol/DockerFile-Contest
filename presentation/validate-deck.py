from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parent
shots=ROOT/'screenshots';shots.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,channel='chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1,reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((ROOT/'9router-proposal.html').as_uri());page.evaluate('document.fonts.ready')
 result={'browser':b.version,'slides':page.locator('.slide').count(),'screenshots':[],'bounds_issues':[],'title_words':[]}
 for i in range(16):
  page.evaluate('(i)=>deck.showSlide(i)',i);page.wait_for_timeout(80)
  bounds=page.evaluate('''()=>{const s=document.querySelector('.slide.active');return [...s.querySelectorAll('svg text')].filter(t=>{const r=t.getBBox();return r.x<0||r.x+r.width>1920||r.y<280||r.y+r.height>985}).map(t=>t.textContent)}''')
  if bounds:result['bounds_issues'].append({'slide':i+1,'labels':bounds})
  name=shots/f'slide-{i+1:02}.png';page.screenshot(path=str(name));result['screenshots'].append(str(name))
  result['title_words'].append(page.locator('.active h1').inner_text())
 page.keyboard.press('Home');assert page.evaluate('deck.currentSlide')==0
 page.keyboard.press('ArrowRight');assert page.evaluate('deck.currentSlide')==1
 page.keyboard.press('End');assert page.evaluate('deck.currentSlide')==15
 page.keyboard.press('ArrowRight');assert page.evaluate('deck.currentSlide')==15
 result['keyboard']='Home/ArrowRight/End/clamping PASS'
 result['network_dependencies']=page.locator('script[src],link[href],img[src]').count()
 for w,h in [(1920,1080),(390,844)]:
  page.set_viewport_size({'width':w,'height':h});page.evaluate('deck.showSlide(13)');page.wait_for_timeout(80)
  rect=page.locator('.deck-stage').bounding_box();assert abs(rect['width']/rect['height']-16/9)<.001
  page.screenshot(path=str(shots/f'viewport-{w}x{h}.png'))
 result['viewport']='1920x1080, 1280x720, 390x844 fixed ratio PASS'
 result['errors']=errors
 (ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k!='screenshots'},ensure_ascii=False,indent=2))
 b.close()
