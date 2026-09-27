"""对当前Word、PDF、图件和来源索引执行可重复的成品检查。"""
from pathlib import Path
from zipfile import ZipFile
import hashlib, json, re, subprocess
from lxml import etree
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'研究报告/05_review/闭环核验'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    source=ROOT/'研究报告/数据来源/当前报告数据来源.json'
    data=json.loads(source.read_text());report=data['report']
    for kind in ['docx','pdf']:check(kind+'与来源索引同版',sha(ROOT/report[kind])==report[kind+'_sha256'])
    files=sorted((ROOT/'研究报告/03_MD').glob('[0-9][0-9] *.md'))+[ROOT/'研究报告/03_MD/参考文献.md']
    text='\n'.join(p.read_text() for p in files)
    expected=len(re.findall(r'\\\(.*?\\\)',text,re.S))+len(re.findall(r'\\\[.*?\\\]',text,re.S))
    with ZipFile(ROOT/report['docx']) as z:
        xml=etree.fromstring(z.read('word/document.xml'));fonts=etree.fromstring(z.read('word/fontTable.xml'))
        math=xml.findall('.//m:oMath',NS)
        check('Word公式数与全部LaTeX表达式一致',len(math)==expected,{'expected':expected,'native':len(math)})
        wtext=''.join(xml.xpath('.//w:t/text()',namespaces=NS))
        check('无未渲染LaTeX',not re.search(r'\\(?:frac|mathrm|tag|Delta)|\\[\[\(]',wtext))
        check('目录缓存已更新','目录更新中' not in wtext)
        anchors=set(xml.xpath('.//w:sdt//w:hyperlink/@w:anchor',namespaces=NS))
        bookmarks=set(xml.xpath('.//w:bookmarkStart/@w:name',namespaces=NS))
        check('目录链接均有正文书签',bool(anchors) and anchors<=bookmarks)
        check('正文仿宋字体已嵌入',bool(fonts.xpath('./w:font[@w:name="方正仿宋_GBK"]/w:embedRegular',namespaces=NS)))
        check('Times New Roman已嵌入',bool(fonts.xpath('./w:font[@w:name="Times New Roman"]/w:embedRegular',namespaces=NS)))
        display=[p for p in xml.findall('.//w:p',NS) if re.fullmatch(r'（4-\d+）',''.join(p.xpath('./w:r/w:t/text()',namespaces=NS)).strip())]
        check('正文29组公式',len(display)==29,len(display))
        inline=len(math)-len(display)
        check('正文字符说明有独立行内公式',inline>150,inline)
    pdf=pymupdf.open(ROOT/report['pdf']);tiny=[];bounds=[];bad=[]
    for i,p in enumerate(pdf):
        if '\ufffd' in p.get_text() or '<?>' in p.get_text():bad.append(i+1)
        for b in p.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if span['size']<4:tiny.append({'page':i+1,'text':span['text']})
                    if x0<0 or y0<0 or x1>p.rect.width+1 or y1>p.rect.height+1:bounds.append({'page':i+1,'text':span['text']})
    check('整篇PDF无微小字号',not tiny,tiny)
    check('整篇PDF文字无页面越界',not bounds,bounds)
    check('整篇PDF无乱码替换符',not bad,bad)
    pdftext=''.join(p.get_text() for p in pdf);compact=re.sub(r'\s+','',pdftext)
    for i in range(1,30):check('PDF式（4-'+str(i)+'）可检索','（4-'+str(i)+'）' in compact)
    bibliography=pdftext.rsplit('参考文献',1)[-1]
    listed=[int(n) for n in re.findall(r'\[(\d+)\]',bibliography)]
    check('成品参考文献连续编号1至68',listed==list(range(1,69)),listed)
    toc=''.join(xml.find('.//w:sdt',NS).xpath('.//w:t/text()',namespaces=NS))
    check('目录第七章为结论与展望','结论与展望' in toc and '工程应用建议与总结' not in toc)
    check('目录无公式和来源附录','公式符号说明' not in toc and '数据来源说明' not in toc)
    check('参考文献无原始出处标签','原始出处' not in bibliography)
    note=ROOT/'研究报告/数据来源/数据来源说明.pdf'
    nd=pymupdf.open(note);nt=''.join(p.get_text() for p in nd)
    check('独立数据来源说明含六节',all(t in nt for t in ['1. 文件用途','2. 原始资料','3. 模型、结果','4. 文献与引文','5. 图表编号','6. 逐图逐表']))
    check('独立说明未列缺项及后续补充要求','缺项及后续补充要求' not in nt)
    note_bounds=[]
    for i,p in enumerate(nd):
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<0 or y0<0 or x1>p.rect.width+1 or y1>p.rect.height+1:note_bounds.append([i+1,span['text']])
    check('独立说明文字无页面越界',not note_bounds,note_bounds)
    for item in data['materials']:check('独立说明收录图表 '+item['number'],item['number'] in nt)
    figures=json.loads((ROOT/'研究报告/05_review/图件展示修订核验.json').read_text())
    check('正式图件数',len(figures)==17,len(figures))
    for f in figures:
        name=f['number'];p=ROOT/'研究报告/02图表/final_figures'/name
        check(name+'数据保持不变',f['data_unchanged'])
        check(name+'无内部地区编码',not any(re.search(r'QX-\d+|BDZ-\d+',t) for t in f['display_text']))
        check(name+'使用实际仿宋字体','FZFangSong-Z02' in f['font_families'])
        check(name+'当前PNG哈希',sha(p.with_suffix('.png'))==f['figure_sha256'])
        svg=p.with_suffix('.svg').read_text();check(name+'SVG字体与PDF字体一致','FZFangSong-Z02' in svg)
    human=ROOT/'研究报告/数据来源/当前报告数据来源与计算审查.pdf'
    hp=pymupdf.open(human);ht=''.join(p.get_text() for p in hp)
    human_bounds=[];human_tiny=[]
    for i,p in enumerate(hp):
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if span['size']<4:human_tiny.append({'page':i+1,'text':span['text']})
                    if x0<0 or y0<0 or x1>p.rect.width+1 or y1>p.rect.height+1:human_bounds.append({'page':i+1,'text':span['text']})
    check('人读来源PDF文字无页面越界',not human_bounds,human_bounds)
    check('人读来源PDF无微小字号',not human_tiny,human_tiny)
    check('人读来源PDF无乱码替换符','\ufffd' not in ht and '<?>' not in ht)
    for r in data['records']:check('人读PDF包含来源记录 '+r['id'],r['id'] in ht)
    check('人读PDF绑定同版Word',report['docx_sha256'] in re.sub(r'\s+','',ht))
    check('人读PDF绑定同版报告PDF',report['pdf_sha256'] in re.sub(r'\s+','',ht))
    result={'passed':all(x['passed'] for x in checks),'checks':len(checks),'failed':[x for x in checks if not x['passed']],
        'report_pages':len(pdf),'source_note_pages':len(nd),'source_audit_pages':len(hp),'native_math_count':len(math),'inline_math_count':inline,
        'report_formulas':29,'formal_figures':17,'formal_tables':15,'source_records':len(data['records']),
        'county_rows_recalculated':len(data['county_statistics']),
        'scope':'成品哈希、原生公式、目录、字体、文字边界、图件、人工审查文件与机读记录一致性；人工复核记录另存',
        'checks_detail':checks}
    (QA/'最终成品核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks_detail'},ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
