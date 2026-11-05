from pathlib import Path
import sys,json
sys.path.insert(0,'/home/taint73/.hermes/profiles/restored/cache/scratch/python-slide-tools')
from playwright.sync_api import sync_playwright
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
TITLES=['Tối ưu Dockerfile','Từ CTF','Bốn cách đóng','Image layers','Xóa chưa nhỏ','Cache đúng chỗ','Hai loại cache','Tách build runtime','Chọn base image','Pin đầu vào','Strip có giá','Đo công bằng','Build song song','Kích thước image','Build lạnh','Sửa source','Chạy mới tính','Bài học dependency','Đọc bằng chứng','Tối ưu có chứng']
report:dict={'bounds_issues':[],'overlap_issues':[],'screenshots':[],'viewports':[],'page_errors':[],'external_requests':[]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/taint73/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome',args=['--no-sandbox'])
 report['browser']=b.version
 page=b.new_page(viewport={'width':1280,'height':720},reduced_motion='reduce')
 page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
 page.on('request',lambda r:report['external_requests'].append(r.url) if r.url.startswith(('https:','http:')) else None)
 page.goto((ROOT/'python-contest.html').as_uri());page.evaluate('document.fonts.ready')
 titles=page.locator('.slide h1').all_text_contents();assert titles==TITLES
 report['slides']=len(titles);report['exact_titles']=True;report['title_words']=[len(t.split()) for t in titles]
 # Vietnamese title syllables are space-separated; exact supplied titles take precedence over the 2–3-word heuristic.
 report['longer_supplied_titles']=[t for t in titles if len(t.split())>3]
 assert page.evaluate("document.fonts.check('32px Deck')")
 report['embedded_font_loaded']=True
 for width,height in [(1280,720),(1920,1080),(390,844)]:
  page.set_viewport_size({'width':width,'height':height})
  for i in range(20):
   page.evaluate('(i)=>deck.showSlide(i)',i);page.wait_for_timeout(30)
   issues=page.evaluate('''()=>{let s=document.querySelector('.slide.active'),v=s.querySelector('svg.visual'),box=s.getBoundingClientRect();return [...s.querySelectorAll('h1,header,footer,svg text')].filter(e=>{let r=e.getBoundingClientRect();return r.left<box.left-.5||r.right>box.right+.5||r.top<box.top-.5||r.bottom>box.bottom+.5}).map(e=>e.textContent)}''')
   if issues:report['bounds_issues'].append({'viewport':[width,height],'slide':i+1,'text':issues})
   collisions=page.evaluate('''()=>{let texts=[...document.querySelectorAll('.active svg text')],out=[];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){let a=texts[i].getBoundingClientRect(),b=texts[j].getBoundingClientRect();if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)out.push([texts[i].textContent,texts[j].textContent])}return out}''')
   if collisions:report['overlap_issues'].append({'viewport':[width,height],'slide':i+1,'pairs':collisions})
   rect=page.locator('.deck-stage').bounding_box();assert abs(rect['width']/rect['height']-16/9)<.0001
   assert page.locator('.slide.active').count()==1
   if width==1280 or (width==390 and i in [0,13,16,17]) or (width==1920 and i in [0,13]):
    name=f'{width}x{height}-slide-{i+1:02}.png';page.screenshot(path=str(OUT/name));report['screenshots'].append(name)
  report['viewports'].append({'width':width,'height':height,'slides_checked':20,'uniform_ratio':True})
 page.keyboard.press('Home');assert page.evaluate('deck.currentSlide')==0
 page.keyboard.press('ArrowRight');assert page.evaluate('deck.currentSlide')==1
 page.keyboard.press('End');assert page.evaluate('deck.currentSlide')==19
 page.keyboard.press('ArrowRight');assert page.evaluate('deck.currentSlide')==19
 page.locator('#prev').click();assert page.evaluate('deck.currentSlide')==18
 page.evaluate("dispatchEvent(new TouchEvent('touchstart',{changedTouches:[new Touch({identifier:1,target:document.body,clientX:300})]}));dispatchEvent(new TouchEvent('touchend',{changedTouches:[new Touch({identifier:1,target:document.body,clientX:100})]}))")
 assert page.evaluate('deck.currentSlide')==19
 report['navigation']='PASS: keyboard, boundary clamping, button, swipe'
 report['images_decoded']=page.evaluate('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
 report['image_count']=page.locator('img').count()
 report['network_request_count']=len(report['external_requests'])
 b.close()
thumbs=[]
for i in range(20):
 im=Image.open(OUT/f'1280x720-slide-{i+1:02}.png').convert('RGB');im.thumbnail((384,216))
 tile=Image.new('RGB',(404,250),'#e8e5dd');tile.paste(im,(10,10));ImageDraw.Draw(tile).text((12,230),f'{i+1:02}',fill='#252827');thumbs.append(tile)
sheet=Image.new('RGB',(404*4,250*5),'#e8e5dd')
for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*404,(i//4)*250))
sheet.save(OUT/'contact-sheet.png')
report['contact_sheet']='contact-sheet.png'
report['passed']=not any(report[k] for k in ['bounds_issues','overlap_issues','page_errors','external_requests'])
(OUT/'validation-python.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
assert report['passed']
