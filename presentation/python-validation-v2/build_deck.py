"""Rebuild the offline 40-slide deck. Run from repository root."""
from pathlib import Path
import base64, html, json, re, subprocess, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'presentation'; DIAG=OUT/'python-diagrams'; DIAG.mkdir(exist_ok=True)
D2=Path.home()/'.local/bin/d2'
old=(OUT/'python-contest.html').read_text()
font=re.search(r'@font-face\{.*?\}',old).group()
base=(Path.home()/'.hermes/profiles/restored/skills/frontend-slides/viewport-base.css').read_text()
data=json.loads((ROOT/'measurement-data/github-41992840188/comparison/comparison.json').read_text())
rows={d['variant']:d for d in data}; order=['default','top1','top2','top-entry3']
labels=['Mặc định','TOP 1','TOP 2 · điều chỉnh','TOP · mục thứ ba']; colors=['#326878','#37775e','#bd583e','#8b7d64']
titles='Tối ưu Dockerfile|Từ CTF|Mở image|Bốn cách đóng|Xếp từng lớp|Nhìn hợp nhất|Thêm rồi xóa|Byte vẫn còn|Dọn cùng bước|Source đổi trước|Cache mất theo|Đổi thứ tự|Cache được giữ|Bỏ qua RUN|Tải lại ít|Mount bị vô hiệu|Builder cần gì|Chuyển artifact|Runtime giữ gì|Chọn base image|Kiểm tra tương thích|Tag có đổi|Digest giữ nội dung|Pin chưa hết|Strip bỏ gì|Dọn có giá|Chốt điều kiện|Ba lượt build|Bốn runner riêng|Gom bằng chứng|Kích thước image|Nhỏ chưa nhanh|Build có cache|Khi sửa source|Container đã lên|Request mới biết|FastAPI lệch phiên bản|Pin rồi thử|Đọc đúng số|Đo rồi chọn'.split('|')
assert len(titles)==40
manifest=[]
def graph(name,nodes,edges,focus=(),bad=()):
    src=['direction: right','vars: { d2-config: { sketch: false; theme-id: 0 } }','classes: { node: { width: 260; height: 100; style: { fill: "#eeebe3"; stroke: "#c9c9bf"; font-color: "#69716b"; font-size: 26; border-radius: 12; stroke-width: 2 } } }']
    for k,label in nodes:
        src += [f'{k}: "{label}" {{ class: node }}']
        if k in focus: src += [f'{k}.style: {{ fill: "#e4ece3"; stroke: "#37775e"; font-color: "#252827"; stroke-width: 4 }}']
        if k in bad: src += [f'{k}.style: {{ fill: "#f4e5da"; stroke: "#bd583e"; font-color: "#bd583e"; stroke-width: 4 }}']
    for a,b in edges: src += [f'{a} -> {b}: {{ style: {{ stroke: "#9b9f95"; stroke-width: 3 }} }}']
    p=DIAG/(name+'.d2'); p.write_text('\n'.join(src)+'\n')
    subprocess.run([str(D2),'--layout=dagre','--pad=35',str(p),str(p.with_suffix('.svg'))],check=True,capture_output=True)
    svg=p.with_suffix('.svg').read_bytes()
    manifest.append({'source':str(p.relative_to(ROOT)),'svg':str(p.with_suffix('.svg').relative_to(ROOT)),'sha256':hashlib.sha256(svg).hexdigest()})
    return '<img class="diagram" alt="'+html.escape(' → '.join(x[1] for x in nodes))+'" src="data:image/svg+xml;base64,'+base64.b64encode(svg).decode()+'">'
def statement(big,small=''):
    return f'<div class="statement"><p>{big}</p><span>{small}</span></div>'
def cards(items):
    return '<div class="cards">'+''.join(f'<article><small>{a}</small><strong>{b}</strong><span>{c}</span></article>' for a,b,c in items)+'</div>'
