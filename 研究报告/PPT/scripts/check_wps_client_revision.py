"""Read the actual WPS PDF, compare native text and render all pages for review."""
from pathlib import Path
from lxml import etree as E
from PIL import Image,ImageDraw,ImageFont
import pymupdf as fitz
import hashlib,json,re,shutil,sys

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_甲方修正版_20261022'
P=W/'previews/wps';P.mkdir(parents=True,exist_ok=True)
source=Path('/tmp/xuzhou-report-ppt-draft.pdf')
pptx=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_甲方修正版.pptx'
pptx_hash=hashlib.sha256(pptx.read_bytes()).hexdigest()
assert pptx_hash==hashlib.sha256(Path('/tmp/xuzhou-report-ppt-draft.pptx').read_bytes()).hexdigest()
assert source.stat().st_mtime>=Path('/tmp/xuzhou-report-ppt-draft.pptx').stat().st_mtime, 'PDF must be exported after opening the current PPTX copy'
dest=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_甲方修正版.pdf'
shutil.copy2(source,dest)
doc=fitz.open(dest);plan=json.loads((W/'content_map.json').read_text())['pages']
assert len(doc)==len(plan)==34
ns={'s':'http://www.w3.org/2000/svg'}
norm=lambda s:re.sub(r'\s+','',s)
findings=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);thumbs=[]
for i,(page,row) in enumerate(zip(doc,plan),1):
    root=E.parse(str(W/'authoring-svg-flat'/row['svg']))
    expected=[norm(''.join(t.itertext())) for t in root.findall('.//s:text',ns)]
    for marker in root.findall('.//s:g[@data-pptx-replace-with="table"]',ns):
        meta=marker.find('s:metadata',ns)
        if meta is not None:
            payload=json.loads(meta.text)
            def cell_text(c):
                if isinstance(c,str):return c
                if c.get('text')is not None:return str(c['text'])
                return ''.join(p if isinstance(p,str)else p.get('text','')or ''.join(r.get('text','')for r in p.get('runs',[]))for p in c.get('paragraphs',[]))
            grid=([payload['columns']]if payload.get('columns')else[])+payload.get('rows',[])
            expected.extend(norm(cell_text(c))for row in grid for c in row)
    actual=norm(page.get_text())
    missing=[s for s in expected if s and s not in actual]
    clipped=[]
    for block in page.get_text('dict')['blocks']:
        for ln in block.get('lines',[]):
            for sp in ln['spans']:
                box=fitz.Rect(sp['bbox'])
                if box.x0<-.5 or box.y0<-.5 or box.x1>page.rect.width+.5 or box.y1>page.rect.height+.5:clipped.append(sp['text'])
    findings.append({'page':i,'missing_native_text':missing,'outside_page_text':clipped,'fonts':[f[3] for f in page.get_fonts()]})
    png=P/f'page_{i:02d}.png';page.get_pixmap(matrix=fitz.Matrix(2,2)).save(png)
    im=Image.open(png).convert('RGB');im.thumbnail((480,360));canvas=Image.new('RGB',(500,390),'#E5EBE9');canvas.paste(im,(10,24));ImageDraw.Draw(canvas).text((10,4),str(i),font=font,fill='black');thumbs.append(canvas)
for start in range(0,len(thumbs),12):
    sheet=Image.new('RGB',(1500,1560),'white')
    for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%3)*500,(j//3)*390))
    sheet.save(P/f'总览_{start+1:02d}.jpg',quality=92)
report={'renderer':'WPS Office for Linux, isolated display :139','pptx_sha256':pptx_hash,'pdf':str(dest.relative_to(W)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pages':len(doc),'native_text_comparison':'SVG-authored native text versus WPS PDF extracted text; images checked visually','findings':findings,'visual_review':'pending'}
(W/'validation/wps_export_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'pages':len(doc),'missing_native_text':sum(len(r['missing_native_text']) for r in findings),'outside_page_text':sum(len(r['outside_page_text']) for r in findings),'issues':[r for r in findings if r['missing_native_text'] or r['outside_page_text']]},ensure_ascii=False))
