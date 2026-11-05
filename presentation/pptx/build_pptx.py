"""Build presentation/Dockerfile-Optimize.pptx from committed benchmark data.

Run from the repository root:
    uv run --no-project --with python-pptx --with pillow python presentation/pptx/build_pptx.py
"""
import json
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path(__file__).resolve().parent / 'assets'
OUT = ROOT / 'presentation' / 'Dockerfile-Optimize.pptx'
RUNS = ['42057474702', '42058703830', '42059152289']
MAIN = RUNS[0]

DATA = {r: json.loads((ROOT / f'measurement-data/github-{r}/comparison/comparison.json').read_text())['aggregate']
        for r in RUNS}
A = DATA[MAIN]
V = ['default', 'top1', 'top2']
NAME = {'default': 'Mặc định', 'top1': 'TOP 1', 'top2': 'TOP 2 · bài em'}

NAVY, INK, MUTED, BG, CARD, LINE = '0B1F3A', '1B2430', '5B6675', 'F6F7F9', 'FFFFFF', 'E3E7ED'
BLUE, RED, GREEN, AMBER = '2496ED', 'D64545', '2E9E6B', 'E3A008'
COLOR = {'default': '7C8BA1', 'top1': '2E9E6B', 'top2': 'F06A35'}
FONT, MONO = 'Segoe UI', 'Consolas'


def rgb(h):
    return RGBColor.from_string(h)


def layer_split(variant):
    """Split Trivy findings into OS-package vs Python-package counts."""
    report = json.loads((ROOT / f'measurement-data/github-{MAIN}/benchmark-{variant}-1/trivy.json').read_text())
    os_n = py_n = 0
    for target in report.get('Results') or []:
        n = len(target.get('Vulnerabilities') or [])
        if target.get('Class') == 'os-pkgs':
            os_n += n
        else:
            py_n += n
    total = sum(A[variant]['cves'].values())
    assert os_n + py_n == total, (variant, os_n, py_n, total)
    return os_n, py_n


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- primitives
def new_slide(bg=BG):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(bg)
    return s


