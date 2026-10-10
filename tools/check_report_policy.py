"""报告强制约束：源稿、原生Word格式、目录域和实际PDF一致性。"""
from pathlib import Path
import argparse, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--stage',choices=['source','docx','final'],default='source')
    args=parser.parse_args();root=args.root.resolve()
    policy=json.loads((root/'tools/report_policy.json').read_text())
    report=root/'研究报告';text=report/'03_MD/当前版';asset=report/'02图表/当前版';review=report/'05_review/当前版'
    tables=json.loads((asset/'计算表.json').read_text());sections=json.loads((asset/'生成段落.json').read_text())
    sources=sorted(text.glob('0[1-6] *.md'));assert len(sources)==6
    body='\n\n'.join(p.read_text() for p in sources)
    body=re.sub(r'\[\[SECTION:([^\]]+)\]\]',lambda m:sections[m[1]],body)
    body=re.sub(r'\[\[TABLE:([^\]]+)\]\]',lambda m:tables[m[1]],body)
    errors=[]
    for rule,pattern in policy['forbidden_body_patterns'].items():
        for m in re.finditer(pattern,body):errors.append(f'{rule}: {m[0]}')
    # 连续式中解释应合并到一段，不能用多个空行分列符号解释。
    if re.search(r'式中[^\n]*\n\s*\n式中',body):errors.append('相邻式中说明应合并')
    for equation in re.findall(r'\$\$([\s\S]*?)\$\$',body):
        if equation.count(r'\qquad')>=2 and r'\begin{aligned}' not in equation:
            errors.append('包含多组关系的长公式须显式分行')
    for name in re.findall(r'\[\[FIG:([^|]+)\|',body):
        if not (asset/(name+'.png')).is_file():errors.append('缺少图件: '+name)
    profiles=report/'数据来源/当前版/区域时序'
    summary=json.loads((profiles/'summary.json').read_text())
    import csv
    for region in policy['profile_regions']:
        p=profiles/f'{region}_8760.csv';rows=list(csv.DictReader(p.open()))
        assert len(rows)==policy['required_profile_hours']
        assert summary[region]['curve_sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
        assert len({r['hour'] for r in rows})==len(rows)
        assert all(r['net_mw'] and r['abs_mw'] for r in rows)
    assert not errors,'\n'.join(sorted(set(errors)))
    result={'状态':'通过','阶段':args.stage,'规则版本':policy['version'],'源稿SHA256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    if args.stage!='source':
        from docx import Document
        from docx.oxml.ns import qn
        docpath=report/'04_word/研究报告终稿.docx';doc=Document(docpath)
        def zero_indent(p):
            inds=p.xpath('./w:pPr/w:ind');assert len(inds)==1,'未显式设置段落缩进'
            ind=inds[0]
            for a in ['firstLine','firstLineChars','left','right']:
                assert ind.get(qn('w:'+a))=='0',(a,ind.attrib)
            assert all(ind.get(qn('w:'+a),'0')=='0' for a in ['hanging','hangingChars','leftChars','rightChars','startChars','endChars'])
        display=doc._element.xpath('.//w:p[m:oMathPara]')
        expected=len(re.findall(r'\\tag\{',body));assert len(display)==expected
        for p in display:
            zero_indent(p);assert p.xpath('./w:pPr/w:jc/@w:val')==['center']
            assert p.xpath('.//m:oMathParaPr/m:jc/@m:val')==['center']
            row=p.getparent().getparent()
            assert all(x.xpath('./w:pPr/w:keepNext') for x in row.xpath('.//w:p')),'公式须与式中解释保持同页'
        explanations=[p for p in doc._element.xpath('.//w:p') if ''.join(p.xpath('./w:r/w:t/text()')).startswith('式中')]
        for p in explanations:zero_indent(p)
        bookmarks={b.get(qn('w:name')):b for b in doc._element.xpath('.//w:bookmarkStart')}
        headings=json.loads((review/'目录标题.json').read_text());anchors={x[2] for x in headings}
        assert anchors<=bookmarks.keys()
        fields=[];field_results={}
        for p in doc._element.xpath('.//w:p[w:r/w:instrText]'):
            m=re.search(r'PAGEREF\s+(\w+)',''.join(p.xpath('./w:r/w:instrText/text()')))
            if not m:continue
            anchor=m[1];assert anchor in anchors
            assert p.xpath('./w:hyperlink/@w:anchor')==[anchor]
            fields.append(anchor)
            active=False;cached=[]
            for r in p.findall(qn('w:r')):
                kinds=r.xpath('./w:fldChar/@w:fldCharType')
                if 'separate' in kinds:active=True;continue
                if 'end' in kinds:active=False
                if active:cached.extend(r.xpath('./w:t/text()'))
            field_results[anchor]=''.join(cached)
        assert len(fields)==len(headings) and set(fields)==anchors
        for anchor in anchors:
            p=bookmarks[anchor].getparent();assert p[0].tag==qn('w:pPr'),'书签不能置于段落属性前'
        result.update(独立公式=len(display),式中段落=len(explanations),目录链接=len(fields),WordSHA256=hashlib.sha256(docpath.read_bytes()).hexdigest())
        hashes=json.loads((review/'装配源文件登记.json').read_text())
        assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in hashes.items()),'源稿变化后未重新装配'
        if args.stage=='final':
            import pymupdf
            pdfpath=report/'04_word/研究报告终稿.pdf';pdf=pymupdf.open(pdfpath)
            assert any(s in str(pdf.metadata).lower() for s in ['wps','kingsoft'])
            toc=json.loads((review/'目录页码核对.json').read_text())
            norm=lambda x:re.sub(r'\s+','',x)
            pages=[norm(p.get_text()) for p in pdf]
            # 正文第一页由第一章标题和印刷页码共同确定；封面+两页目录。
            lines=[norm(l) for p in list(pdf)[:3] for l in p.get_text().splitlines()]
            for entry in toc:
                title=norm(entry['标题']);n=entry['页码']
                assert field_results[entry['锚点']]==str(n),('Word页码域缓存与实际页不一致',entry)
                assert title in pages[n-1] and n>=4,entry
                hits=[l for l in lines if l.startswith(title)]
                assert len(hits)==1 and re.search(r'(\d+)$',hits[0][len(title):]),(entry,hits)
                assert int(re.search(r'(\d+)$',hits[0][len(title):])[1])==n,(entry,hits)
            # 检查WPS实际导出的目录内部链接是否指向对应标题页。
            links=[l for p in list(pdf)[:3] for l in p.get_links() if l.get('kind')==1]
            assert len(links)>=len(toc),('PDF目录缺少内部跳转',len(links),len(toc))
            title_links=[l for l in links if l['from'].x0<300]
            assert len(title_links)==len(toc)
            assert [l['page']+1 for l in title_links]==[e['页码'] for e in toc],'目录标题跳转目标与对应页码不一致'
            for entry in toc:
                assert entry['页码']-1 in {l['page'] for l in links},entry
            result.update(PDF页数=len(pdf),PDFSHA256=hashlib.sha256(pdfpath.read_bytes()).hexdigest())
            exported=json.loads((review/'WPS原生导出登记.json').read_text())
            assert exported['WordSHA256']==result['WordSHA256'] and exported['PDFSHA256']==result['PDFSHA256'],'Word/PDF导出登记未同步'
    out=review/'1010表述与Word修正';out.mkdir(exist_ok=True)
    (out/f'{args.stage}约束检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='源稿SHA256'},ensure_ascii=False))

if __name__=='__main__':main()
