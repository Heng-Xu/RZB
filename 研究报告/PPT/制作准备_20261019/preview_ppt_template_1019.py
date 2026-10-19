from pathlib import Path
from PIL import Image,ImageDraw
import cairosvg
from lxml import etree as E
import base64,mimetypes
root=Path.cwd()/'研究报告/PPT/成果汇报_20261019'
out=Path.cwd()/'研究报告/PPT/制作准备_20261019'
can=Image.new('RGB',(1440,1120),'#E5E9EB')
for i,p in enumerate(sorted((root/'authoring-svg-flat').glob('slide_*.svg'))):
    dest=out/f'成果模板_第{i+1:02d}页.png'
    tree=E.parse(str(p))
    for el in tree.getroot().iter():
        if el.get('href'):
            resource=(p.parent/el.get('href')).resolve()
            target='data:'+str(mimetypes.guess_type(resource)[0] or 'image/png')+';base64,'+base64.b64encode(resource.read_bytes()).decode()
            el.set('href',target)
            el.set('{http://www.w3.org/1999/xlink}href',target)
        if el.get('font-family'):
            el.set('font-family','Noto Sans CJK SC')
    cairosvg.svg2png(bytestring=E.tostring(tree),write_to=str(dest),output_width=960,output_height=720,background_color='white')
    im=Image.open(dest).convert('RGB');im.thumbnail((700,525))
    x=(i%2)*720+10;y=(i//2)*560+25
    can.paste(im,(x,y));ImageDraw.Draw(can).text((x,y-18),str(i+1),fill='black')
can.save(out/'成果模板_缩略图.jpg',quality=92)
print('Source template previews saved')
