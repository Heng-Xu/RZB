"""保留原生公式，写入渲染器目录缓存并嵌入正文实际字体。"""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, uuid
from lxml import etree
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
C='http://schemas.openxmlformats.org/package/2006/content-types'

def main():
    p=ROOT/'研究报告/04_word/研究报告终稿.docx'
    with ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
    doc=etree.fromstring(parts['word/document.xml'])
    cache=Path('/tmp/rzb-closed-loop/toc-cache.docx')
    with ZipFile(cache) as z:cached=etree.fromstring(z.read('word/document.xml'))
    old=doc.find('.//{'+W+'}sdt');new=cached.find('.//{'+W+'}sdt')
    assert old is not None and new is not None
    toc=deepcopy(new)
    # The roundtrip's section IDs refer to its own package. Keep the original
    # section boundary outside the TOC and translate the TOC styles.
    style_ids={'ContentsHeading':'42','Contents1':'19','Contents2':'20','Contents3':'14'}
    for e in list(toc.iter()):
        if e.tag in ['{'+W+'}sectPr','{'+W+'}webHidden']:
            e.getparent().remove(e)
        elif e.tag=='{'+W+'}pStyle':
            e.set('{'+W+'}val',style_ids.get(e.get('{'+W+'}val'),'19'))
        elif e.tag=='{'+W+'}rStyle':e.getparent().remove(e)
    # Recreate the cached links' heading bookmarks in the original document.
    def paragraph_text(node):return ''.join(node.xpath('.//w:t/text()',namespaces={'w':W})).replace(' ','')
    originals={paragraph_text(n):n for n in doc.findall('./{'+W+'}body/{'+W+'}p') if paragraph_text(n)}
    anchors={e.get('{'+W+'}anchor') for e in toc.findall('.//{'+W+'}hyperlink')}
    existing={e.get('{'+W+'}name') for e in doc.findall('.//{'+W+'}bookmarkStart')}
    ident=max([int(e.get('{'+W+'}id')) for e in doc.findall('.//{'+W+'}bookmarkStart')]+[0])+1
    copied=set()
    for e in cached.findall('.//{'+W+'}bookmarkStart'):
        name=e.get('{'+W+'}name')
        if name not in anchors or name in existing:continue
        parent=e.getparent()
        while parent is not None and parent.tag!='{'+W+'}p':parent=parent.getparent()
        if parent is None:continue
        target=originals.get(paragraph_text(parent))
        if target is None:continue
        start=etree.Element('{'+W+'}bookmarkStart',{'{'+W+'}name':name,'{'+W+'}id':str(ident)})
        end=etree.Element('{'+W+'}bookmarkEnd',{'{'+W+'}id':str(ident)})
        target.insert(1 if target.find('{'+W+'}pPr') is not None else 0,start);target.append(end)
        copied.add(name);ident+=1
    assert anchors <= (existing|copied), '目录链接缺少正文书签：'+str(anchors-(existing|copied))
    old.getparent().replace(old,toc)
    parts['word/document.xml']=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    ft=etree.fromstring(parts['word/fontTable.xml'])
    relpath='word/_rels/fontTable.xml.rels'
    rel=etree.fromstring(parts[relpath]) if relpath in parts else etree.Element('{'+P+'}Relationships',nsmap={None:P})
    for i,(name,file) in enumerate([('方正仿宋_GBK','/usr/share/fonts/wps-office/FZFSK.TTF'),('Times New Roman','/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf')],1):
        font=TTFont(file)
        assert not font['OS/2'].fsType & 2, '字体禁止嵌入：'+file
        raw=bytearray(Path(file).read_bytes())
        guid=uuid.UUID(bytes=hashlib.sha256(raw).digest()[:16])
        key=bytes.fromhex(guid.hex)[::-1]
        for j in range(32):raw[j]^=key[j%16]
        dest=f'fonts/report-font-{i}.odttf';parts['word/'+dest]=bytes(raw)
        node=next((e for e in ft if e.get('{'+W+'}name')==name),None)
        if node is None:node=etree.SubElement(ft,'{'+W+'}font',{'{'+W+'}name':name})
        for e in list(node):
            if e.tag=='{'+W+'}embedRegular':node.remove(e)
        rid=f'rIdReportFont{i}'
        etree.SubElement(node,'{'+W+'}embedRegular',{'{'+R+'}id':rid,'{'+W+'}fontKey':'{'+str(guid).upper()+'}'})
        for e in list(rel):
            if e.get('Id')==rid:rel.remove(e)
        etree.SubElement(rel,'{'+P+'}Relationship',Id=rid,Type=R+'/font',Target=dest)
    ct=etree.fromstring(parts['[Content_Types].xml'])
    if not any(n.get('Extension')=='odttf' for n in ct):
        etree.SubElement(ct,'{'+C+'}Default',Extension='odttf',ContentType='application/vnd.openxmlformats-officedocument.obfuscatedFont')
    settings=etree.fromstring(parts['word/settings.xml'])
    if settings.find('{'+W+'}embedTrueTypeFonts') is None:etree.SubElement(settings,'{'+W+'}embedTrueTypeFonts')
    for file,node in [('word/fontTable.xml',ft),(relpath,rel),('[Content_Types].xml',ct),('word/settings.xml',settings)]:
        parts[file]=etree.tostring(node,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(p,'w',ZIP_DEFLATED) as z:
        for k,v in parts.items():z.writestr(k,v)
    print('目录缓存及仿宋、Times New Roman字体已写入；原生公式保持不变。')

if __name__=='__main__':main()
