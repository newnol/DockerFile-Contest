"""Real Chromium checks and screenshots; run with Playwright Python."""
from pathlib import Path
import json, re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
html=ROOT/'presentation/python-contest-v2.html'
results={'slides':40,'viewports':{},'errors':[],'external_requests':[],'navigation':{},'diagrams':[]}
CHECK="""() => {const s=document.querySelector('.slide.active'), r=s.getBoundingClientRect();let issues=[];const els=[...s.querySelectorAll('header,h1,.visual,footer,article,small,strong,span,pre,.layer,.side,.filesystem,.band,.binary div,.binary-label,.row label,.row b')];for(const e of els){let b=e.getBoundingClientRect();if(b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1)issues.push('bounds: '+e.tagName+' '+e.textContent.slice(0,45));if(e.scrollWidth>e.clientWidth+2&&e.clientWidth>0)issues.push('overflow: '+e.className+' '+e.textContent.slice(0,45))}const texts=[...s.querySelectorAll('h1,small,strong,.cards span,.layer,.side strong,.side p,.filesystem,pre,.code small,.band,.strata p,.row label,.row b,.axis,.binary div,.binary-label')];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){let a=texts[i],b=texts[j];if(a.contains(b)||b.contains(a))continue;let x=a.getBoundingClientRect(),y=b.getBoundingClientRect();if(Math.min(x.right,y.right)-Math.max(x.left,y.left)>1&&Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>1)issues.push('overlap: '+a.textContent.slice(0,35)+' / '+b.textContent.slice(0,35))}return {issues,title:s.querySelector('h1').textContent,images:[...s.querySelectorAll('img')].every(i=>i.complete&&i.naturalWidth>0),ratio:r.width/r.height}}"""
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    page.on('pageerror',lambda e:results['errors'].append(str(e)))
    page.on('request',lambda r:results['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
    page.goto(html.as_uri());page.evaluate('document.fonts.ready');page.wait_for_timeout(600)
    assert page.locator('.slide').count()==40
    for name,w,h in [('desktop',1920,1080),('laptop',1280,720),('mobile',390,844)]:
        page.set_viewport_size({'width':w,'height':h}); entries=[]
        for i in range(40):
            page.evaluate('(i)=>deck.showSlide(i,false)',i);page.wait_for_timeout(30)
            result=page.evaluate(CHECK); result['slide']=i+1;entries.append(result)
            if name=='desktop':
                page.wait_for_timeout(510);page.screenshot(path=str(OUT/f'slide-{i+1:02}.png'))
        results['viewports'][name]=entries
        page.wait_for_timeout(550);page.screenshot(path=str(OUT/f'{name}-final.png'))
    page.set_viewport_size({'width':1920,'height':1080})
    for a,b in [(10,11),(12,13),(17,18),(29,30),(37,38)]:
        page.evaluate('(i)=>deck.showSlide(i,false)',a-1);page.wait_for_timeout(550)
        page.evaluate('(i)=>deck.showSlide(i)',b-1);page.wait_for_timeout(180)
        op=page.locator('.slide.active').evaluate('(e)=>getComputedStyle(e).opacity')
        page.screenshot(path=str(OUT/f'transition-{a:02}-{b:02}.png'))
        results.setdefault('transitions',[]).append({'from':a,'to':b,'active_opacity_at_capture':op})
        page.wait_for_timeout(550)
    page.keyboard.press('Home');page.wait_for_timeout(550);assert page.evaluate('deck.currentSlide')==0
    page.keyboard.press('ArrowRight');assert page.evaluate('deck.currentSlide')==1
    page.keyboard.press('ArrowLeft');assert page.evaluate('deck.currentSlide')==0
    page.keyboard.press('End');assert page.evaluate('deck.currentSlide')==39
    page.locator('#prev').click();assert page.evaluate('deck.currentSlide')==38
    results['navigation']['keyboard_and_buttons']='passed'
    page.evaluate("""() => {dispatchEvent(new TouchEvent('touchstart',{changedTouches:[new Touch({identifier:1,target:document.body,clientX:300,clientY:400})]}));dispatchEvent(new TouchEvent('touchend',{changedTouches:[new Touch({identifier:1,target:document.body,clientX:100,clientY:400})]}))}""")
    assert page.evaluate('deck.currentSlide')==39;results['navigation']['swipe']='passed'
    page.emulate_media(reduced_motion='reduce');page.evaluate('deck.showSlide(12)');page.wait_for_timeout(20)
    results['reduced_motion']=page.locator('.slide.active .visual').evaluate('(e)=>getComputedStyle(e).transitionDuration')
    page.screenshot(path=str(OUT/'reduced-motion.png'))
    page.wait_for_timeout(900);before=page.evaluate('deck.currentSlide');page.wait_for_timeout(1200);assert before==page.evaluate('deck.currentSlide');results['no_autoplay']=True
    for path in sorted((ROOT/'presentation/python-diagrams').glob('*.svg')):
        page.goto(path.as_uri());page.wait_for_timeout(20)
        issues=page.evaluate("""() => {let t=[...document.querySelectorAll('text')],out=[];for(let i=0;i<t.length;i++)for(let j=i+1;j<t.length;j++){let a=t[i].getBoundingClientRect(),b=t[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)out.push([t[i].textContent,t[j].textContent])}return out}""")
        results['diagrams'].append({'file':path.name,'text_overlaps':issues})
    browser.close()
results['passed']=not results['errors'] and not results['external_requests'] and all(not x['issues'] and x['images'] and abs(x['ratio']-16/9)<0.001 for arr in results['viewports'].values() for x in arr) and all(not d['text_overlaps'] for d in results['diagrams'])
(OUT/'validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps({'passed':results['passed'],'errors':results['errors'],'external_requests':len(results['external_requests']),'layout_issues':[(v,x['slide'],x['issues']) for v,a in results['viewports'].items() for x in a if x['issues']],'diagram_issues':[d for d in results['diagrams'] if d['text_overlaps']],'navigation':results['navigation'],'reduced_motion':results['reduced_motion']},ensure_ascii=False,indent=2))
assert results['passed']
