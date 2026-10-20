from pathlib import Path
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64,json,mimetypes,math
import cairosvg

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_20261019';P=W/'previews';P.mkdir(exist_ok=True)
plan=json.loads((W/'content_map.json').read_text())['pages'];thumbs=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
for row in plan:
    f=W/'authoring-svg-flat'/row['svg'];root=E.parse(str(f)).getroot()
    for el in root.iter():
        href=el.get('href')
        if href and not href.startswith(('#','data:')):
            p=(f.parent/href).resolve();mime=mimetypes.guess_type(p)[0] or 'image/png';data='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode();el.set('href',data);el.set('{http://www.w3.org/1999/xlink}href',data)
        if el.get('font-family') and '黑体' in el.get('font-family'):el.set('font-family','Microsoft YaHei')
    out=P/f"page_{row['page']:02d}.png";cairosvg.svg2png(bytestring=E.tostring(root),write_to=str(out),output_width=1440,output_height=1080,background_color='white')
    im=Image.open(out).convert('RGB');im.thumbnail((480,360));canvas=Image.new('RGB',(500,390),'#E5EBE9');canvas.paste(im,(10,24));ImageDraw.Draw(canvas).text((10,4),str(row['page']),font=font,fill='black');thumbs.append(canvas)
for start in range(0,len(thumbs),12):
    sheet=Image.new('RGB',(1500,1560),'white')
    for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%3)*500,(j//3)*390))
    sheet.save(P/f'总览_{start+1:02d}.jpg',quality=90)
html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>成果汇报初稿预览</title><style>body{background:#e6ecea;font:16px sans-serif;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:24px}img{width:100%;background:white}article{padding:12px;background:white}h2{font-size:18px}</style><h1>成果汇报初稿：25页主汇报＋11页备查</h1><p>当前为源页面预览，最终版面以WPS导出PDF为准。数值按报告来源快照生成。</p><main>'
for r in plan:html+=f'<article><h2>{r["page"]:02d} {r["title"]}</h2><a href="page_{r["page"]:02d}.png"><img src="page_{r["page"]:02d}.png"></a></article>'
(P/'index.html').write_text(html+'</main></html>')
print('Rendered',len(plan),'source previews')
