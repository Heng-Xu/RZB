from pathlib import Path
import json,hashlib
import pymupdf
from PIL import Image,ImageDraw
root=Path.cwd();r=root/'研究报告/05_review/当前版/1020矩阵窗口与有功限值修正';out=r/'版面';out.mkdir(exist_ok=True)
p=pymupdf.open('/tmp/matrix-correct-pass2.pdf');need=['候选指标的采样节点与点数','图5-11','3.5.2 情景采样','表3-14','折算后的有功上限','3.6.2 逐站能力','表5-63','表5-64','表5-65','表5-66','表5-67','表5-68','表5-69','基准宽度','1.96～2.03','表5-75','图5-17']
pages={1,2,3};items=[]
for page in p:
 t=page.get_text();hits=[s for s in need if s in t]
 if hits:pages.add(page.number+1);items.append({'页码':page.number+1,'内容':hits})
for n in sorted(pages):p[n-1].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(out/f'changed-{n:03}.png')
for start in range(0,len(pages),6):
 group=sorted(pages)[start:start+6];canvas=Image.new('RGB',(1320,990*((len(group)+2)//3)),(225,225,225))
 for i,n in enumerate(group):
  im=Image.open(out/f'changed-{n:03}.png').convert('RGB');im.thumbnail((420,945));tile=Image.new('RGB',(440,990),'white');tile.paste(im,((440-im.width)//2,30));ImageDraw.Draw(tile).text((10,8),f'PDF page {n}',fill='black');canvas.paste(tile,((i%3)*440,(i//3)*990))
 canvas.save(out/f'changed-contact-{start//6+1}.png')
(out/'改动页面索引.json').write_text(json.dumps({'页码':sorted(pages),'内容':items},ensure_ascii=False,indent=2)+'\n')
print('改动页',sorted(pages))
# 两次输入只变目录缓存，确认最终稿与实际WPS输入逐部件一致。
from zipfile import ZipFile
native=root/'研究报告/04_word/研究报告终稿.docx';input_path=Path('/tmp/matrix-correct-pass2.docx')
def parts(path):
 with ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}
a,b=parts(native),parts(input_path);diff=[n for n in set(a)|set(b) if a.get(n)!=b.get(n)]
print('最终Word与WPS输入部件差异',diff)
