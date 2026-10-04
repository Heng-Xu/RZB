"""提取甲方批注、修订痕迹及范文语料，保留原文件。"""
from pathlib import Path
import hashlib,json,zipfile
from lxml import etree

ROOT=Path(__file__).resolve().parents[3]
REPORT=ROOT/'研究报告'
OUT=Path(__file__).parent/'1003反馈修订'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'

def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        root=etree.fromstring(z.read('word/document.xml'))
        paragraphs=root.xpath('//w:body//w:p',namespaces=NS)
        texts=[''.join(p.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)) for p in paragraphs]
        comments=[]
        if 'word/comments.xml' in z.namelist():
            cr=etree.fromstring(z.read('word/comments.xml'))
            for c in cr:
                cid=c.get(W+'id');started=False;selected=[];indices=[]
                for i,p in enumerate(paragraphs):
                    for el in p.iter():
                        if el.tag==W+'commentRangeStart' and el.get(W+'id')==cid:started=True;indices.append(i)
                        if started and el.tag in (W+'t',W+'delText'):selected.append(el.text or '')
                        if el.tag==W+'commentRangeEnd' and el.get(W+'id')==cid:started=False;indices.append(i)
                if not indices:
                    indices=[i for i,p in enumerate(paragraphs) if p.xpath('.//w:commentReference[@w:id="'+cid+'"]',namespaces=NS)]
                low=min(indices) if indices else 0;high=max(indices) if indices else low
                comments.append({'编号':cid,'作者':c.get(W+'author'),'日期':c.get(W+'date'),'意见':''.join(c.xpath('.//w:t/text()',namespaces=NS)),'锚定文字':''.join(selected),'段落索引':[low,high],'上下文':texts[max(0,low-1):high+2]})
        revisions=[]
        for i,p in enumerate(paragraphs):
            for el in p.xpath('.//w:ins|.//w:del',namespaces=NS):
                revisions.append({'段落索引':i,'类型':etree.QName(el).localname,'作者':el.get(W+'author'),'日期':el.get(W+'date'),'文字':''.join(el.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)),'上下文':texts[i]})
        accepted=[]
        for p in paragraphs:
            accepted.append(''.join(p.xpath('.//w:t[not(ancestor::w:del)]/text()',namespaces=NS)))
        return {'文件':str(path.relative_to(ROOT)),'SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'批注':comments,'修订痕迹':revisions,'正文':accepted}

def main():
    OUT.mkdir(exist_ok=True)
    path=REPORT/'甲方反馈/10.03 最新稿件的意见反馈/10.02研究报告 (甲方批注).docx'
    result=extract_docx(path)
    (OUT/'甲方批注与修订原文.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (OUT/'甲方批注定位.md').write_text('# 10.03 甲方批注定位\n\n'+'\n\n'.join('## 批注 '+c['编号']+'\n\n意见：'+c['意见']+'\n\n锚定：'+c['锚定文字']+'\n\n上下文：'+'\n\n'.join(c['上下文']) for c in result['批注']))
    (OUT/'甲方修订痕迹.md').write_text('# 甲方文字修订\n\n'+'\n\n'.join(f"段落 {r['段落索引']} / {r['类型']}：{r['文字']}\n\n上下文：{r['上下文']}" for r in result['修订痕迹']))
    corpus=REPORT/'范文与语料'
    sample=extract_docx(next(corpus.glob('*.docx')))
    (OUT/'宿迁范文提取.txt').write_text('\n\n'.join(sample['正文']))
    manifest=[]
    with zipfile.ZipFile(corpus/'提取语料.zip') as z:
        for item in z.infolist():
            if item.is_dir():continue
            name=item.filename
            if not item.flag_bits&0x800:
                try:name=name.encode('cp437').decode('gbk')
                except (UnicodeError,LookupError):pass
            raw=z.read(item)
            record={'文件名':name,'字节数':len(raw),'SHA256':hashlib.sha256(raw).hexdigest()}
            if name.lower().endswith(('.txt','.md','.json')):
                decoded=None
                for enc in ('utf-8-sig','gb18030'):
                    try:decoded=raw.decode(enc);break
                    except UnicodeError:pass
                if decoded is not None:
                    target=OUT/'语料文本'/Path(name).name;target.parent.mkdir(exist_ok=True)
                    target.write_text(decoded);record['提取文件']=str(target.relative_to(ROOT))
            manifest.append(record)
    (OUT/'语料登记.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps({'批注数':len(result['批注']),'文字修订数':len(result['修订痕迹']),'语料文件':manifest},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
