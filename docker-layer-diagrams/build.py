from pathlib import Path
import html, re, json
R=Path(__file__).resolve().parent
INK='#142D43'; BLUE='#145EA8'; TEAL='#096B60'; RED='#A42D40'; MUTED='#455D70'
def text(x,y,s,size=25,color=INK,weight=400,mono=False):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"'+(' font-family="Consolas, monospace"' if mono else '')+'>'+html.escape(s)+'</text>'
def box(x,y,w,h,fill='#EAF2FA',stroke='#9BB4CA',dash=False):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="8 6"' if dash else '')+'/>'
def arrow(x,y,X,Y,color=BLUE):
 return f'<path d="M{x} {y} L{X} {Y}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#arrow)"/>'
def line(x,y,X,Y):return f'<path d="M{x} {y} L{X} {Y}" stroke="#CBD8E3" stroke-width="2"/>'
def note(s):return box(64,706,1472,96,'#F0F5F9','#D2DEE7')+text(88,745,s[0],25,INK,600)+text(88,780,s[1],23,MUTED)
def frame(i,title,desc,body,source):
 return (f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-labelledby="title{i} desc{i}"><title id="title{i}">{html.escape(title)}</title><desc id="desc{i}">{html.escape(desc)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="{BLUE}"/></marker></defs><g font-family="Segoe UI, Arial, sans-serif"><rect width="1600" height="900" fill="white"/>{text(64,92,title,46,INK,700)}{text(64,139,desc,25,MUTED)}{line(64,171,1536,171)}{body}{text(64,847,'Nguồn: '+source,19,MUTED)}{text(1458,847,f'{i} / 4',22,MUTED)}</g></svg>''').replace('id="arrow"',f'id="arrow{i}"').replace('url(#arrow)',f'url(#arrow{i})')
slides=[]
b=text(80,228,'Dockerfile minh họa',29,INK,700)+text(910,228,'Image: chồng các lớp chỉ đọc',29,INK,700)
b+=box(80,260,660,388,'#F5F8FB','#B3C6D5')
for y,s in [(320,'FROM alpine:3.21'),(390,'COPY app/ /app/'),(460,'RUN chmod +x /app/start.sh'),(530,'CMD ["/app/start.sh"]')]: b+=text(108,y,s,25,INK,400,True)
b+=text(108,600,'CMD: cấu hình chạy, không thêm lớp tệp',23,MUTED)
for y,label,sub in [(280,'Lớp mới: RUN','Đổi quyền /app/start.sh'),(390,'Lớp mới: COPY','Thêm nội dung /app/'),(500,'Các lớp từ base image','FROM tham chiếu image nền')]:
 b+=box(910,y,610,94)+text(936,y+37,label,28,BLUE,700)+text(936,y+72,sub,23)
b+=arrow(755,406,887,406)+text(775,382,'build',23,BLUE,600)
b+=text(930,634,'Đọc chồng từ dưới lên',24,MUTED)
b+=note(['RUN, COPY, ADD có thể tạo thay đổi hệ thống tệp.','Không phải mọi lệnh Dockerfile đều tạo filesystem layer; FROM dùng các lớp có sẵn.'])
slides.append(frame(1,'Dockerfile tạo nên image layers','Mô hình giản lược: các thay đổi hệ thống tệp được xếp thành lớp.',b,'docs.docker.com/engine/storage/drivers/'))
b=text(80,228,'Container dùng image',29,INK,700)+text(765,228,'Merged view: cây tệp nhìn thấy',29,INK,700)
b+=box(80,266,570,108,'#E0F3EF','#71A99E')+text(104,307,'Writable container layer',29,TEAL,700)+text(104,345,'Ghi mới / sửa / đánh dấu xóa',24)
for y,label in [(400,'Image layer: ứng dụng'),(490,'Image layers: nền')]: b+=box(80,y,570,72)+text(104,y+46,label+' · chỉ đọc',26,BLUE,600)
b+=arrow(668,416,741,416)+text(672,390,'Gộp',20,BLUE,600)
b+=box(765,267,390,296,'#F5F8FB','#B3C6D5')+text(790,315,'/app/start.sh',26,INK,400,True)+text(790,364,'/etc/config',26,INK,400,True)+text(790,413,'/tmp/session',26,TEAL,400,True)+text(790,510,'Gộp lớp ghi + lớp đọc',23,MUTED)
b+=box(1200,267,320,296,'#FFF3DC','#C9A464',True)+text(1224,315,'Volume',30,'#795016',700)+text(1224,362,'Dữ liệu riêng',24)+text(1224,403,'ngoài lớp ghi',24)+text(1224,510,'Gắn tại /data',24,'#795016')
b+=text(790,462,'/data (mount)',25,'#795016',400,True)+arrow(1155,455,1200,455)
b+=text(80,632,'Mỗi container có lớp ghi riêng; nhiều container có thể dùng chung image.',27,INK,600)
b+=note(['Xóa container → mất lớp ghi; volume không tự mất theo container.','Đường dẫn được gắn volume đọc/ghi vào volume, không vào writable layer của container.'])
slides.append(frame(2,'Image chỉ đọc, container có lớp ghi','Merged view là góc nhìn hợp nhất, không phải một bản sao đầy đủ của image.',b,'docs.docker.com/engine/storage/drivers/'))
b=''
for x,title in [(64,'1. Trước khi sửa'),(570,'2. Lần ghi đầu'),(1076,'3. Ghi tiếp')]:
 b+=text(x,235,title,30,INK,700)+text(x,288,'upperdir · lớp ghi',23,TEAL,600)+box(x,310,460,140,'#E0F3EF','#71A99E')+text(x,500,'lowerdir · image chỉ đọc',23,BLUE,600)+box(x,520,460,120)
b+=text(90,365,'Chưa có config.txt',26,MUTED)+text(90,564,'config.txt · bản gốc',25,BLUE,600)+text(90,606,'Đọc trực tiếp từ lớp dưới',23)
b+=text(596,359,'config.txt · bản sửa',25,TEAL,600)+text(596,409,'Sửa trên bản sao',23)+text(596,564,'config.txt · bản gốc',25,BLUE,600)+text(596,606,'Không thay đổi',23)
b+=arrow(1000,520,1000,450)+text(900,478,'copy-up',22,BLUE,600)
b+=text(1102,359,'config.txt · sửa tiếp',25,TEAL,600)+text(1102,409,'Ghi ngay ở upperdir',23)+text(1102,564,'config.txt · bản gốc',25,BLUE,600)+text(1102,606,'Vẫn không thay đổi',23)
b+=arrow(528,381,560,381)+arrow(1034,381,1066,381)
b+=note(['overlay2 copy-up toàn bộ tệp, dù chỉ sửa một phần nội dung.','Lần ghi sau dùng bản đã ở upperdir; merged view ưu tiên bản ở lớp trên.'])
slides.append(frame(3,'Copy-up: sao chép trước, rồi mới sửa','Ví dụ sửa nội dung một tệp đã tồn tại trong image với storage driver overlay2.',b,'docs.docker.com/engine/storage/drivers/overlayfs-driver/'))
b=text(64,230,'Xóa ở RUN sau',31,RED,700)+text(845,230,'Tạo và xóa trong cùng RUN',31,TEAL,700)+line(800,218,800,671)
b+=box(64,259,690,110,'#F5F8FB','#B3C6D5')+text(86,300,'RUN tạo /tmp/cache.bin',25,INK,400,True)+text(86,341,'RUN rm /tmp/cache.bin',25,INK,400,True)
b+=box(64,398,690,84,'#FBECEF','#CB8F99')+text(88,433,'Lớp sau: whiteout / dấu xóa',26,RED,700)+text(88,466,'Merged view không còn thấy tệp',23)
b+=box(64,511,690,84)+text(88,547,'Lớp trước: cache.bin vẫn còn',26,BLUE,700)+text(88,580,'Dữ liệu cũ vẫn chiếm dung lượng image',23)
b+=text(64,650,'Ẩn tệp ≠ thu hồi dữ liệu ở lớp dưới',27,RED,700)
b+=box(845,259,690,110,'#F5F8FB','#B3C6D5')+text(867,300,'RUN tạo /tmp/cache.bin &&',25,INK,400,True)+text(867,341,'    rm /tmp/cache.bin',25,INK,400,True)
b+=box(845,398,690,197,'#E0F3EF','#71A99E')+text(869,441,'Kết thúc RUN: tệp không còn',28,TEAL,700)+text(869,491,'Không lưu nội dung tệp tạm này',25)+text(869,529,'trong thay đổi cuối của lớp.',25)+text(869,572,'Điều kiện: tệp được tạo trong RUN này.',23,MUTED)
b+=text(845,650,'Dọn tệp tạm trước khi kết thúc RUN',27,TEAL,700)
b+=note(['Xóa tệp vốn có ở lớp dưới, dù trong cùng RUN, vẫn không xóa dữ liệu lớp dưới.','Whiteout chỉ che tệp; ví dụ là mã giả. Không tính kích thước nén hay cache build.'])
slides.append(frame(4,'Xóa ở lớp sau không làm lớp trước nhỏ lại','So sánh dữ liệu được giữ lại trong image, không chỉ cây tệp cuối cùng.',b,'Docker Docs · storage/drivers/ và storage/drivers/overlayfs-driver/'))
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#dfe8ef;color:#142d43;font-family:"Segoe UI",Arial,sans-serif}nav{padding:16px 24px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:#fff}nav strong{margin-right:auto}a,button{font:inherit;color:#145ea8;background:white;border:1px solid #9bb4ca;border-radius:5px;padding:8px 12px;text-decoration:none;cursor:pointer}a:hover,button:hover{background:#eaf2fa}:focus-visible{outline:3px solid #a42d40;outline-offset:4px}main{max-width:1648px;margin:auto;padding:24px}figure{margin:0 0 28px;background:white;scroll-margin-top:16px}svg{display:block;width:100%;height:auto;aspect-ratio:16/9}figcaption{padding:12px 20px;color:#455d70;font-size:14px}figcaption a{padding:0;border:0;text-decoration:underline}::selection{background:#145ea8;color:white}body.solo nav,body.solo figcaption{display:none}body.solo main{max-width:none;padding:0}body.solo figure{display:none;margin:0}body.solo figure.chosen{display:block}body.solo{background:white}@media(max-width:600px){main{padding:12px}.canvas{overflow-x:auto}.canvas svg{min-width:1000px}nav{padding:12px}nav strong{width:100%}figcaption{line-height:1.6}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{@page{size:16in 9in;margin:0}body{background:white}nav,figcaption{display:none}main{padding:0;max-width:none}figure{margin:0;break-after:page}.canvas svg{min-width:0;width:100%;height:100vh}body.solo figure{display:block}}'''
parts=[]
for i,s in enumerate(slides,1):
 (R/f'diagram-{i}.svg').write_text(s,encoding='utf-8')
 parts.append(f'<figure id="diagram-{i}"><div class="canvas">{s}</div><figcaption><a href="#diagram-{i}" data-show="{i}">Chỉ hiện hình {i}</a> · <a href="https://docs.docker.com/engine/storage/drivers/">Storage drivers</a> · <a href="https://docs.docker.com/engine/storage/drivers/overlayfs-driver/">OverlayFS driver</a></figcaption></figure>')
page='''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Docker layers — Bộ diagram tiếng Việt</title><style>'''+css+'''</style></head><body><nav aria-label="Điều hướng diagram"><strong>Docker layers · 4 hình 16:9</strong>'''+''.join(f'<a href="#diagram-{i}">Hình {i}</a>' for i in range(1,5))+'''<button id="all" type="button">Hiện tất cả</button><button id="print" type="button">In / lưu PDF</button></nav><main>'''+''.join(parts)+'''</main><script>function show(n){document.body.classList.add('solo');document.querySelectorAll('figure').forEach((f,i)=>f.classList.toggle('chosen',i===n-1));window.scrollTo(0,0)}document.querySelectorAll('[data-show]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();history.replaceState(null,'','#slide-'+a.dataset.show);show(Number(a.dataset.show))}));function all(){document.body.classList.remove('solo');history.replaceState(null,'',location.pathname)}document.getElementById('all').onclick=all;document.getElementById('print').onclick=()=>window.print();document.addEventListener('keydown',e=>{if(e.key==='Escape')all()});const m=location.hash.match(/^#slide-([1-4])$/);if(m)show(Number(m[1]));</script></body></html>'''
(R/'index.html').write_text(page,encoding='utf-8')
print('CREATED index.html + 4 SVG')
# Validate standalone XML and HTML inventory.
import xml.etree.ElementTree as ET
for i in range(1,5):
 root=ET.parse(R/f'diagram-{i}.svg').getroot(); assert root.attrib['viewBox']=='0 0 1600 900'
assert page.count('<svg ')==4
assert not re.search(r'(?:src=|@import|url\([\"\']?https?://)',page)
print('PASS: 4 SVG parse, 1600×900 viewBox, 4 inline SVG, no remote runtime assets')