def chart(metric,limit,unit):
    vals=[rows[k]['image_bytes']/1048576 if metric=='size' else rows[k]['startup_seconds'] if metric=='startup' else rows[k]['builds'][metric]['seconds'] for k in order]
    return '<div class="chart"><div class="axis">0 <span>'+str(limit)+' '+unit+'</span></div>'+''.join(f'<div class="row"><label>{lab}</label><div class="track"><i style="width:{v/limit*100:.6f}%;background:{c}"></i></div><b>{v:.2f}' + (' MiB' if metric=='size' else ' s')+'</b></div>' if metric=='size' else f'<div class="row"><label>{lab}</label><div class="track"><i style="width:{v/limit*100:.6f}%;background:{c}"></i></div><b>{v:.3f} s</b></div>' for lab,v,c in zip(labels,vals,colors))+'</div>'
def layers(state):
    labels2=['FROM · Python','COPY · manifest','RUN · dependencies','COPY · source']
    blocks=''.join(f'<div class="layer l{i} {"focus" if (state==0 and i==3) else ""}" style="bottom:{i*112}px;left:{i*45}px;width:{850-i*45}px">{s}</div>' for i,s in enumerate(labels2))
    return '<div class="layer-scene"><div class="stack">'+blocks+'</div><div class="side"><strong>'+('Lớp mới' if state==0 else 'Một filesystem')+'</strong><p>'+('Không viết lại lớp cũ' if state==0 else 'Góc nhìn hợp nhất')+'</p><div class="filesystem">/app<br>/usr/local<br>/lib</div></div></div>'
def delete_scene(state):
    return '<div class="delete-scene"><div class="code"><small>'+('HAI BƯỚC' if state<2 else 'CÙNG MỘT BƯỚC')+'</small><pre>'+('RUN download archive\nRUN extract &amp;&amp; rm archive' if state<2 else 'RUN download archive \\\n &amp;&amp; extract \\\n &amp;&amp; rm archive')+'</pre></div><div class="strata"><div class="band">'+('Lớp 2 · dấu xóa' if state<2 else 'Lớp cuối · artifact')+'</div><div class="band '+('warn' if state==1 else '')+'">'+('Lớp 1 · archive vẫn còn' if state<2 else 'Không commit file tạm')+'</div><p>'+('File không còn hiện ra' if state==0 else 'Ẩn file ≠ thu hồi byte' if state==1 else 'Tạo → dùng → dọn')+'</p></div></div>'
slides=[]
def add(body,caption,section='CƠ CHẾ',note=''):
    i=len(slides)+1
    slides.append(f'<!-- === SLIDE {i:02}: {titles[i-1]} === --><section class="slide" aria-label="{titles[i-1]}" data-slide="{i}"><header><span class="eyebrow">PYTHON / {section}</span><span class="number">{i:02} / 40</span><h1>{titles[i-1]}</h1></header><div class="visual">{body}</div><footer><span>{caption}</span><span>DOCKERFILE / PYTHON</span></footer><!-- {html.escape(note)} --></section>')
