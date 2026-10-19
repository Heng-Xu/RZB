from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, re
import fitz

ROOT=Path.cwd()
OUT=ROOT/'研究报告/PPT/制作准备_20261019'
OUT.mkdir(parents=True,exist_ok=True)
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
refs=ROOT/'研究报告/PPT/模版和范本'
manifest=[]
for f in sorted(refs.iterdir()):
    manifest.append({'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
    if f.suffix=='.pptx':
        with ZipFile(f) as z:
            pr=E.fromstring(z.read('ppt/presentation.xml'))
            size=pr.find('p:sldSz',NS)
            names=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda x:int(re.search(r'slide(\d+)',x).group(1)))
            pages=[]
            for i,n in enumerate(names,1):
                el=E.fromstring(z.read(n)); texts=el.xpath('//a:t/text()',namespaces=NS)
                imgs=el.xpath('//p:pic',namespaces=NS)
                fonts=el.xpath('//a:latin/@typeface|//a:ea/@typeface',namespaces=NS)
                colors=el.xpath('//a:srgbClr/@val',namespaces=NS)
                pages.append({'page':i,'text':texts,'pictures':len(imgs),'shapes':len(el.xpath('//p:sp',namespaces=NS)),'fonts':sorted(set(fonts)),'colors':sorted(set(colors))})
            info={'file':f.name,'pages':len(pages),'size_emu':dict(size.attrib),'slides':pages}
            (OUT/(f.stem+'_提取.json')).write_text(json.dumps(info,ensure_ascii=False,indent=2))
            (OUT/(f.stem+'_逐页文字.md')).write_text('\n\n'.join(f"## 第 {p['page']} 页\n"+'\n'.join(p['text']) for p in pages))
            print(json.dumps({'file':f.name,'pages':len(pages),'size':dict(size.attrib),'titles':[p['text'][:3] for p in pages]},ensure_ascii=False))
    elif f.suffix=='.pdf':
        doc=fitz.open(f)
        (OUT/(f.stem+'_逐页文字.md')).write_text('\n\n'.join(f'## 第 {i+1} 页\n'+p.get_text() for i,p in enumerate(doc)))
        thumbs=[]
        for i,p in enumerate(doc):
            pix=p.get_pixmap(matrix=fitz.Matrix(.38,.38),alpha=False)
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((440,280))
            canvas=Image.new('RGB',(460,310),'#e5e9eb');canvas.paste(im,((460-im.width)//2,22));ImageDraw.Draw(canvas).text((10,4),str(i+1),fill='black')
            thumbs.append(canvas)
        for start in range(0,len(thumbs),12):
            sheet=Image.new('RGB',(460*3,310*4),'white')
            for j,im in enumerate(thumbs[start:start+12]):sheet.paste(im,((j%3)*460,(j//3)*310))
            sheet.save(OUT/f'对标PDF_缩略图_{start+1:02d}.jpg',quality=90)
        for i in [2,5,10,15,20]:
            if i<len(doc):doc[i].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(str(OUT/f'对标PDF_第{i+1:02d}页.png'))
        print(json.dumps({'file':f.name,'pages':len(doc),'page_size':list(doc[0].rect),'text_chars':[len(p.get_text()) for p in doc]},ensure_ascii=False))

f=ROOT/'研究报告/04_word/研究报告终稿.docx'
manifest.append({'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
with ZipFile(f) as z:
    doc=E.fromstring(z.read('word/document.xml'));body=doc.find('w:body',NS)
    lines=[];tables=[];images=[]
    rel=E.fromstring(z.read('word/_rels/document.xml.rels'));rels={x.get('Id'):x.get('Target') for x in rel}
    last=''
    for n,el in enumerate(body):
        if el.tag==f"{{{NS['w']}}}p":
            text=''.join(el.xpath('.//w:t/text()',namespaces=NS));
            if text.strip():lines.append(f'P{n:04d} '+text);last=text
            for rid in el.xpath('.//a:blip/@r:embed',namespaces=NS):
                images.append({'body_index':n,'preceding':last,'target':rels.get(rid),'id':rid})
        elif el.tag==f"{{{NS['w']}}}tbl":
            rows=[[''.join(c.xpath('.//w:t/text()',namespaces=NS)) for c in r.findall('w:tc',NS)] for r in el.findall('w:tr',NS)]
            tables.append({'body_index':n,'preceding':last,'rows':rows});lines.append(f'TABLE {len(tables)} '+json.dumps(rows,ensure_ascii=False))
    (OUT/'研究报告终稿_全文与表格.txt').write_text('\n'.join(lines))
    (OUT/'研究报告终稿_表格.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    (OUT/'研究报告终稿_表图索引.md').write_text('\n'.join(f"{i+1:03d} | P{x['body_index']:04d} | {x['preceding']} | {len(x['rows'])}行" for i,x in enumerate(tables))+'\n\n'+'\n'.join(f"P{x['body_index']:04d} | {x['target']} | {x['preceding']}" for x in images))
    (OUT/'研究报告终稿_图片位置.json').write_text(json.dumps(images,ensure_ascii=False,indent=2))
    print(json.dumps({'report_paragraphs':len(lines)-len(tables),'tables':len(tables),'images':len(images),'headings':[x for x in lines if re.search(r'^P\d+ (第[一二三四五六]章|[1-6]\.\d+ )',x)]},ensure_ascii=False))
(OUT/'输入文件哈希.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
