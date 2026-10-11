"""报告强制约束：源稿、原生Word格式、目录域和实际PDF一致性。"""
from pathlib import Path
import argparse, hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]

def body_policy_errors(sources,sections,tables,patterns):
    """只检查正文实际引用的材料，并保留可编辑源的位置。"""
    errors=[]
    def scan(value,location,stack=()):
        for line_no,line in enumerate(value.splitlines(),1):
            for rule,pattern in patterns.items():
                for match in re.finditer(pattern,line):
                    errors.append(f'{location}:{line_no}: {rule}: {match[0]}')
            for kind,key in re.findall(r'\[\[(SECTION|TABLE):([^\]]+)\]\]',line):
                token=(kind,key)
                if token in stack:
                    raise ValueError(f'正文引用循环: {location}:{line_no}: {token}')
                data=sections if kind=='SECTION' else tables
                name='生成段落.json' if kind=='SECTION' else '计算表.json'
                scan(data[key],f'{location}:{line_no} → {name}[{key}]',stack+(token,))
    for location,value in sources:
        scan(value,location)
    return errors

def check_figure_paragraphs(doc,policy,expected_count):
    from docx.oxml.ns import qn
    figure_policy=policy['figure_paragraph_format']
    figures=doc._element.xpath('.//w:body//w:p[.//w:drawing or .//w:pict]')
    captions=[p for p in doc._element.xpath('.//w:body//w:p') if re.match(r'^图\d+-',''.join(p.xpath('.//w:t/text()')).strip())]
    assert len(figures)==expected_count, '图片段落数与正文源不一致'
    assert len(captions)==len(figures),'图片与图题数量不一致'
    if figure_policy['inline_only']:
        assert not doc._element.xpath('.//w:body//wp:anchor | .//w:body//w:pict'),'图片应使用嵌入型，避免浮动定位覆盖段落居中'
    for i,p in enumerate(figures+(captions if figure_policy['include_captions'] else []),1):
        label=f'图片或图题段落{i}'
        assert p.xpath('./w:pPr/w:jc/@w:val')==[figure_policy['alignment']],label+'必须居中对齐'
        inds=p.xpath('./w:pPr/w:ind');assert len(inds)==1,label+'必须显式设置无缩进'
        for attr in figure_policy['zero_indent_attributes']:
            assert inds[0].get(qn('w:'+attr))=='0',label+'缩进未清零: '+attr
    return {'图片无缩进居中':len(figures),'图题无缩进居中':len(captions)}

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
    brief_source=(report/'供电公司讨论稿/讨论稿.md').read_text()
    errors=body_policy_errors(
        [(str(p.relative_to(root)),p.read_text()) for p in sources]+[('研究报告/供电公司讨论稿/讨论稿.md',brief_source)],
        sections,tables,policy['forbidden_body_patterns'])
    # 参数切片必须有响应；完整原始结果仍保留在计算资料。
    for key in re.findall(r'\[\[TABLE:([^\]]+)\]\]', '\n'.join(p.read_text() for p in sources)+'\n'+'\n'.join(sections.values())):
        if not key.startswith(('restore_storage_price_', 'restore_support_duration_h_', 'restore_line_cost_coefficient_', 'restore_initial_transfer_fraction_', 'restore_eta_', 'restore_growth_rate_')):
            continue
        rows=[[c.strip() for c in ln.strip('|').split('|')] for ln in tables[key].splitlines() if ln.startswith('|')][2:]
        if len(rows)>1 and len({tuple(row[1:]) for row in rows})==1:
            errors.append('无响应参数切片不得重复展示: '+key)
    for m in re.finditer(r'由(\d+(?:\.\d+)?)(%| MW| MVA|万元)?变为\1\2(?=[，；。 ])',body):
        errors.append('相同数值不能表述为变化: '+m[0])
    correlation=report/'05_review/当前版/1011局部优化/相关性复算.json'
    evidence=json.loads(correlation.read_text())
    for path,sha in evidence['原始记录SHA256'].items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,'相关性原始记录已变化，应复算'
    corr_rows=[[c.strip() for c in ln.strip('|').split('|')] for ln in tables['new_correlations'].splitlines() if ln.startswith('|')][2:]
    for row,item in zip(corr_rows,evidence['输入与结果'],strict=True):
        assert row[1:]==[f"{item[y+'_'+m]:.2f}" for y in ['clr','cost'] for m in ['pearson','spearman']],'相关表与复算结果不一致'
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
        result.update(check_figure_paragraphs(doc,policy,len(re.findall(r'\[\[FIG:',body))))
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
            from build_discussion_brief import check as check_brief
            check_brief(root,pdf=True)
            import pymupdf
            pdfpath=report/'04_word/研究报告终稿.pdf';pdf=pymupdf.open(pdfpath)
            assert any(s in str(pdf.metadata).lower() for s in ['wps','kingsoft'])
            # 同时验证渲染后的图片位置，防止Word结构正确但导出排版偏移。
            pdf_images=[(page,im) for page in pdf for im in page.get_image_info()]
            assert len(pdf_images)==len(doc.inline_shapes),'PDF图件数量与Word不一致'
            left=doc.sections[0].left_margin.pt;right=doc.sections[0].right_margin.pt
            offsets=[]
            for page,im in pdf_images:
                r=pymupdf.Rect(im['bbox']);offset=abs((r.x0+r.x1)/2-(page.rect.width+left-right)/2)
                assert offset<=policy['figure_paragraph_format']['pdf_center_tolerance_pt'],('PDF图片未居中',page.number+1,offset)
                offsets.append(offset)
            result['PDF图片最大居中偏差_pt']=round(max(offsets,default=0),4)
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
    out=review/'1011局部优化';out.mkdir(exist_ok=True)
    (out/f'{args.stage}约束检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='源稿SHA256'},ensure_ascii=False))

if __name__=='__main__':main()