def text(s, x, y, w, h, content, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, font=FONT,
         anchor=MSO_ANCHOR.TOP, spacing=1.1):
    """content: str, or list of paragraphs; a paragraph is str or list of (text, {opts}) runs."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
        setattr(tf, side, Inches(0.04))
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        runs = para if isinstance(para, list) else [(para, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get('font', font)
            f.size = Pt(o.get('size', size))
            f.bold = o.get('bold', bold)
            f.color.rgb = rgb(o.get('color', color))
    return tb


def box(s, x, y, w, h, fill=CARD, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.shadow.inherit = False
    sp.fill.solid()
    sp.fill.fore_color.rgb = rgb(fill)
    if line:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(1.25)
    else:
        sp.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = radius
    sp.text_frame.text = ''
    return sp


def label_in(sp, content, size=16, color=INK, bold=False, align=PP_ALIGN.CENTER, font=FONT):
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    lines = content if isinstance(content, list) else [content]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = line if isinstance(line, list) else [(line, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            r.font.name = o.get('font', font)
            r.font.size = Pt(o.get('size', size))
            r.font.bold = o.get('bold', bold)
            r.font.color.rgb = rgb(o.get('color', color))
    return sp


def card(s, x, y, w, h, title, body, accent=BLUE, title_size=20, body_size=15):
    g = s.shapes.add_group_shape()
    bg = box(g, x, y, w, h, CARD, LINE)
    bar = box(g, x, y, 0.09, h, accent, shape=MSO_SHAPE.RECTANGLE)
    text(g, x + 0.3, y + 0.22, w - 0.5, 0.6, title, size=title_size, bold=True)
    text(g, x + 0.3, y + 0.85, w - 0.5, h - 1.0, body, size=body_size, color=MUTED, spacing=1.2)
    return g


def code(s, x, y, w, h, lines, size=15):
    """lines: list of str or (str, color)."""
    g = s.shapes.add_group_shape()
    box(g, x, y, w, h, '111827', radius=0.04)
    for i, c in enumerate(('EF4444', 'F59E0B', '10B981')):
        dot = box(g, x + 0.2 + i * 0.22, y + 0.17, 0.13, 0.13, c, shape=MSO_SHAPE.OVAL)
    paras = []
    for ln in lines:
        t, col = (ln, 'E5E7EB') if isinstance(ln, str) else ln
        paras.append([(t, {'color': col})])
    text(g, x + 0.25, y + 0.45, w - 0.45, h - 0.55, paras, size=size, font=MONO, spacing=1.15)
    return g


def picture(s, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw['width'] = Inches(w)
    if h:
        kw['height'] = Inches(h)
    return s.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def logo(s, name, x, y, size=0.6):
    return picture(s, ASSETS / f'logo-{name}.png', x, y, w=size, h=size)


def arrow(s, x1, y1, x2, y2, color=MUTED, width=2.25):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(etree.SubElement(ln, qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return c


def header(s, tag, title, n):
    text(s, 0.6, 0.38, 9, 0.35, tag.upper(), size=13, color=BLUE, bold=True)
    text(s, 0.6, 0.68, 12.1, 0.9, title, size=32, bold=True)
    text(s, 12.0, 0.38, 0.75, 0.35, f'{n:02d}', size=13, color=MUTED, align=PP_ALIGN.RIGHT)


def footer(s, note):
    s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.6), Inches(6.95), Inches(12.73), Inches(6.95)).line.color.rgb = rgb(LINE)
    text(s, 0.6, 7.0, 12.1, 0.35, note, size=11, color=MUTED)


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body.strip()


# ---------------------------------------------------------------- animation
P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'


def fade_transition(s):
    tr = etree.SubElement(s._element, qn('p:transition'), {'spd': 'med'})
    etree.SubElement(tr, qn('p:fade'))
    return tr


def builds(s, shapes):
    """Fade each shape in on its own click, in order."""
    ids = iter(range(3, 10_000))
    pars = []
    for sh in shapes:
        spid = str(sh.shape_id)
        outer, mid, eff, setc, animc = (next(ids) for _ in range(5))
        pars.append(f'''
<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>
 <p:par><p:cTn id="{mid}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
  <p:par><p:cTn id="{eff}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect">
   <p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
    <p:set><p:cBhvr><p:cTn id="{setc}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
     <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>
     <p:to><p:strVal val="visible"/></p:to></p:set>
    <p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{animc}" dur="450"/>
     <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>
   </p:childTnLst></p:cTn></p:par>
 </p:childTnLst></p:cTn></p:par>
</p:childTnLst></p:cTn></p:par>''')
    xml = f'''<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{''.join(pars)}
</p:childTnLst></p:cTn>
<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'''
    s._element.append(etree.fromstring(xml))


# ---------------------------------------------------------------- charts
def bar_chart(s, x, y, w, h, categories, series, kind=XL_CHART_TYPE.BAR_CLUSTERED, fmt='0.0',
              point_colors=None, point_labels=None, legend=False, label_size=15, gap=55, label_pos=None):
    cd = CategoryChartData()
    cd.categories = categories
    for name, values, _ in series:
        cd.add_series(name, values)
    gf = s.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.font.name = FONT
    ch.font.size = Pt(14)
    ch.font.color.rgb = rgb(INK)
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(13)
    plot = ch.plots[0]
    plot.gap_width = gap
    if kind in (XL_CHART_TYPE.BAR_STACKED, XL_CHART_TYPE.COLUMN_STACKED):
        plot.overlap = 100
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = fmt
    dl.number_format_is_linked = False
    dl.font.size = Pt(label_size)
    dl.font.bold = True
    if label_pos:
        dl.position = label_pos
    for (name, values, color), ser in zip(series, plot.series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = rgb(color)
        if point_colors:
            for j, c in enumerate(point_colors):
                pt = ser.points[j]
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb = rgb(c)
        if point_labels:
            for j, lab in enumerate(point_labels):
                tf = ser.points[j].data_label.text_frame
                tf.text = lab
                for r in tf.paragraphs[0].runs:
                    r.font.size = Pt(label_size)
                    r.font.bold = True
                ser.points[j].data_label.position = label_pos or XL_LABEL_POSITION.OUTSIDE_END
    va = ch.value_axis
    va.has_major_gridlines = False
    va.visible = False
    ca = ch.category_axis
    ca.tick_labels.font.size = Pt(16)
    ca.format.line.color.rgb = rgb(LINE)
    if kind in (XL_CHART_TYPE.BAR_CLUSTERED, XL_CHART_TYPE.BAR_STACKED):
        ca.reverse_order = True
    return gf


def rng(st, d=2, unit=''):
    return f"{st['median']:.{d}f}{unit}  ({st['min']:.{d}f}–{st['max']:.{d}f})"


def table(s, x, y, w, h, rows, col_w=None, size=15, header_fill=NAVY, highlight_col=None):
    gf = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h))
    t = gf.table
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = rgb(header_fill if i == 0 else (CARD if i % 2 else 'EEF1F5'))
            tf = c.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT
            r.font.size = Pt(size)
            r.font.bold = i == 0 or (highlight_col is not None and j == highlight_col)
            r.font.color.rgb = rgb('FFFFFF' if i == 0 else INK)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    return gf


def divider(n, num, title, sub):
    s = new_slide(NAVY)
    text(s, 0.9, 2.1, 3, 1.4, num, size=96, bold=True, color=BLUE)
    text(s, 0.9, 3.55, 11, 1.0, title, size=40, bold=True, color='FFFFFF')
    text(s, 0.9, 4.45, 11, 0.8, sub, size=20, color='A9B6C8')
    logo(s, 'docker', 11.3, 5.5, 1.3)
    return s


# ================================================================ slides
slides = []
sz = {v: A[v]['image_mib']['median'] for v in V}
gz = {v: A[v]['gzip_mib']['median'] for v in V}

# 1 Title
s = new_slide(NAVY)
logo(s, 'docker', 0.9, 0.9, 1.1)
logo(s, 'python', 2.2, 0.95, 1.0)
text(s, 0.9, 2.45, 11.5, 1.3, 'Tối ưu Dockerfile', size=60, bold=True, color='FFFFFF')
text(s, 0.9, 3.65, 11.5, 0.8, [[('Nhỏ hơn · ', {}), ('Nhanh hơn · ', {}), ('Vẫn phải chạy đúng', {'color': BLUE, 'bold': True})]],
     size=28, color='D6DEE9')
text(s, 0.9, 5.3, 11, 0.9, ['Ngô Tấn Tài (newnol)', 'Dockerfile Contest 2025 · case study Python / FastAPI'],
     size=18, color='A9B6C8')
notes(s, '''
Chào các anh. Hôm nay em chia sẻ lại quá trình em tối ưu Dockerfile cho cuộc thi Dockerfile Contest 2025, phần Python/FastAPI.
Thông điệp chính: image nhỏ hơn mới là một con số; tối ưu thật sự là nhỏ hơn, build nhanh hơn, và ứng dụng vẫn chạy đúng – và em phải đo được cả ba.
Bài của em là TOP 2 phần Python. Em sẽ so nó với Dockerfile mặc định và bài TOP 1, đo lại hôm nay trên CI.''')
slides.append(s)

# 2 Agenda
s = new_slide()
header(s, 'Lộ trình · 25 phút', 'Hôm nay em kể theo 5 chặng', 2)
items = [('01', 'Từ CTF', 'Vì sao em soi bên trong image', '3′', BLUE),
         ('02', 'Cơ chế', 'Layer · cache · multi-stage · base', '11′', '6366F1'),
         ('03', 'Đo lường', '3 recipe × 5 runner trên CI', '2′', GREEN),
         ('04', 'Kết quả', 'Size · build · runtime · CVE', '5′', COLOR['top2']),
         ('05', 'Bài học', 'Đọc đúng số, chọn có điều kiện', '4′', AMBER)]
grp = []
for i, (num, t, sub, mins, col) in enumerate(items):
    x = 0.6 + i * 2.48
    g = s.shapes.add_group_shape()
    box(g, x, 2.0, 2.3, 3.9, CARD, LINE)
    box(g, x, 2.0, 2.3, 0.12, col, shape=MSO_SHAPE.RECTANGLE)
    text(g, x + 0.25, 2.35, 1.8, 0.9, num, size=44, bold=True, color=col)
    text(g, x + 0.25, 3.35, 1.9, 0.5, t, size=22, bold=True)
    text(g, x + 0.25, 3.95, 1.9, 1.2, sub, size=15, color=MUTED, spacing=1.2)
    text(g, x + 0.25, 5.2, 1.9, 0.5, mins, size=20, bold=True, color=col)
    grp.append(g)
builds(s, grp)
notes(s, '''
Bài nói gồm 5 phần: câu chuyện CTF khiến em quan tâm tới nội dung image; các cơ chế layer và cache; cách em thiết kế phép đo; kết quả; và những bài học, kể cả những chỗ bài của em làm chưa tốt.''')
slides.append(s)

# 3 CTF
s = new_slide()
header(s, '01 · Bối cảnh', 'Từ CTF: image không chỉ chứa app', 3)
c = code(s, 0.6, 1.75, 6.3, 4.6, [
    ('$ docker run -it challenge sh', '93C5FD'),
    ('/app # id', '93C5FD'), 'uid=0(root) gid=0(root)',
    ('/app # ls -a', '93C5FD'), '.  ..  .env  .git  app.py  logs/',
    ('/app # which curl wget gcc', '93C5FD'), '/usr/bin/curl', '/usr/bin/wget', '/usr/bin/gcc',
    ('# → quyền dư, file thừa, tool sẵn', 'FBBF24')], size=16)
risks = [('File thừa', '.env, .git, log, cache build – lộ dữ liệu nếu có bí mật', RED),
         ('Tool có sẵn', 'shell, curl, compiler – giúp thao tác sau khi xâm nhập', AMBER),
         ('Quyền dư', 'chạy root, port thừa – rủi ro tùy cấu hình runtime', '6366F1')]
cards = [card(s, 7.3, 1.75 + i * 1.62, 5.4, 1.5, t, b, col, 19, 13) for i, (t, b, col) in enumerate(risks)]
builds(s, cards)
footer(s, 'Ví dụ minh họa từ thói quen chơi CTF web · không phải nội dung của image nào trong bài so sánh')
notes(s, '''
Em chơi CTF mảng web. Mỗi challenge thường kèm Dockerfile để tự dựng lại môi trường, và việc đầu tiên em làm là vào container xem: đang chạy user gì, có file gì thừa, có sẵn công cụ gì.
Ba thứ hay gặp: file thừa như .env, .git; công cụ có sẵn như shell, curl, compiler; và quyền dư như chạy root.
Có những thứ này không có nghĩa là bị tấn công ngay, nhưng nó làm việc khai thác sau xâm nhập dễ hơn. Từ đó khi viết Dockerfile em luôn hỏi: runtime cần giữ gì, bỏ được gì, và bỏ xong làm sao biết là tốt hơn.''')
slides.append(s)

# 4 Three recipes
s = new_slide()
header(s, '01 · Ba recipe', 'Cùng một source, ba cách đóng gói', 4)
rec = [('default', 'Mặc định', 'docker-example.txt', ['alpinelinux', 'python'],
        ['Base uv:python3.13-alpine', 'COPY . . rồi uv sync', '1 stage · chạy root']),
       ('top1', 'TOP 1', 'Bài hạng nhất', ['debian', 'python'],
        ['Builder bookworm-slim + uv', 'Runtime distroless (không shell)', 'Bind lockfile · non-root']),
       ('top2', 'TOP 2 · bài em', 'pip --prefix + dọn mạnh', ['alpinelinux', 'python'],
        ['python:3.13-alpine @digest', 'Strip .so, xóa tests/docs', 'Pin fastapi==0.120.4 (1 dòng)'])]
grp = []
for i, (v, t, sub, logos_, pts) in enumerate(rec):
    x = 0.6 + i * 4.1
    g = s.shapes.add_group_shape()
    box(g, x, 1.75, 3.85, 4.75, CARD, COLOR[v] if v == 'top2' else LINE)
    box(g, x, 1.75, 3.85, 0.14, COLOR[v], shape=MSO_SHAPE.RECTANGLE)
    for k, lg in enumerate(logos_):
        logo(g, lg, x + 0.3 + k * 0.75, 2.15, 0.6)
    text(g, x + 0.3, 2.95, 3.4, 0.5, t, size=24, bold=True, color=COLOR[v] if v != 'default' else INK)
    text(g, x + 0.3, 3.5, 3.4, 0.4, sub, size=14, color=MUTED)
    text(g, x + 0.3, 4.1, 3.4, 2.2, [[('• ' + p, {})] for p in pts], size=16, spacing=1.45)
    grp.append(g)
builds(s, grp)
footer(s, 'Nguồn recipe: devops.vn/webinar/dockerfile-contest-2025 · TOP 2 sửa đúng 1 dòng để chạy được với FastAPI hiện tại')
notes(s, '''
Ba recipe cùng build một source FastAPI. Mặc định là file docker-example.txt của ban tổ chức: COPY toàn bộ rồi uv sync, một stage, chạy root.
TOP 1 build trên Debian slim rồi chép Python và venv sang distroless – runtime không có shell.
TOP 2 là bài của em: Alpine, cài bằng pip vào /install, strip file .so, xóa test và docs, chạy user 10001.
Lưu ý: bài em khi build lại hôm nay không chạy được vì pip kéo FastAPI mới nhất, nên em pin fastapi==0.120.4 – đúng một dòng. Em sẽ quay lại chuyện này ở cuối.''')
slides.append(s)

# 5 Divider
s = divider(5, '01', 'Cơ chế: layer & cache', 'Hiểu image được xếp thế nào trước khi cắt gọt')
notes(s, 'Trước khi nói số, em đi nhanh qua bốn cơ chế quyết định kích thước và tốc độ build.')
slides.append(s)

# 6 Layers
s = new_slide()
header(s, '02 · Layer', 'Image là các lớp xếp chồng', 6)
layers = [('FROM python:3.13-alpine', 'base · ~45 MiB', '7C8BA1'),
          ('COPY pyproject.toml uv.lock', 'manifest · vài KB', '6366F1'),
          ('RUN pip / uv install', 'dependencies · lớp lớn nhất', COLOR['top2']),
          ('COPY src/', 'source · đổi thường xuyên', GREEN)]
shapes_ = []
for i, (cmd, desc, col) in enumerate(layers):
    y = 5.35 - i * 1.05
    sp = box(s, 0.9, y, 6.4, 0.9, col, radius=0.12)
    label_in(sp, [[(cmd, {'font': MONO, 'bold': True, 'color': 'FFFFFF', 'size': 17})],
                  [(desc, {'color': 'F1F5F9', 'size': 13})]])
    shapes_.append(sp)
side = text(s, 7.9, 2.1, 4.8, 3.8, [
    [('RUN / COPY / ADD', {'bold': True, 'color': INK})], [('→ tạo layer mới (thay đổi filesystem)', {'color': MUTED})], '',
    [('ENV / CMD / EXPOSE', {'bold': True, 'color': INK})], [('→ chỉ là metadata', {'color': MUTED})], '',
    [('Layer cũ không bị sửa', {'bold': True, 'color': COLOR['top2']})],
    [('lớp trên chỉ "che" lớp dưới', {'color': MUTED})]], size=19, spacing=1.15)
builds(s, shapes_ + [side])
footer(s, 'Minh họa thứ tự lớp kiểu "manifest trước, source sau" · kích thước là ví dụ')
notes(s, '''
Mỗi lệnh RUN, COPY, ADD tạo một layer mới chứa phần filesystem thay đổi. ENV, CMD, EXPOSE chỉ là cấu hình.
Điểm quan trọng: layer đã tạo thì không bị sửa. Lớp phía trên chỉ che lớp phía dưới. Hai hệ quả: xóa file ở lớp sau không lấy lại dung lượng, và thứ tự lớp quyết định cache.''')
slides.append(s)

# 7 Delete later
s = new_slide()
header(s, '02 · Layer', 'Xóa ở bước sau ≠ image nhỏ đi', 7)
left = s.shapes.add_group_shape()
text(left, 0.6, 1.7, 5.8, 0.5, '✗  Hai lệnh RUN', size=20, bold=True, color=RED)
code(left, 0.6, 2.25, 5.8, 1.3, [('RUN wget app.tar.gz      # +50 MB', 'E5E7EB'), ('RUN tar xf … && rm app.tar.gz', 'E5E7EB')], 15)
l1 = box(left, 0.6, 3.8, 5.8, 0.75, 'FDE2E2', RED)
label_in(l1, 'Layer 1 · archive 50 MB vẫn nằm đây', 15, RED, True)
l2 = box(left, 0.6, 4.65, 5.8, 0.75, 'F1F5F9', LINE)
label_in(l2, 'Layer 2 · "whiteout" – chỉ ẩn file', 15, MUTED)
right = s.shapes.add_group_shape()
text(right, 6.9, 1.7, 5.8, 0.5, '✓  Cùng một lệnh RUN', size=20, bold=True, color=GREEN)
code(right, 6.9, 2.25, 5.8, 1.3, [('RUN wget app.tar.gz \\', 'E5E7EB'), ('  && tar xf … && rm app.tar.gz', 'E5E7EB')], 15)
r1 = box(right, 6.9, 3.8, 5.8, 1.6, 'DCF3E8', GREEN)
label_in(r1, ['Một layer · chỉ còn kết quả', [('file tạm không bao giờ được commit', {'size': 14, 'color': MUTED, 'bold': False})]], 16, GREEN, True)
big = text(s, 0.6, 5.7, 12.1, 0.8, [[('Bài em: ', {'bold': True}), ('bước dọn stdlib & pip nằm ở RUN riêng sau COPY → phần đó gần như không giảm size.', {'color': MUTED})]], size=18)
builds(s, [left, right, big])
footer(s, 'Ví dụ cơ chế · số 50 MB là minh họa, không phải số đo')
notes(s, '''
Nếu tải file ở một RUN rồi xóa ở RUN sau, file biến mất khỏi góc nhìn cuối cùng nhưng byte vẫn nằm ở layer trước. Muốn không tốn dung lượng thì tạo, dùng và dọn trong cùng một RUN.
Em tự nhận: trong bài của em, bước xóa stdlib và pip nằm ở RUN riêng sau khi base đã có các file đó, nên phần dọn ấy gần như không giảm kích thước. Phần thật sự có tác dụng là dọn trong stage builder trước khi COPY sang.''')
slides.append(s)

# 8 COPY order
s = new_slide()
header(s, '02 · Cache', 'Thứ tự COPY quyết định cache', 8)
g1 = s.shapes.add_group_shape()
text(g1, 0.6, 1.7, 5.8, 0.5, 'Mặc định', size=20, bold=True, color=COLOR['default'])
code(g1, 0.6, 2.2, 5.8, 2.0, ['COPY . .', ('RUN uv sync --frozen   ← chạy lại', 'FCA5A5'), 'CMD ["python", "app.py"]'], 16)
text(g1, 0.6, 4.35, 5.8, 0.9, 'Sửa 1 dòng code → hash đầu vào đổi → cài lại toàn bộ dependency', size=16, color=MUTED)
g2 = s.shapes.add_group_shape()
text(g2, 6.9, 1.7, 5.8, 0.5, 'Manifest trước, source sau', size=20, bold=True, color=GREEN)
code(g2, 6.9, 2.2, 5.8, 2.0, ['COPY pyproject.toml uv.lock ./', ('RUN uv sync --frozen   ← CACHED', '86EFAC'), 'COPY src/ ./src/'], 16)
text(g2, 6.9, 4.35, 5.8, 0.9, 'Dependency không đổi → bước cài được bỏ qua hoàn toàn', size=16, color=MUTED)
sc = A
big = text(s, 0.6, 5.35, 12.1, 1.2, [[(f"{sc['default']['source_change_s']['median']:.2f} s", {'color': COLOR['default'], 'bold': True, 'size': 40}),
                                       ('   →   ', {'color': MUTED, 'size': 32}),
                                       (f"{sc['top1']['source_change_s']['median'] + 1e-9:.2f} s", {'color': GREEN, 'bold': True, 'size': 40}),
                                       ('   build lại khi chỉ sửa source (median 5 runner)', {'color': MUTED, 'size': 18})]])
builds(s, [g1, g2, big])
footer(s, f'Run {MAIN} · Mặc định vs TOP 1 · chế độ source-change = thêm 1 dòng comment Python')
notes(s, f'''
Docker cache theo đầu vào của từng bước. Recipe mặc định COPY toàn bộ source trước khi uv sync, nên chỉ cần sửa một dòng code là bước cài dependency chạy lại.
Đưa file khai báo dependency và lockfile lên trước, cài xong rồi mới COPY source, thì sửa code không đụng tới bước cài.
Số đo thật: mặc định mất khoảng {sc['default']['source_change_s']['median']:.1f} giây, TOP 1 dưới nửa giây, bài em khoảng {sc['top2']['source_change_s']['median']:.2f} giây.''')
slides.append(s)

# 9 Cache mount
s = new_slide()
header(s, '02 · Cache', 'Có cache mount chưa chắc đã dùng được', 9)
c1 = card(s, 0.6, 1.75, 3.9, 2.0, 'Layer cache', 'Đầu vào không đổi → bỏ qua cả lệnh RUN, dùng lại kết quả.', BLUE, 20, 15)
c2 = card(s, 0.6, 3.95, 3.9, 2.0, 'Cache mount', 'Giữ file đã tải (pip/apk) cho lần RUN sau · không nằm trong image.', '6366F1', 20, 15)
cd_ = code(s, 4.9, 1.75, 7.8, 3.2, [
    ('# trích bài của em (TOP 2)', '9CA3AF'),
    'ENV PIP_NO_CACHE_DIR=1',
    'RUN --mount=type=cache,target=/root/.cache/pip \\',
    '    python -m pip install --no-cache-dir \\',
    '        --prefix=/install  …'], 16)
warn = box(s, 4.9, 5.15, 7.8, 0.85, 'FFF4E5', AMBER)
label_in(warn, [[('Mount có, nhưng PIP_NO_CACHE_DIR + --no-cache-dir tắt cache pip → mount không có tác dụng', {'bold': True})]], 15, '8A5A00')
builds(s, [c1, c2, cd_, warn])
footer(s, 'benchmarks/dockerfiles/top2.Dockerfile · tương tự: apk add --no-cache cùng cache mount /var/cache/apk')
notes(s, '''
Có hai loại cache dễ nhầm. Layer cache là khi đầu vào không đổi, Docker bỏ qua cả lệnh. Cache mount là thư mục được giữ giữa các lần build để pip hay apk không phải tải lại; nó không nằm trong image.
Đây là lỗi của chính em: em khai báo cache mount cho pip, nhưng đồng thời đặt PIP_NO_CACHE_DIR và --no-cache-dir. Như vậy pip không ghi vào cache, mount có cũng như không. Nhìn Dockerfile có chữ mount chưa có nghĩa là đang được tận dụng.''')
slides.append(s)

# 10 Multi-stage
s = new_slide()
header(s, '02 · Multi-stage', 'Builder đủ đồ nghề, runtime chỉ nhận artifact', 10)
b = box(s, 0.6, 1.9, 4.2, 3.9, 'EEF2FF', '6366F1')
label_in(b, [[('Stage builder', {'bold': True, 'size': 22, 'color': '4338CA'})], '',
             [('build-base · gcc · cargo', {'font': MONO})], [('pip install --prefix=/install', {'font': MONO})],
             [('strip .so · xóa tests/docs', {'font': MONO})]], 15, INK)
a1 = arrow(s, 4.95, 3.85, 6.0, 3.85, '6366F1', 3)
mid = box(s, 6.1, 3.2, 1.9, 1.3, 'FFFFFF', LINE)
label_in(mid, [[('COPY --from', {'font': MONO, 'bold': True})], [('/install', {'font': MONO, 'size': 13, 'color': MUTED})]], 15)
a2 = arrow(s, 8.1, 3.85, 9.1, 3.85, GREEN, 3)
r = box(s, 9.2, 1.9, 3.55, 3.9, 'DCF3E8', GREEN)
label_in(r, [[('Runtime', {'bold': True, 'size': 22, 'color': '166534'})], '',
             [('python + site-packages', {'font': MONO})], [('src/', {'font': MONO})], [('user 10001', {'font': MONO})]], 15, INK)
note_ = text(s, 0.6, 6.0, 12.1, 0.6, 'Compiler và cache build ở lại builder · runtime vẫn phải đủ interpreter, shared library, package data', size=16, color=MUTED)
builds(s, [b, a1, mid, a2, r, note_])
footer(s, 'Sơ đồ theo bài TOP 2 · TOP 1 làm tương tự nhưng runtime là distroless')
notes(s, '''
Multi-stage tách nơi build và nơi chạy. Stage builder có thể cài đủ gcc, cargo, header; xong chỉ COPY --from đúng thư mục kết quả sang runtime.
Nhưng cẩn thận: runtime vẫn cần đủ interpreter, shared library và package data. Thiếu một file .so có thể chỉ lộ ra khi import hoặc khi gọi đúng nhánh code đó – nên phải test bằng request thật chứ không chỉ xem container có lên không.''')
slides.append(s)

# 11 Base image
s = new_slide()
header(s, '02 · Base image', 'Chọn base: nhỏ chưa chắc nhanh', 11)
bases = [('alpinelinux', 'Alpine', 'musl libc', ['Base rất nhỏ', 'Có thể phải build wheel từ source', 'Có shell + apk để debug'], '0D597F'),
         ('debian', 'Debian slim', 'glibc', ['Dùng wheel manylinux có sẵn', 'Build thường nhanh hơn', 'Base lớn hơn Alpine'], 'A81D33'),
         ('docker', 'Distroless', 'runtime chọn lọc', ['Không shell, không package manager', 'Bề mặt tấn công nhỏ', 'Debug khó hơn'], BLUE)]
grp = []
for i, (lg, t, sub, pts, col) in enumerate(bases):
    x = 0.6 + i * 4.1
    g = s.shapes.add_group_shape()
    box(g, x, 1.75, 3.85, 4.6, CARD, LINE)
    logo(g, lg, x + 0.3, 2.05, 0.75)
    text(g, x + 1.25, 2.05, 2.5, 0.5, t, size=24, bold=True, color=col)
    text(g, x + 1.25, 2.55, 2.5, 0.4, sub, size=14, color=MUTED)
    text(g, x + 0.3, 3.3, 3.35, 2.8, [[('• ' + p, {})] for p in pts], size=16, spacing=1.5)
    grp.append(g)
builds(s, grp)
footer(s, 'Bài em (Alpine) cần build-base + cargo trong builder → cold build lâu nhất trong 3 recipe (slide 18)')
notes(s, '''
Alpine dùng musl nên nhiều package không có wheel dựng sẵn, có thể phải build từ source – đó là lý do bài em cần build-base và cargo trong builder. Debian slim dùng glibc, tận dụng wheel manylinux. Distroless bỏ hết shell và package manager: bề mặt tấn công nhỏ nhưng debug khó.
Base nhỏ không tự làm build nhanh – lát nữa số cold build sẽ cho thấy điều đó.''')
slides.append(s)

# 12 Tag vs digest
s = new_slide()
header(s, '02 · Pin version', 'Tag có thể đổi · digest thì không', 12)
t1 = box(s, 0.6, 1.9, 5.8, 1.5, 'F1F5F9', LINE)
label_in(t1, [[('python:3.13-alpine', {'font': MONO, 'bold': True, 'size': 20})], [('hôm nay trỏ image A, tháng sau trỏ image B', {'color': MUTED})]], 15)
t2 = box(s, 6.9, 1.9, 5.8, 1.5, 'DCF3E8', GREEN)
label_in(t2, [[('python:3.13-alpine@sha256:e5fa…', {'font': MONO, 'bold': True, 'size': 18})], [('luôn đúng nội dung đã chọn', {'color': MUTED})]], 15)
warn = box(s, 0.6, 3.75, 12.1, 1.15, 'FFF4E5', AMBER)
label_in(warn, [[('Nhưng digest cũng "già" đi: ', {'bold': True}), ('không ai cập nhật thì lỗ hổng mới cứ tích lại (slide 22)', {})]], 18, '8A5A00')
ren = s.shapes.add_group_shape()
logo(ren, 'renovate', 0.6, 5.2, 0.9)
text(ren, 1.7, 5.2, 11, 1.0, [[('Pin + cập nhật tự động: ', {'bold': True}), ('Renovate mở PR khi có digest/version mới → CI build, test, scan lại', {'color': MUTED})]], size=18)
builds(s, [t1, t2, warn, ren])
footer(s, 'Repo này đã bật Renovate (PR #1–#3) · TOP 1 còn cài riêng starlette sau frozen sync → pin chưa phủ hết')
notes(s, '''
Tag là con trỏ có thể dịch chuyển; cùng tag python:3.13-alpine có thể ra image khác nhau theo thời gian. Digest sha256 cố định đúng nội dung.
Nhưng pin xong mà không cập nhật thì image cứ già đi. Cách em làm bây giờ là pin cộng Renovate: có digest mới thì bot mở PR, CI build và scan lại, mình review rồi merge.''')
slides.append(s)

# 13 Divider
s = divider(13, '02', 'Đo thế nào cho công bằng', 'Cùng source · cùng máy · lặp nhiều lần')
notes(s, 'Phần tiếp theo: em đo ba recipe như thế nào để so sánh được.')
slides.append(s)

# 14 Measurement design
s = new_slide()
header(s, '03 · Thiết kế đo', '3 recipe × 5 runner song song trên CI', 14)
pic = picture(s, ASSETS / 'ci-run.png', 0.6, 2.0, w=7.45)
chips = [('Cùng commit', '9b49c07 · cùng source'), ('Máy', 'linux/amd64 · ubuntu-24.04'),
         ('Giới hạn', '1 CPU · 512 MiB'), ('Lặp lại', '5 runner/recipe · median'),
         ('Mỗi job', 'build ×3 → chạy → Trivy')]
grp = []
for i, (k, v) in enumerate(chips):
    g = s.shapes.add_group_shape()
    box(g, 8.3, 1.7 + i * 0.98, 4.43, 0.85, CARD, LINE)
    text(g, 8.5, 1.76 + i * 0.98, 4.1, 0.35, k.upper(), size=11, bold=True, color=BLUE)
    text(g, 8.5, 2.06 + i * 0.98, 4.1, 0.45, v, size=15, bold=True)
    grp.append(g)
builds(s, grp)
footer(s, f'github.com/newnol/DockerFile-Contest/actions/runs/{MAIN} · thêm 2 lượt chạy lại: {RUNS[1]}, {RUNS[2]}')
notes(s, f'''
Em viết một workflow chạy 15 job song song: 3 recipe nhân 5 runner độc lập, cùng commit, cùng loại máy amd64, container giới hạn 1 CPU và 512 MiB.
Mỗi job đo cold build với builder mới và --no-cache, build lại khi không đổi gì, build lại khi chỉ thêm một dòng comment, rồi chạy container, kiểm tra request và quét Trivy.
Vì runner trên cloud có nhiễu nên em báo median kèm min–max, và chạy lại thêm hai lượt nữa để kiểm tra độ ổn định.''')
slides.append(s)

# 15 Smoke test
s = new_slide()
header(s, '03 · Kiểm chứng', '"Chạy đúng" nghĩa là request trả đúng', 15)
pic = picture(s, ASSETS / 'app-home.png', 0.6, 1.7, w=7.4)
chk = code(s, 8.3, 1.7, 4.43, 2.6, [('GET /health/', '93C5FD'), '{"heartbeat": "HEALTHY"}', '',
                                     ('GET /', '93C5FD'), '… "Dockerfile Contest 2025"'], 14)
res = box(s, 8.3, 4.5, 4.43, 1.4, 'DCF3E8', GREEN)
label_in(res, [[('15 / 15 PASS', {'bold': True, 'size': 28, 'color': '166534'})], [('cả 3 recipe × 5 runner', {'color': MUTED})]], 15)
builds(s, [chk, res])
footer(s, 'Coffee API trỏ tới stub nội bộ (HTTP 200, []) · đây là smoke test đóng gói, không phải test chức năng hay tải')
notes(s, '''
Container lên chưa đủ. Em coi một lần chạy là đạt khi /health/ trả heartbeat HEALTHY và trang chủ render đúng chuỗi "Dockerfile Contest 2025".
Coffee API bên ngoài được thay bằng stub nội bộ để kết quả không phụ thuộc mạng. Cả 15 lần chạy đều đạt. Đây là smoke test cho việc đóng gói, chưa phải test toàn bộ chức năng hay test tải.''')
slides.append(s)

# 16 Divider
s = divider(16, '03', 'Kết quả', f'Run {MAIN} · median của 5 runner')
notes(s, 'Giờ tới phần số liệu.')
slides.append(s)

# 17 Size
s = new_slide()
header(s, '04 · Kích thước', f"Bài em nhỏ nhất: {sz['top2']:.1f} MiB (−{100 * (1 - sz['top2'] / sz['default']):.0f}%)", 17)
ch = bar_chart(s, 0.6, 1.7, 8.3, 5.0, [NAME[v] for v in V],
               [('Chưa nén (docker inspect)', [sz[v] for v in V], '334155'), ('Nén gzip ≈ dung lượng tải', [gz[v] for v in V], '94A3B8')],
               fmt='0.0" MiB"', legend=True, gap=45)
for j, v in enumerate(V):
    pt = ch.chart.plots[0].series[0].points[j]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = rgb(COLOR[v])
side = text(s, 9.2, 2.0, 3.6, 4.3, [
    [('Chưa nén', {'bold': True})], [(f"{sz['default']:.1f} → {sz['top1']:.1f} → {sz['top2']:.1f} MiB", {'color': MUTED})], '',
    [('Khi tải (gzip)', {'bold': True})], [(f"{gz['default']:.1f} → {gz['top1']:.1f} → {gz['top2']:.1f} MiB", {'color': MUTED})], '',
    [('5/5 lần build ra cùng kích thước', {'color': GREEN, 'bold': True})]], size=17, spacing=1.2)
builds(s, [ch, side])
footer(s, 'docker inspect .Size (chưa nén) · gzip của docker save ≈ dung lượng kéo về registry · median 5 runner')
notes(s, f'''
Kích thước chưa nén: mặc định {sz['default']:.1f} MiB, TOP 1 {sz['top1']:.1f}, bài em {sz['top2']:.1f} MiB – nhỏ hơn mặc định khoảng {100 * (1 - sz['top2'] / sz['default']):.0f}%.
Cột nhạt là dung lượng nén, gần với lượng phải kéo về khi pull: {gz['default']:.1f}, {gz['top1']:.1f} và {gz['top2']:.1f} MiB.
Con số 105 MB em ghi lúc nộp bài là đo trên Mac arm64 bằng docker images, nên không so trực tiếp được với số hôm nay.''')
slides.append(s)

# 18 Cold build
s = new_slide()
header(s, '04 · Build lần đầu', 'Nhỏ nhất ≠ build nhanh nhất', 18)
cold = {v: A[v]['cold_s'] for v in V}
ch = bar_chart(s, 0.6, 1.8, 8.6, 4.6, [NAME[v] for v in V], [('Cold build', [cold[v]['median'] for v in V], INK)],
               point_colors=[COLOR[v] for v in V], point_labels=[rng(cold[v], 1, ' s') for v in V], gap=45)
side = card(s, 9.5, 2.0, 3.25, 3.9, 'Vì sao chậm?',
            'Alpine + musl → cài build-base, cargo; compile/strip trong builder.\n\nĐánh đổi: build lâu hơn để runtime nhỏ hơn.', COLOR['top2'], 18, 14)
builds(s, [ch, side])
footer(s, 'Cold = builder mới, --pull --no-cache, gồm export/load · median (min–max) 5 runner · 3 lượt chạy giữ nguyên thứ tự')
notes(s, f'''
Build lần đầu không có cache: TOP 1 nhanh nhất khoảng {cold['top1']['median']:.1f} giây, mặc định {cold['default']['median']:.1f}, bài em chậm nhất, khoảng {cold['top2']['median']:.1f} giây – gần gấp đôi mặc định.
Lý do là bài em cài build-base, cargo rồi strip trong builder. Đó là đánh đổi: tốn thời gian build để runtime nhỏ hơn. Thứ tự này giữ nguyên qua cả ba lượt chạy.''')
slides.append(s)

# 19 Rebuild
s = new_slide()
header(s, '04 · Build lại', 'Sửa 1 dòng code: thứ tự layer thắng', 19)
warm = {v: A[v]['warm_s']['median'] for v in V}
src = {v: A[v]['source_change_s']['median'] for v in V}
ch = bar_chart(s, 0.6, 1.8, 8.6, 4.7, [NAME[v] for v in V],
               [('Không đổi gì (warm)', [warm[v] for v in V], 'CBD5E1'), ('Thêm 1 dòng comment', [src[v] for v in V], INK)],
               fmt='0.00" s"', legend=True, gap=45)
for j, v in enumerate(V):
    pt = ch.chart.plots[0].series[1].points[j]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = rgb(COLOR[v])
big = s.shapes.add_group_shape()
box(big, 9.5, 2.0, 3.25, 3.9, CARD, LINE)
text(big, 9.7, 2.25, 2.9, 0.9, f"{src['default'] / src['top1']:.0f}×", size=60, bold=True, color=COLOR['top1'])
text(big, 9.7, 3.4, 2.9, 2.3, f"Mặc định chậm hơn TOP 1 khi chỉ sửa source, vì COPY . . đứng trước uv sync", size=15, color=MUTED, spacing=1.2)
builds(s, [ch, big])
footer(s, 'Warm = build lại, đầu vào không đổi · source-change = append 1 dòng comment vào app.py · median 5 runner')
notes(s, f'''
Đây là cơ chế cache ở slide 8 thể hiện thành số. Khi không đổi gì, cả ba đều dưới một giây.
Khi chỉ thêm một dòng comment: mặc định mất {src['default']:.1f} giây vì cài lại toàn bộ dependency; TOP 1 {src['top1']:.2f} giây, bài em {src['top2']:.2f} giây. Chênh khoảng {src['default'] / src['top1']:.0f} lần.
Với dev hằng ngày, đây là con số ảnh hưởng nhiều nhất, hơn cả kích thước image.''')
slides.append(s)

# 20 Runtime
s = new_slide()
header(s, '04 · Runtime', 'RAM rõ ràng · startup không xếp hạng', 20)
ram = {v: A[v]['idle_mem_mib'] for v in V}
ch = bar_chart(s, 0.6, 1.8, 6.0, 4.4, [NAME[v] for v in V], [('RAM rỗi', [ram[v]['median'] for v in V], INK)],
               point_colors=[COLOR[v] for v in V], point_labels=[f"{ram[v]['median']:.1f} MiB" for v in V], gap=45)
text(s, 0.6, 6.25, 6.0, 0.5, 'docker stats 5 s sau khi lên · 1 worker, chưa có tải', size=13, color=MUTED)
rows = [['Startup (median, s)'] + [f'Lượt {i + 1}' for i in range(len(RUNS))]]
for v in V:
    rows.append([NAME[v]] + [f"{DATA[r][v]['startup_s']['median']:.2f}" for r in RUNS])
tb = table(s, 7.0, 1.9, 5.73, 2.4, rows, col_w=[2.13, 1.2, 1.2, 1.2], size=15)
warn = box(s, 7.0, 4.6, 5.73, 1.55, 'FFF4E5', AMBER)
label_in(warn, [[('Thứ tự đổi giữa 3 lượt', {'bold': True})], [('polling 0.5 s · chênh < 0.5 s là nhiễu', {})]], 16, '8A5A00')
builds(s, [ch, tb, warn])
footer(s, f'Runs {", ".join(RUNS)} · thời gian dừng ≈ 0.35 s cho cả 3 recipe')
notes(s, f'''
RAM khi rỗi: bài em thấp nhất khoảng {ram['top2']['median']:.0f} MiB, hai recipe kia khoảng {ram['default']['median']:.0f} MiB; con số này ổn định qua các lượt.
Startup thì em không xếp hạng: lượt đầu bài em chậm nhất, lượt ba lại nhanh nhất. Script kiểm tra mỗi nửa giây nên chênh dưới nửa giây là nhiễu đo. Dừng container cả ba đều khoảng 0,35 giây.''')
slides.append(s)

# 21 CVE
s = new_slide()
header(s, '04 · Bảo mật', 'Trivy hôm nay: không recipe nào "0 CVE"', 21)
split = {v: layer_split(v) for v in V}
ch = bar_chart(s, 0.6, 1.8, 8.6, 4.7, [NAME[v] for v in V],
               [('Package hệ điều hành', [split[v][0] for v in V], '64748B'), ('Package Python', [split[v][1] for v in V], BLUE)],
               kind=XL_CHART_TYPE.BAR_STACKED, fmt='0;;;', legend=True, gap=45, label_pos=XL_LABEL_POSITION.CENTER)
for ser in ch.chart.plots[0].series:
    ser.data_labels.show_value = True
    ser.data_labels.number_format = '0;;;'
    ser.data_labels.number_format_is_linked = False
    ser.data_labels.position = XL_LABEL_POSITION.CENTER
    ser.data_labels.font.color.rgb = rgb('FFFFFF')
    ser.data_labels.font.size = Pt(15)
    ser.data_labels.font.bold = True
rows = [['', 'Critical', 'High']] + [[NAME[v], A[v]['cves']['CRITICAL'], A[v]['cves']['HIGH']] for v in V]
tb = table(s, 9.5, 1.9, 3.25, 2.0, rows, col_w=[1.35, 1.0, 0.9], size=12)
tl = s.shapes.add_group_shape()
logo(tl, 'trivy', 9.5, 4.3, 0.7)
text(tl, 10.35, 4.25, 2.4, 1.9, f'Bài em: {split["top2"][1]} ở Python, {split["top2"][0]} ở Alpine 3.22.2 (openssl, musl, zlib…)', size=14, color=MUTED, spacing=1.2)
builds(s, [ch, tb, tl])
footer(s, 'Trivy 0.76.2 · 05/11/2026 · 1 lần quét / recipe · số lượng phát hiện ≠ mức độ rủi ro thực tế')
notes(s, f'''
Em quét cả ba image bằng Trivy hôm nay. Không recipe nào còn 0 CVE.
Mặc định: toàn bộ {split['default'][1]} phát hiện nằm ở package Python từ uv.lock cũ. TOP 1: {split['top1'][0]} ở Debian và {split['top1'][1]} ở Python.
Bài em thì ngược lại: phần Python chỉ còn {split['top2'][1]} – việc nâng aiohttp, starlette lúc thi vẫn có tác dụng – nhưng {split['top2'][0]} phát hiện nằm ở package Alpine. Lưu ý đây là số đếm, chưa phải đánh giá khả năng khai thác.''')
slides.append(s)

# 22 CVE timeline lesson
s = new_slide()
header(s, '05 · Bài học', '"0 CVE" là ảnh chụp của một ngày', 22)
line = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(2.0), Inches(3.4), Inches(11.3), Inches(3.4))
line.line.color.rgb = rgb(LINE)
line.line.width = Pt(4)
pts = [(2.0, '11/2025', 'Nộp bài', '0 CVE · Trivy · Mac arm64', GREEN),
       (6.65, 'Một năm', 'Digest không đổi', 'Alpine 3.22.2 đứng yên, không rebuild', AMBER),
       (11.3, '11/2026', 'Quét lại', f'{sum(A["top2"]["cves"].values())} phát hiện · {split["top2"][0]} ở OS', RED)]
grp = []
for x, d, t, sub, col in pts:
    g = s.shapes.add_group_shape()
    box(g, x - 0.2, 3.2, 0.4, 0.4, col, shape=MSO_SHAPE.OVAL)
    text(g, x - 1.1, 2.3, 2.6, 0.5, d, size=20, bold=True, color=col, align=PP_ALIGN.CENTER)
    text(g, x - 1.2, 3.85, 2.8, 0.5, t, size=18, bold=True, align=PP_ALIGN.CENTER)
    text(g, x - 1.3, 4.35, 3.0, 0.9, sub, size=14, color=MUTED, align=PP_ALIGN.CENTER)
    grp.append(g)
fix = box(s, 0.6, 5.45, 12.1, 1.15, 'EAF4FE', BLUE)
label_in(fix, [[('Bài học: ', {'bold': True}), ('pin digest để tái lập + Renovate/CI rebuild định kỳ + scan trên pipeline, không scan một lần lúc nộp', {})]], 17, INK)
builds(s, grp + [fix])
footer(s, 'security-scan.sh cũ chấm "100/100" theo thang tự đặt · label security.scan="trivy-passed" được ghi cứng, không phải bằng chứng')
notes(s, '''
Lúc nộp bài em quét được 0 CVE. Một năm sau, cùng digest đó, số phát hiện tăng lên hơn trăm – không phải vì Dockerfile tệ đi mà vì thế giới tìm ra lỗ hổng mới trong openssl, musl, zlib.
Bài học: pin digest để tái lập, nhưng phải có Renovate hoặc CI rebuild định kỳ và scan trên pipeline. Em cũng rút kinh nghiệm là không ghi cứng label "trivy-passed" vào image.''')
slides.append(s)

# 23 FastAPI drift
s = new_slide()
header(s, '05 · Bài học', 'Container lên ≠ request chạy đúng', 23)
tb_ = code(s, 0.6, 1.7, 7.6, 3.9, [
    ('$ curl localhost:5000/', '93C5FD'), ('{"detail": "Internal Server Error"}', 'FCA5A5'), '',
    ('prometheus_fastapi_instrumentator/routing.py', '9CA3AF'), '    route_name = route.path',
    ("AttributeError: '_IncludedRouter' object", 'FCA5A5'), ("  has no attribute 'path'", 'FCA5A5')], 15)
steps = [('Nguyên nhân', 'fastapi>=0.116.0 không cận trên → kéo bản 0.162', RED),
         ('Sửa', 'Pin fastapi==0.120.4 (1 dòng) → 15/15 PASS', GREEN),
         ('Bài học', 'Range mở: mỗi lần build một khác → lock + test request', BLUE)]
cards = [card(s, 8.5, 1.7 + i * 1.65, 4.23, 1.5, t, b, col, 17, 14) for i, (t, b, col) in enumerate(steps)]
builds(s, [tb_] + cards)
footer(s, 'Tái hiện lại bằng chính source repo này với FastAPI 0.162 · lỗi gốc ở run 41990729849')
notes(s, '''
Đây là lỗi em gặp khi build lại bài của mình. Container vẫn lên, port vẫn mở, nhưng mọi request trả 500: thư viện Prometheus không hiểu kiểu router mới của FastAPI 0.162.
Nguyên nhân là em ghi fastapi>=0.116.0 không có cận trên. Sửa bằng cách pin fastapi==0.120.4, chạy lại thì 15 trên 15 đều đạt.
Bài học: range mở nghĩa là mỗi lần build có thể ra bộ thư viện khác, và chỉ kiểm tra container có lên là không đủ.''')
slides.append(s)

# 24 Read numbers right
s = new_slide()
header(s, '05 · Bài học', 'Đọc đúng số trước khi kết luận', 24)
cs = [('Số đo', '5 mẫu / recipe, 3 lượt chạy', 'Báo median (min–max). Runner cloud vẫn nhiễu: cold build TOP 1 dao động 8–11 s.', BLUE),
      ('Phạm vi', 'So nguyên recipe', 'Base, dependency, thứ tự lệnh đều khác nhau → không tách được từng kỹ thuật đóng góp bao nhiêu.', '6366F1'),
      ('Chưa đo', 'Live API · tải · pull time', 'Smoke test dùng stub. CVE là số đếm, không phải mức rủi ro khai thác.', AMBER)]
grp = []
for i, (k, t, b, col) in enumerate(cs):
    x = 0.6 + i * 4.1
    g = s.shapes.add_group_shape()
    box(g, x, 1.8, 3.85, 4.5, CARD, LINE)
    box(g, x, 1.8, 3.85, 0.12, col, shape=MSO_SHAPE.RECTANGLE)
    text(g, x + 0.3, 2.15, 3.3, 0.4, k.upper(), size=13, bold=True, color=col)
    text(g, x + 0.3, 2.6, 3.3, 1.0, t, size=22, bold=True, spacing=1.05)
    text(g, x + 0.3, 3.8, 3.3, 2.3, b, size=15, color=MUTED, spacing=1.25)
    grp.append(g)
builds(s, grp)
footer(s, 'Toàn bộ log, inspect, packages, trivy.json: measurement-data/github-<run-id>/ trong repo')
notes(s, '''
Trước khi kết luận, em muốn nói rõ giới hạn. Mỗi recipe có 5 mẫu, chạy 3 lượt; vẫn có nhiễu. Em so nguyên cả recipe nên không nói được riêng kỹ thuật nào đóng góp bao nhiêu. Và em chưa đo API thật, tải, hay thời gian pull thực tế.
Mọi log và dữ liệu thô đều nằm trong repo để các anh kiểm tra lại.''')
slides.append(s)

# 25 Conclusion
s = new_slide(NAVY)
text(s, 0.6, 0.5, 12, 0.5, 'KẾT LUẬN', size=14, bold=True, color=BLUE)
text(s, 0.6, 0.85, 12, 0.9, 'Nhỏ hơn là một số đo. Tối ưu là một kết luận có điều kiện.', size=30, bold=True, color='FFFFFF')
tk = [(f"-{100 * (1 - sz['top2'] / sz['default']):.0f}%", 'kích thước', 'Multi-stage + dọn trong builder có tác dụng thật', COLOR['top2']),
      (f"{src['default'] / src['top1']:.0f}×", 'build lại nhanh hơn', 'Thứ tự layer quan trọng hơn chọn base', COLOR['top1']),
      (f"{split['top2'][0]}", 'CVE ở base cũ', 'Pin phải đi cùng cập nhật & scan định kỳ', RED)]
grp = []
for i, (num, unit, msg, col) in enumerate(tk):
    x = 0.6 + i * 4.1
    g = s.shapes.add_group_shape()
    box(g, x, 2.2, 3.85, 4.0, '13294B')
    text(g, x + 0.35, 2.45, 3.3, 1.3, num, size=60, bold=True, color=col)
    text(g, x + 0.35, 3.85, 3.3, 0.5, unit, size=18, bold=True, color='FFFFFF')
    text(g, x + 0.35, 4.5, 3.2, 1.5, msg, size=16, color='A9B6C8', spacing=1.2)
    grp.append(g)
builds(s, grp)
notes(s, '''
Ba điều em rút ra. Một: multi-stage và dọn trong builder thực sự làm image nhỏ đi, bài em nhỏ hơn mặc định khoảng hai phần ba. Hai: thứ tự layer ảnh hưởng tới tốc độ làm việc hằng ngày nhiều hơn chọn base. Ba: pin phiên bản mà không có quy trình cập nhật thì image già đi rất nhanh.
Nên em không nói recipe nào "tốt nhất"; tốt hay không phụ thuộc mình ưu tiên size, tốc độ build hay khả năng bảo trì.''')
slides.append(s)

# 26 Thanks
s = new_slide(NAVY)
logo(s, 'docker', 5.9, 1.2, 1.5)
text(s, 0.6, 3.0, 12.1, 1.0, 'Cảm ơn các anh · Q&A', size=44, bold=True, color='FFFFFF', align=PP_ALIGN.CENTER)
text(s, 0.6, 4.1, 12.1, 1.2, ['github.com/newnol/DockerFile-Contest', 'benchmarks/ · measurement-data/ · presentation/'],
     size=18, color='A9B6C8', align=PP_ALIGN.CENTER, font=MONO)
notes(s, '''
Câu hỏi có thể gặp:
- Vì sao 5 lần? Runner cloud nhiễu; 5 mẫu đủ thấy dao động, đủ rẻ để chạy song song trong ~2 phút.
- Vì sao bài em phải sửa? FastAPI 0.162 làm hỏng instrumentator; pin 0.120.4 là 1 dòng, bản gốc lỗi ở run 41990729849.
- Lúc nộp 0 CVE sao giờ nhiều thế? Cùng digest nhưng một năm có thêm lỗ hổng mới ở openssl/musl/zlib của Alpine 3.22.2.
- gzip có bằng dung lượng pull không? Gần đúng; registry nén từng layer bằng gzip.
- Sao không tách từng kỹ thuật? Cần thí nghiệm đổi đúng một biến mỗi lần – là bước tiếp theo.''')
slides.append(s)

for s in slides:
    fade_transition(s)
    # p:transition must precede p:timing in the slide XML
    el = s._element
    tr, tm = el.find(qn('p:transition')), el.find(qn('p:timing'))
    if tm is not None and el.index(tm) < el.index(tr):
        el.remove(tr)
        el.insert(el.index(tm), tr)

prs.save(OUT)
print(f'wrote {OUT.relative_to(ROOT)} · {len(slides)} slides')