add(statement('Nhỏ hơn.<br>Nhanh hơn.<br><em>Phải chạy đúng.</em>','Đóng gói → đo thật → kiểm chứng'),'Không chỉ nhìn số MiB','MỞ ĐẦU')
add(graph('02-ctf',[('a','Challenge local'),('b','Image'),('c','Giữ gì?')],[('a','b'),('b','c')],['b']),'Từ thói quen soi môi trường, đến cách đóng gói có chủ đích','BỐI CẢNH')
add(graph('03-image',[('a','Source'),('b','Runtime'),('c','Đồ nghề build'),('d','File dư?')],[('a','b'),('c','b'),('d','b')],['a','b']),'Sơ đồ minh họa · không kết luận image nào chứa bí mật')
add(cards([('Mặc định','Alpine + uv','COPY tất cả trước'),('TOP 1','Distroless','Venv + shared libs'),('TOP 2 · điều chỉnh','Alpine + pip','FastAPI 0.120.4'),('TOP · mục thứ ba','Debian slim','Wheels → runtime')]),'Cùng source; khác base và dependencies · không xác nhận hạng ba','BỐN RECIPE')
add(layers(0),'RUN / COPY tạo thay đổi filesystem; ENV / CMD là cấu hình')
add(layers(1),'Góc nhìn hợp nhất không cho biết byte nằm ở lớp nào')
add(delete_scene(0),'Ví dụ cơ chế · không phải số MiB đã đo riêng')
add(delete_scene(1),'Lớp trên che file; dữ liệu ở lớp dưới không biến mất')
add(delete_scene(2),'Nếu file đã COPY ở lớp trước, xóa sau không thu hồi byte')
cachebad=[('a','COPY source'),('b','RUN install'),('c','Image')]; es=[('a','b'),('b','c')]
add(graph('10-cache-input',cachebad,es,['a']),'Chỉ sửa source, nhưng source đứng trước bước cài thư viện')
add(graph('11-cache-miss',cachebad,es,[],['a','b','c']),'Đầu vào đổi → bước phụ thuộc phải xét lại cache')
cachegood=[('a','Manifest + lock'),('b','RUN install'),('c','COPY source'),('d','Image')]; eg=[('a','b'),('b','c'),('c','d')]
add(graph('12-cache-order',cachegood,eg,['a','b']),'Đưa phần ít đổi lên trước; source hay đổi xuống sau')
add(graph('13-cache-hit',cachegood,eg,['a','b'],['c','d']),'Sửa source không buộc cài lại dependency khi đầu vào bước install giữ nguyên')
cachetypes=[('a','Input không đổi'),('b','Layer cache'),('c','RUN được bỏ qua')]
add(graph('14-layer-cache',cachetypes,es,['b','c']),'Tái dùng kết quả của bước · không thực thi lại lệnh')
mount=[('a','RUN vẫn chạy'),('b','Cache tải / wheel'),('c','Dependency đã cài')]
add(graph('15-cache-mount',mount,es,['a','b']),'Cache mount tiết kiệm tải lại; không tự trở thành nội dung image')
add(graph('16-disabled-mount',[('a','Mount pip cache'),('b','--no-cache-dir'),('c','Không dùng cache pip')],es,[],['b','c']),'TOP 2: có mount chưa có nghĩa pip đang tận dụng nó')
arch=[('a','Compiler / headers'),('b','uv / pip + cache'),('c','Venv / wheels'),('d','Python + libs'),('e','Source + non-root')]; ea=[('a','c'),('b','c'),('c','d'),('d','e')]
add(graph('17-builder',arch,ea,['a','b']),'Builder có thể đầy đủ đồ nghề; runtime không cần nhận tất cả')
add(graph('18-artifact',arch,ea,['c','d']),'COPY --from chỉ chuyển những artifact được chỉ định')
add(graph('19-runtime',arch,ea,['d','e']),'Giữ đủ interpreter, shared libraries, package data và source')
add(cards([('ALPINE','musl','Có wheel phù hợp?'),('DEBIAN SLIM','glibc','Wheel manylinux'),('DISTROLESS','Runtime chọn lọc','Chuẩn bị cách debug')]),'Base nhỏ không tự làm dependency build nhanh')
add(graph('21-compatibility',[('a','Python / ABI'),('b','libc + shared libs'),('c','Import + request')],es,['a','b','c']),'Chuyển thiếu thư viện có thể chỉ lộ lỗi khi import hoặc gọi một nhánh chức năng')
pinning=[('a','python:3.13-slim'),('b','Thời điểm T1'),('c','Thời điểm T2'),('d','Nội dung A'),('e','Nội dung B')]; ep=[('a','b'),('a','c'),('b','d'),('c','e')]
add(graph('22-tag',pinning,ep,[],['d','e']),'Cùng tag có thể trỏ sang nội dung khác theo thời gian')
add(graph('23-digest',[('a','image@sha256:…'),('b','Thời điểm T1'),('c','Thời điểm T2'),('d','Cùng nội dung')],[('a','b'),('a','c'),('b','d'),('c','d')],['a','d']),'Digest cố định nội dung image được chọn, không khóa mọi đầu vào')
add(graph('24-pin-scope',[('a','Base digest'),('b','Dependency lock'),('c','Source + tooling'),('d','Cập nhật + test')],[('a','d'),('b','d'),('c','d')],['b','c','d']),'TOP 1 còn cài riêng Starlette sau frozen sync · pin phải đi cùng cập nhật')
add('<div class="binary"><div>.text / .rodata</div><div>Dynamic linking</div><div class="removed">Debug / symbol table</div></div><div class="binary-label">strip → bỏ có chọn lọc</div>','Tùy chế độ và loại binary · không xóa mọi symbol')
add(cards([('STRIP','Khó debug hơn','Test import + runtime'),('METADATA','Package discovery','Giữ thông tin cần thiết'),('LICENSE / STDLIB','Không xóa mù','Kiểm nghĩa vụ + đường chạy')]),'Chưa đo riêng lợi ích từng bước dọn · không suy ra ít CVE hơn')
add(cards([('SOURCE','35be046…','Cùng commit'),('BUILD','amd64','ubuntu-24.04'),('RUNTIME','1 CPU · 512 MiB','PORT=5000 · WORKERS=1')]),'So cả recipe · dependencies và bases khác nhau','THIẾT KẾ ĐO')
add(graph('28-build-sequence',[('a','Cold'),('b','Warm'),('c','Source comment')],es,['a','b','c']),'Builder mới --pull --no-cache → cùng builder → thêm comment · gồm export/load')
ci=[('a','Commit 35be046…'),('b','default'),('c','top1'),('d','top2 · điều chỉnh'),('e','TOP · mục thứ ba'),('f','Artifacts'),('g','comparison.json')]; ec=[('a',k) for k in 'bcde']+[(k,'f') for k in 'bcde']+[('f','g')]
add(graph('29-ci-runners',ci,ec,['b','c','d','e']),'Bốn runner riêng · không chia sẻ cache giữa recipes · một mẫu mỗi chế độ')
add(graph('30-ci-evidence',ci,ec,['f','g']),'Mỗi nhánh: cold → warm → source → runtime → artifact · đọc status bên trong JSON')
add(chart('size',240,'MiB'),'Docker inspect .Size · local chưa nén, không phải dung lượng tải registry','KẾT QUẢ')
add(chart('cold',40,'s'),'Cold: TOP 2 điều chỉnh nhỏ nhất nhưng không nhanh nhất · n=1 / recipe','KẾT QUẢ')
add(chart('warm',1,'s'),'Warm: đầu vào không đổi, cùng builder của recipe đó · có export/load','KẾT QUẢ')
add(chart('source-change',25,'s'),'Chỉ thêm comment Python · không đổi lockfile hay thêm dependency','KẾT QUẢ')
add(chart('startup',3.5,'s'),'Từ docker run đến khi health + homepage đạt · gồm nhịp polling, không phải request latency','RUNTIME')
add(graph('36-request-check',[('a','Container'),('b','/health/ JSON'),('c','Homepage'),('d','Coffee stub /hot')],[('a','b'),('a','c'),('c','d')],['b','c','d']),'Cả bốn PASS smoke · stub HTTP 200 + [] · chưa test live API hay toàn bộ chức năng')
add(graph('37-dependency-fail',[('a','FastAPI 0.162.0'),('b','instrumentator 7.1.0'),('c','Request 500')],es,[],['c']),'Run trước: _IncludedRouter không có path · server lên chưa đủ chứng minh request chạy đúng')
add(graph('38-dependency-pin',[('a','FastAPI 0.120.4'),('b','Starlette 0.49.3'),('c','Smoke PASS')],es,['a','b','c']),'TOP 2 đã điều chỉnh, không phải bản gốc · pin rồi kiểm thử, không hứa tương thích toàn bộ')
add(cards([('SỐ ĐO','1 mẫu / recipe','Runner và mạng còn nhiễu'),('PHẠM VI','Whole recipe','Không cô lập kỹ thuật'),('CHƯA ĐO','CVE / live / tải','Không suy từ size hay label')]),'Run 41992840188 · commit 35be0461710f… · log, inspect, packages đi cùng kết quả','BẰNG CHỨNG')
add(graph('40-decision',[('a','Soi image'),('b','Đổi có chủ đích'),('c','Test request'),('d','Đo rồi chọn')],[('a','b'),('b','c'),('c','d')],['d']),'Nhỏ hơn là một số đo. Tối ưu là một kết luận có điều kiện.','KẾT LUẬN')
assert len(slides)==40
css='''
/* === IVORY EDITORIAL === */
:root{--stage-bg:#e8e5dd;--slide-bg:#f8f6f1;--ink:#252827}*{box-sizing:border-box}body{font-family:Deck,sans-serif;color:var(--ink)}
.slide:before{content:'';position:absolute;inset:0 0 auto;height:10px;background:linear-gradient(90deg,#bd583e 12%,#e9e4d9 12%)}
header{position:absolute;top:60px;left:110px;right:110px}.eyebrow{font-size:21px;letter-spacing:2px;color:#69716b}.number{float:right;font-size:22px;color:#69716b}h1{font-size:84px;letter-spacing:-3px;line-height:1.2;margin:40px 0 0}header:after{content:'';position:absolute;top:197px;width:78px;height:5px;background:#bd583e}.visual{position:absolute;left:110px;top:310px;width:1700px;height:620px}.diagram{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}footer{position:absolute;bottom:46px;left:110px;right:110px;font-size:21px;color:#69716b;border-top:1px solid #dedcd6;padding-top:22px;display:flex;justify-content:space-between;gap:30px}footer span:first-child{max-width:1360px}footer span:last-child{white-space:nowrap}.statement p{font-size:88px;line-height:1.3;margin:0}.statement em{font-style:normal;color:#37775e}.statement span{display:block;font-size:30px;margin-top:32px;color:#69716b}.cards{display:flex;gap:30px;height:470px;margin-top:45px}.cards article{flex:1;border-top:5px solid #326878;background:#eeebe3;padding:36px 30px;min-width:0}.cards article:nth-child(2){border-color:#37775e}.cards article:nth-child(3){border-color:#bd583e}.cards article:nth-child(4){border-color:#8b7d64}.cards small{display:block;font-size:25px;color:#69716b;min-height:80px}.cards strong{display:block;font-size:39px;line-height:1.5;margin:24px 0}.cards span{display:block;font-size:26px;line-height:1.7}.layer-scene,.delete-scene{display:flex;gap:110px;padding-top:30px}.stack{position:relative;width:1000px;height:500px}.layer{position:absolute;height:95px;background:#e3eceb;border:2px solid #a1b7b4;padding:26px 34px;font-size:30px}.layer:nth-child(even){background:#e4ece3}.layer.focus{background:#f4e5da;border-color:#bd583e}.side{width:530px;padding-top:50px}.side strong{font-size:45px}.side p{font-size:30px;color:#69716b}.filesystem{border-left:5px solid #37775e;padding:24px;font-size:32px;line-height:1.8}.code{width:790px;padding:30px;background:#eeebe3;height:420px}.code small{font-size:24px;color:#bd583e}pre{font-size:28px;line-height:2.1;white-space:pre-wrap}.strata{width:800px;padding-top:20px}.band{padding:35px;background:#e4ece3;font-size:31px;margin-bottom:22px;border:2px solid #bbc6b7}.band.warn{background:#f4e5da;border-color:#bd583e}.strata p{font-size:36px;color:#bd583e}.binary{width:1350px;margin-top:50px;display:flex;border:3px solid #326878}.binary div{padding:70px 30px;font-size:33px;background:#e3eceb;flex:1}.binary div.removed{background:#f4e5da;text-decoration:line-through;color:#bd583e}.binary-label{font-size:42px;margin-top:60px;color:#37775e}.chart{margin-top:20px}.axis{margin-left:420px;width:1080px;font-size:23px;color:#69716b;border-bottom:2px solid #c9c9bf;padding-bottom:14px}.axis span{float:right}.row{display:flex;align-items:center;height:120px;gap:24px}.row label{width:396px;font-size:30px}.track{width:1080px;height:57px;flex-shrink:0;border-left:2px solid #c9c9bf}.track i{display:block;height:100%;min-width:2px;border-radius:0 8px 8px 0}.row b{font-size:29px;white-space:nowrap;min-width:170px}
/* === PRESENTER-PACED TRANSITIONS === */
.slide{transition:opacity 420ms ease,visibility 420ms;z-index:0}.slide.active{z-index:2}.slide .visual{transition:transform 500ms ease,opacity 420ms;transform:translateX(22px);opacity:0}.slide.active .visual{transform:translateX(0);opacity:1}.slide.leaving{visibility:visible;opacity:0;z-index:1}.slide.leaving .visual{transform:translateX(-22px)}.deck-controls{top:8px;bottom:auto;display:flex;align-items:center;gap:9px;background:#fffefb;border:1px solid #dedcd6;border-radius:8px;padding:4px 7px;font-size:13px}button{font:inherit;min-height:32px;padding:4px 13px;border:1px solid #dedcd6;border-radius:4px;color:#252827;background:#fffefb;cursor:pointer}button:disabled{opacity:.35}:focus-visible{outline:3px solid #326878;outline-offset:2px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}@media(prefers-reduced-motion:reduce){.slide,.slide .visual{transition:none!important;transform:none!important}}@media print{@page{size:1920px 1080px;margin:0}.slide .visual{opacity:1;transform:none}}
'''
js='''
/* === FIXED CANVAS / MANUAL NAVIGATION === */
class SlidePresentation{
constructor(){this.slides=[...document.querySelectorAll('.slide')];this.currentSlide=-1;this.stage=document.querySelector('.deck-stage');this.scale();addEventListener('resize',()=>this.scale());this.showSlide((Number(location.hash.slice(1))||1)-1,false)}
scale(){let s=Math.min(innerWidth/1920,innerHeight/1080);this.stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`}
showSlide(n,animate=true){n=Math.max(0,Math.min(n,39));if(n===this.currentSlide)return;let prev=this.slides[this.currentSlide];if(prev&&animate){prev.classList.add('leaving');setTimeout(()=>prev.classList.remove('leaving'),500)}this.currentSlide=n;this.slides.forEach((e,i)=>{e.classList.toggle('active',i===n);e.inert=i!==n;e.setAttribute('aria-hidden',String(i!==n))});history.replaceState(null,'','#'+(n+1));document.querySelector('#position').textContent=`${n+1} / 40`;document.querySelector('#prev').disabled=n===0;document.querySelector('#next').disabled=n===39;document.querySelector('#announce').textContent=this.slides[n].querySelector('h1').textContent}
}
window.deck=new SlidePresentation();document.querySelector('#prev').onclick=()=>deck.showSlide(deck.currentSlide-1);document.querySelector('#next').onclick=()=>deck.showSlide(deck.currentSlide+1);
addEventListener('keydown',e=>{if(e.target.matches('button')&&e.key===' ')return;let d={ArrowRight:1,ArrowDown:1,PageDown:1,' ':1,ArrowLeft:-1,ArrowUp:-1,PageUp:-1}[e.key];if(d){e.preventDefault();deck.showSlide(deck.currentSlide+d)}if(e.key==='Home')deck.showSlide(0);if(e.key==='End')deck.showSlide(39);if(e.key==='f'&&!document.fullscreenElement)document.documentElement.requestFullscreen?.()});
let touch;addEventListener('touchstart',e=>touch=[e.changedTouches[0].clientX,e.changedTouches[0].clientY],{passive:true});addEventListener('touchend',e=>{if(!touch)return;let dx=touch[0]-e.changedTouches[0].clientX,dy=touch[1]-e.changedTouches[0].clientY;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy))deck.showSlide(deck.currentSlide+(dx>0?1:-1));touch=null},{passive:true});let last=0;addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>25&&Date.now()-last>700){deck.showSlide(deck.currentSlide+(e.deltaY>0?1:-1));last=Date.now()}},{passive:true});addEventListener('hashchange',()=>deck.showSlide((Number(location.hash.slice(1))||1)-1));
'''
result='<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tối ưu Dockerfile · 40 bước</title><style>'+base+font+css+'</style></head><body><div class="deck-viewport"><main class="deck-stage">'+''.join(slides)+'</main></div><nav class="deck-controls" aria-label="Điều khiển slide"><button id="prev" aria-label="Slide trước">←</button><span id="position"></span><button id="next" aria-label="Slide sau">→</button></nav><span id="announce" class="sr-only" aria-live="polite"></span><script>'+js+'</script></body></html>'
(OUT/'python-contest-v2.html').write_text(result)
(DIAG/'manifest-v2.json').write_text(json.dumps({'d2_version':'v0.9.0','release':'https://github.com/d2lang/d2/releases/tag/v0.9.0','archive_sha256':'5669ddc46b99e942cc96078f4a4e36d5e62103348f4c05179ede27802fdd87a9','render_command':'d2 --layout=dagre --pad=35 INPUT.d2 OUTPUT.svg','diagrams':manifest},indent=2))
print(f'Built {len(slides)} slides; {len(manifest)} genuine D2 source/SVG pairs; {len(result)} HTML characters')
