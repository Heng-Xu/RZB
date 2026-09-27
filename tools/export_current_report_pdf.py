from pathlib import Path
import os,sys,subprocess,time,json
import uno
from com.sun.star.beans import PropertyValue
def prop(k,v):
 p=PropertyValue();p.Name=k;p.Value=v;return p
base=Path('/tmp/huaweibei-lo/root/usr/lib/libreoffice/program')
log=open('/tmp/rzb-stage3/uno-office.log','w')
p=None
ctx=uno.getComponentContext();resolver=ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx)
for _ in range(60):
 try:remote=resolver.resolve('uno:socket,host=127.0.0.1,port=20884;urp;StarOffice.ComponentContext');break
 except Exception:time.sleep(.3)
else:raise RuntimeError('UNO unavailable')
desktop=remote.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',remote)

root=Path.cwd();report=root/'研究报告/04_word/研究报告终稿.docx'
# Render a temporary copy using the installed fonts; the delivered Word
# retains its native equations and embedded fonts.
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
with ZipFile(report) as archive:parts={n:archive.read(n) for n in archive.namelist()}
font_tree=etree.fromstring(parts['word/fontTable.xml'])
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
for node in list(font_tree.iter()):
 if node.tag in ['{'+W+'}embedRegular','{'+W+'}embedBold','{'+W+'}embedItalic','{'+W+'}embedBoldItalic']:node.getparent().remove(node)
parts['word/fontTable.xml']=etree.tostring(font_tree,xml_declaration=True,encoding='UTF-8',standalone=True)
render_source=Path('/tmp/rzb-closed-loop/report-render-source.docx')
with ZipFile(render_source,'w',ZIP_DEFLATED) as archive:
 for name,data in parts.items():archive.writestr(name,data)
doc=desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(render_source)), '_blank',0,(prop('Hidden',True),prop('ReadOnly',False),prop('UpdateDocMode',3)))
assert len(doc.Text.String)>20000, '正文导入不完整，停止导出'
objects=doc.getEmbeddedObjects();repairs=[]
for name in sorted(objects.getElementNames(),key=lambda n:int(n[6:])):
 m=objects.getByName(name).Model;before=m.Formula
 after=before.replace('{+}', '{"+"}').replace('{−}', '{"−"}').replace('{-}', '{"-"}').replace('{*}', '{"*"}').replace('( 1 + r {)} ^', '{( 1 + r )} ^').replace('left |', 'left lline').replace('right |', 'right rline').replace('| A |', 'abs A')
 if after!=before:m.Formula=after;repairs.append({'object':name,'before':before,'after':after})
 natural=m.getVisualAreaSize(1)
 if before.startswith('matrix'):
  print('MATRIX',name,objects.getByName(name).Width,natural.Width,natural.Height,flush=True)
  objects.getByName(name).Width=natural.Width
  objects.getByName(name).Height=natural.Height
 m.FontNameText='FZFangSong-Z02';m.FontNameVariables='Times New Roman';m.FontNameNumbers='Times New Roman';m.FontNameFunctions='Times New Roman'
# Native TOC with page numbers in the renderer; save temporary roundtrip only
# to recover its TOC cache, never its converted mathematical objects.
for ix in range(doc.DocumentIndexes.Count):doc.DocumentIndexes.getByIndex(ix).update()
doc.refresh()
for ix in range(doc.DocumentIndexes.Count):doc.DocumentIndexes.getByIndex(ix).update()
assert len(doc.Text.String)>20000, '目录更新后正文不完整，停止导出'
doc.storeToURL(uno.systemPathToFileUrl('/tmp/rzb-closed-loop/toc-cache.docx'),(prop('FilterName','Office Open XML Text'),))
pdf=root/'研究报告/04_word/研究报告终稿.pdf'
doc.storeToURL(uno.systemPathToFileUrl(str(pdf)),(prop('FilterName','writer_pdf_Export'),))
(root/'研究报告/05_review/PDF兼容转换记录.json').write_text(json.dumps({'scope':'仅PDF渲染副本，交付DOCX未经过LibreOffice公式回写','objects':objects.Count,'quoted_isolated_signs':repairs},ensure_ascii=False,indent=2))
print('PDF',pdf,'objects',objects.Count,'repairs',len(repairs),'TOC',doc.DocumentIndexes.Count,flush=True)
doc.close(True)
