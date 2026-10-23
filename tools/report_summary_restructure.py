"""在10.23甲方反馈原包内重构成果总结，保留已有批注及修订。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import csv,hashlib,json,re,shutil
from lxml import etree as E
from summary_feedback import BASE,REVIEW,ROOT,NS,q,text,extract
from revise_current_discussion import Reviser,accept_view
from revise_discussion_selection import reject_ids,revision_nodes,revision_identity

SOURCE=Path('研究报告/03_MD/成果总结/成果总结.md')
OUT=Path('研究报告/04_word/成果总结.docx');PDF=OUT.with_suffix('.pdf')
BASE_SHA='a9834afec1ac431ddf161203d639267c26b2304955aa46cadd4b1bd7186f6b3c'
INDENTS=['firstLine','firstLineChars','hanging','hangingChars','left','right','start','end','leftChars','rightChars','startChars','endChars']
TABLES={65:'final_measures',84:'lookup_matrix_0_low',94:'lookup_matrix_2_high'}
FIGURES=['plan_cost_difference','annual_clr']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
serialize=lambda e:E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)

def active(root=ROOT):
    return read(root/'tools/report_policy.json')['summary'].get('mode')=='feedback_restructure'

def package(path):
    with ZipFile(path)as z:return {name:z.read(name)for name in z.namelist()}

def save(path,parts):
    with ZipFile(path,'w',ZIP_DEFLATED)as z:
        for name,data in parts.items():z.writestr(name,data)

def spec(root=ROOT):
    raw=(root/SOURCE).read_text();items=[]
    pattern=r'<!-- (base|after):(\d+) -->\n(.*?)(?=\n\n<!-- |\Z)'
    for mode,index,value in re.findall(pattern,raw,re.S):
        value=value.strip();kind='body'
        if value.startswith('# '):kind='title';value=value[2:]
        elif value.startswith('## '):kind='h1';value=value[3:]
        elif value.startswith('### '):kind='h2';value=value[4:]
        elif value.startswith('[[FIG:'):kind='figure'
        elif value.startswith('[[KEEP_TABLE:'):kind='table'
        elif value.startswith('表')and re.match(r'表\d+ ',value):kind='caption'
        items.append(dict(mode=mode,index=int(index),text=value,kind=kind))
    assert items and len({(r['mode'],r['index'])for r in items})==len(items),'源稿锚点重复'
    assert [(r['index'],r['mode']=='after')for r in items]==sorted((r['index'],r['mode']=='after')for r in items),'源稿须按原稿位置组织'
    assert re.sub(pattern,'',raw,flags=re.S).strip()=='','存在未解析源稿'
    return items

def final_view(doc):
    # 仅用于读取最终内容；交付Word不接受任何已有修订。
    result=deepcopy(doc)
    for p in list(result.xpath('.//w:p[w:pPr/w:rPr/w:del]',namespaces=NS)):
        if not text(p) and not p.xpath('.//*[local-name()="oMath" and not(ancestor::w:del)]',namespaces=NS):
            p.getparent().remove(p)
    return accept_view(result)

def rows(table):
    return [[text(c)for c in tr.findall(q('tc'))]for tr in table.findall(q('tr'))]

def figures_check(root,plans):
    source=root/'研究报告/数据来源/当前版/1017报告案例更新'
    allrows=list(csv.DictReader((source/'annual_clr.csv').open()))
    assert len(allrows)==60
    for row in allrows:
        region={'邳州':'pizhou','市区':'city'}[row['地区']]
        case={'刚性':'rigid','弹性':'elastic_capacity'}[row['方案']]
        a=next(a for a in plans[region,case]['annual']if a['year']==int(row['年份']))
        for cn,key in [('容载比','clr'),('年末容量_MVA','capacity_mva'),('规划峰值_MW','peak_mw')]:assert abs(float(row[cn])-a[key])<1e-9
    for row in csv.DictReader((source/'plan_cost_difference.csv').open()):
        region={'邳州':'pizhou','市区':'city'}[row['地区']]
        key={'主变':'transformer','储能':'storage','联络':'line'}[row['措施']]+'_npv_10k'
        value=sum(a[key]for a in plans[region,'rigid']['annual'])-sum(a[key]for a in plans[region,'elastic_capacity']['annual'])
        assert abs(float(row['费用差_万元'])-value)<1e-8
    return [{'图件':name,'PNG':sha(root/'研究报告/02图表/当前版'/(name+'.png')),'逐点数据':str((source/(name+'.csv')).relative_to(root)),'CSV':sha(source/(name+'.csv'))}for name in FIGURES]

def source_check(root=ROOT):
    from report_summary import inputs,f,summary_prose_errors
    from check_report_policy import body_policy_errors
    assert sha(root/BASE)==BASE_SHA,'甲方基线已变更，须重新提取并核对锚点'
    items=spec(root);raw=(root/SOURCE).read_text();policy=read(root/'tools/report_policy.json')
    errors=body_policy_errors([(str(SOURCE),raw)],{},{},policy['forbidden_body_patterns'])
    errors+=summary_prose_errors(raw,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    assert not re.search(r'\[\d+\]|参考文献|参考依据|\$\$|容载比为同范围|无量纲|式中，',raw),'凝练总结不恢复甲方删去的定义、文献及公式释义'
    heads=[r['text']for r in items if r['kind']=='h1'];assert len(heads)==4
    assert [s[:2]for s in heads]==['一、','二、','三、','四、']
    assert {r['index']for r in items if r['kind']=='table'}==set(TABLES)
    assert [re.fullmatch(r'\[\[FIG:([^|]+)\|(.+)\]\]',r['text'])[1]for r in items if r['kind']=='figure']==FIGURES
    tables,plans,proof=inputs(root)
    costs={c:sum(plans[r,c]['cost_npv_10k']for r in ['pizhou','city'])for c in ['rigid','elastic_capacity']}
    difference=costs['rigid']-costs['elastic_capacity']
    for value in [costs['rigid'],costs['elastic_capacity'],difference,difference/costs['rigid']*100]:assert f(value)in raw
    for region in ['pizhou','city']:
        for key in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']:
            diff=abs(sum(a[key]for a in plans[region,'rigid']['annual'])-sum(a[key]for a in plans[region,'elastic_capacity']['annual']))
            assert f(diff)+'万元'in raw,'措施费用差缺少当前结果支撑'
    import pandas as pd
    from matrix_planning_windows import records
    rawcells=records(pd.read_csv(root/policy['matrix_display']['source_csv']))
    with ZipFile(root/BASE)as z:original=E.fromstring(z.read('word/document.xml'))
    base=list(original.find(q('body')))
    for index,key in TABLES.items():
        expected=[tables[key]['headers']]+tables[key]['rows']
        assert rows(base[index])==expected,'原稿保留表与锁定结果不一致：'+key
        if key.startswith('lookup_matrix_'):
            assert [v for row in tables[key]['rows']for v in row[2:]]==[r['推荐窗口']for r in rawcells if r['表键']==key]
    figures=figures_check(root,plans)
    result={'状态':'通过','阶段':'source','基线SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),'数据核验':proof,'保留表格数':3,'推荐矩阵展示数':2,'图件核验':figures,'正文字符数':sum(len(r['text'])for r in items if r['kind']not in ['table','figure'])}
    (root/REVIEW/'源稿核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def zero_center(p):
    pp=p.find(q('pPr'))
    if pp is None:pp=E.Element(q('pPr'));p.insert(0,pp)
    for tag in ['ind','jc']:
        for old in list(pp.findall(q(tag))):pp.remove(old)
    E.SubElement(pp,q('ind'),{q(k):'0'for k in INDENTS});E.SubElement(pp,q('jc'),{q('val'):'center'})

def inserted_paragraph(template,value,revision,caption=False,note=False):
    p=deepcopy(template)
    for child in list(p):
        if child.tag!=q('pPr'):p.remove(child)
    pp=p.find(q('pPr'));rp=pp.find(q('rPr'))
    for marker in list(rp)if rp is not None else []:
        if marker.tag in [q('ins'),q('del')]:rp.remove(marker)
    if rp is None:rp=E.SubElement(pp,q('rPr'))
    rp.append(revision.mark('ins'))
    ins=revision.mark('ins');run=E.SubElement(ins,q('r'));rpr=E.SubElement(run,q('rPr'))
    E.SubElement(rpr,q('rFonts'),{q('ascii'):'Times New Roman',q('hAnsi'):'Times New Roman',q('eastAsia'):'方正仿宋_GBK'})
    E.SubElement(rpr,q('sz'),{q('val'):'24'if caption or note else'32'})
    E.SubElement(run,q('t')).text=value;p.append(ins)
    if caption:zero_center(p)
    if note:
        for old in list(pp.findall(q('ind'))):pp.remove(old)
        E.SubElement(pp,q('ind'),{q(k):'0'for k in INDENTS})
        spacing=pp.find(q('spacing'));spacing.set(q('line'),'370')
    return p

def delete_table(table,revision):
    for row in table.findall(q('tr')):
        pr=row.find(q('trPr'))
        if pr is None:pr=E.Element(q('trPr'));row.insert(0,pr)
        pr.append(revision.mark('del'))
        for p in row.findall('.//'+q('p')):
            revision.replace(p,'')
            for math in list(p):
                if E.QName(math).localname in ['oMath','oMathPara']:
                    if E.QName(math).localname=='oMathPara':
                        for equation in list(math):
                            if E.QName(equation).localname!='oMath':continue
                            at=math.index(equation);math.remove(equation);mark=revision.mark('del');mark.append(equation);math.insert(at,mark)
                    else:
                        at=p.index(math);p.remove(math);mark=revision.mark('del');mark.append(math);p.insert(at,mark)

def format_paragraph(p,value,kind,revision):
    lead=value.find('。')+1 if re.match('[一二三]是',value)else 0
    offset=0
    for run in list(p.xpath('.//w:r[w:t and not(ancestor::w:del)]',namespaces=NS)):
        source=''.join(run.xpath('./w:t/text()',namespaces=NS));pieces=[source]
        if offset<lead<offset+len(source):pieces=[source[:lead-offset],source[lead-offset:]]
        parent=run.getparent();at=parent.index(run)
        for value_ in pieces:
            target=deepcopy(run)
            for child in list(target):
                if child.tag!=q('rPr'):target.remove(child)
            E.SubElement(target,q('t'),{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=value_
            pr=target.find(q('rPr'));old=deepcopy(pr)if pr is not None else E.Element(q('rPr'))
            if pr is None:pr=E.Element(q('rPr'));target.insert(0,pr)
            bold=kind in ['h1','h2']or offset<lead
            font='方正黑体_GBK'if kind=='h1'else'方正楷体_GBK'if kind=='h2'or offset<lead else'方正仿宋_GBK'
            for tag in ['rFonts','sz','szCs','b','bCs','i','iCs']:
                for child in list(pr.findall(q(tag))):pr.remove(child)
            E.SubElement(pr,q('rFonts'),{q('ascii'):'Times New Roman',q('hAnsi'):'Times New Roman',q('eastAsia'):font,q('cs'):'Times New Roman'})
            size='36'if kind=='h1'else'24'if kind=='caption'else'32'
            for tag,val in [('sz',size),('szCs',size),('b',int(bold)),('bCs',int(bold)),('i',0),('iCs',0)]:E.SubElement(pr,q(tag),{q('val'):str(val)})
            change=revision.mark('rPrChange');change.append(old);pr.append(change)
            parent.insert(at,target);at+=1;offset+=len(value_)
        parent.remove(run)

def format_matrix(table,revision):
    allrows=table.findall(q('tr'))
    for ri,row in enumerate(allrows):
        for p in row.findall('.//'+q('p')):
            pp=p.find(q('pPr'));oldpp=deepcopy(pp)
            spacing=pp.find(q('spacing'));spacing.set(q('line'),'460')
            if ri==len(allrows)-1 and pp.find(q('keepNext'))is None:E.SubElement(pp,q('keepNext'))
            change=revision.mark('pPrChange');change.append(oldpp);pp.append(change)
            for run in p.findall(q('r')):
                pr=run.find(q('rPr'));old=deepcopy(pr)
                for tag in ['rFonts','sz','szCs']:
                    for child in list(pr.findall(q(tag))):pr.remove(child)
                E.SubElement(pr,q('rFonts'),{q('ascii'):'Times New Roman',q('hAnsi'):'Times New Roman',q('eastAsia'):'方正仿宋_GBK',q('cs'):'Times New Roman'})
                E.SubElement(pr,q('sz'),{q('val'):'28'});E.SubElement(pr,q('szCs'),{q('val'):'28'})
                change=revision.mark('rPrChange');change.append(old);pr.append(change)

def reject_new(doc,ids):
    restored=deepcopy(doc)
    for change in list(restored.xpath('.//w:rPrChange',namespaces=NS)):
        if change.get(q('id'))not in ids:continue
        pr=change.getparent();old=deepcopy(change.find(q('rPr')))
        for child in list(pr):pr.remove(child)
        for child in old:pr.append(child)
    for change in list(restored.xpath('.//w:pPrChange',namespaces=NS)):
        if change.get(q('id'))not in ids:continue
        pr=change.getparent();old=deepcopy(change.find(q('pPr')))
        for child in list(pr):pr.remove(child)
        for child in old:pr.append(child)
    return reject_ids(restored,ids)

def display_date(index):
    tz=timezone(timedelta(hours=8))
    if index<67:return (datetime(2026,10,23,13,5,tzinfo=tz)+timedelta(minutes=225*index/66)).isoformat(timespec='seconds')
    return (datetime(2026,10,26,9,5,tzinfo=tz)+timedelta(minutes=75*(index-67)/46)).isoformat(timespec='seconds')

def build(root=ROOT):
    proof=source_check(root);extract(root);parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml'])
    before=list(doc.find(q('body')));revision=Reviser(doc);items=spec(root);by_index={r['index']:r for r in items if r['mode']=='base'}
    additions={r['index']:r for r in items if r['mode']=='after'};newids=[];changes=[];times=[]
    started=datetime.now(timezone.utc).isoformat();oldids={r.get(q('id'))for r in revision_nodes(doc)}
    for i,block in enumerate(before):
        revision.date=display_date(i);previous=revision.next;rule=by_index.get(i)
        if block.tag==q('p'):
            value=rule['text']if rule is not None else''
            if value!=text(block):
                changes.append({'基线块':i,'原文':text(block),'修改后':value})
                revision.replace(block,value)
                if value:format_paragraph(block,value,rule['kind'],revision)
            if i in [44,99,109]:
                pp=block.find(q('pPr'));previous_pr=deepcopy(pp)
                if i in [44,99]:E.SubElement(pp,q('pageBreakBefore'))
                elif pp.find(q('keepNext'))is None:E.SubElement(pp,q('keepNext'))
                change=revision.mark('pPrChange');change.append(previous_pr);pp.append(change)
        elif block.tag==q('tbl'):
            if i not in TABLES:delete_table(block,revision)
            elif i in [84,94]:format_matrix(block,revision)
        if i in additions:
            item=additions[i]
            if item['kind']=='figure':
                from discussion_expansion import image_paragraph
                name,caption=re.fullmatch(r'\[\[FIG:([^|]+)\|(.+)\]\]',item['text']).groups()
                image=image_paragraph(root/'研究报告/02图表/当前版'/(name+'.png'),revision,parts)
                # 图形为嵌入型，图题沿用原稿表题的字号、字体。
                block.addnext(image);image.addnext(inserted_paragraph(before[64],caption,revision,caption=True))
            else:block.addnext(inserted_paragraph(before[5],item['text'],revision,note=True))
        ids=[str(n)for n in range(previous,revision.next)];newids+=ids
        if ids:times.append({'基线块':i,'新增修订ID':ids,'显示日期':revision.date,'实际生成时间UTC':started})
    # 原批注指向已删除的文献标注，沿用原ID，将锚点扩至重写后的同一段落。
    anchor=before[5];start=anchor.find(q('commentRangeStart'));end=anchor.find(q('commentRangeEnd'))
    if start is not None and end is not None:
        anchor.remove(start);anchor.remove(end);anchor.insert(1,start);anchor.append(end)
        refs=anchor.xpath('./w:r[w:commentReference]',namespaces=NS)
        for ref in refs:anchor.remove(ref);anchor.append(ref)
    settings=E.fromstring(parts['word/settings.xml'])
    for old in list(settings.findall(q('revisionView'))):settings.remove(old)
    E.SubElement(settings,q('revisionView'),{q(n):'0'for n in ['markup','comments','insDel','formatting']})
    tracking=settings.find(q('trackRevisions'))
    if tracking is None:tracking=E.SubElement(settings,q('trackRevisions'))
    tracking.set(q('val'),'1');parts['word/settings.xml']=serialize(settings);parts['word/document.xml']=serialize(doc)
    ct=E.fromstring(parts['[Content_Types].xml']);cns='http://schemas.openxmlformats.org/package/2006/content-types'
    if not any(e.get('Extension')=='png'for e in ct):E.SubElement(ct,'{'+cns+'}Default',Extension='png',ContentType='image/png')
    parts['[Content_Types].xml']=serialize(ct)
    save(root/OUT,parts)
    manifest={'状态':'已重构，待原生及WPS核验','基线':str(BASE),'基线SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),'WordSHA256':sha(root/OUT),'原有修订ID':sorted(oldids,key=int),'新增修订ID':newids,'实际操作开始UTC':started,'显示日期性质':'用户指定的修订显示元数据，不表示实际编辑过程；原有修订及批注日期不变','时间映射':times,'段落修改':changes,'保留表格':TABLES,'图件':proof['图件核验'],'批注处理':'保留原ID、作者、日期及批注部件原字节；原文献锚点扩至重构后的同一段落','维护代码':{str(p):sha(root/p)for p in [Path('tools/report_summary_restructure.py'),Path('tools/summary_feedback.py')]}}
    (root/REVIEW/'重构与修订登记.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    docx_check(root)

def signature(doc):
    final=final_view(doc)
    return [(E.QName(b).localname, ''.join(b.xpath('.//w:t/text()|.//*[local-name()="oMath"]//*[local-name()="t"]/text()',namespaces=NS)))for b in final.find(q('body'))if b.tag in [q('p'),q('tbl')]]

def docx_check(root=ROOT):
    result=source_check(root);old=package(root/BASE);new=package(root/OUT)
    baseline=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml']);reg=read(root/REVIEW/'重构与修订登记.json')
    assert reg['WordSHA256']==sha(root/OUT)and reg['正文源SHA256']==sha(root/SOURCE),'Word或源稿变化后须重新登记修订'
    ids=set(reg['新增修订ID']);oldrev=revision_nodes(baseline);newrev=revision_nodes(doc)
    assert len({r.get(q('id'))for r in newrev})==len(newrev),'修订ID重复'
    assert {revision_identity(r)for r in oldrev}<={revision_identity(r)for r in newrev},'原有修订元数据丢失'
    restored=reject_new(doc,ids)
    assert signature(restored)==signature(baseline),'拒绝本轮修订须恢复甲方原稿的完整最终内容'
    original_events={(revision_identity(r),''.join(r.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for r in oldrev}
    restored_events={(revision_identity(r),''.join(r.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for r in revision_nodes(restored)}
    assert original_events==restored_events,'原有修订正文丢失'
    allowed={'word/document.xml','word/settings.xml','word/_rels/document.xml.rels','[Content_Types].xml'}
    for name,data in old.items():
        if name not in allowed:assert new[name]==data,'未涉及包部件变化：'+name
    assert new['word/comments.xml']==old['word/comments.xml']and new['word/commentsExtended.xml']==old['word/commentsExtended.xml']
    for node in newrev:
        if node.get(q('id'))in ids:
            assert node.get(q('author'))=='xh'
            date=datetime.fromisoformat(node.get(q('date')))
            assert (datetime.fromisoformat('2026-10-23T13:00:00+08:00')<=date<=datetime.fromisoformat('2026-10-23T17:00:00+08:00'))or(datetime.fromisoformat('2026-10-26T09:00:00+08:00')<=date<=datetime.fromisoformat('2026-10-26T10:23:00+08:00'))
    settings=E.fromstring(new['word/settings.xml']);assert settings.find(q('trackRevisions')).get(q('val'))=='1'
    final=final_view(doc);body=final.find(q('body'));items=spec(root)
    actual=[text(p)for p in body.findall(q('p'))if text(p)]
    expected=[]
    for item in items:
        if item['kind']=='table':continue
        if item['kind']=='figure':expected.append(re.fullmatch(r'\[\[FIG:([^|]+)\|(.+)\]\]',item['text'])[2])
        else:expected.append(item['text'])
    assert actual==expected,'源稿与原生Word最终正文不一致'
    from report_summary import inputs
    tables,_,_=inputs(root);finaltables=body.findall(q('tbl'));assert len(finaltables)==3
    for table,key in zip(finaltables,TABLES.values()):assert rows(table)==[tables[key]['headers']]+tables[key]['rows']
    assert not final.xpath('.//*[local-name()="oMath"]'),'凝练总结不保留独立公式'
    pictures=body.xpath('.//w:drawing',namespaces=NS);assert len(pictures)==2
    for p in body.findall(q('p')):
        if p.xpath('.//w:drawing',namespaces=NS)or re.match(r'^图[12] ',text(p)):
            assert p.xpath('./w:pPr/w:jc/@w:val',namespaces=NS)==['center']
            assert all(p.find('./'+q('pPr')+'/'+q('ind')).get(q(k))=='0'for k in INDENTS)
            assert not p.xpath('.//*[local-name()="anchor"]'),'图片须为嵌入型'
    # 原批注仍有有效正文锚点，且在同一源段落。
    starts=doc.xpath('.//w:commentRangeStart[@w:id="0"]',namespaces=NS);ends=doc.xpath('.//w:commentRangeEnd[@w:id="0"]',namespaces=NS)
    assert len(starts)==len(ends)==1 and starts[0].getparent()is ends[0].getparent()
    assert text(starts[0].getparent()).startswith('一是分布式光伏')
    result.update(阶段='docx',WordSHA256=sha(root/OUT),保留原有修订=len(oldrev),新增修订=len(ids),原批注保留='原部件字节一致，原ID及日期保持',拒绝本轮恢复核验='通过',表格逐格核验='通过',图形居中及零缩进='通过',原生最终视图段落数=len(actual))
    (root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def final_check(root=ROOT):
    import pymupdf
    result=docx_check(root);pdf=pymupdf.open(root/PDF)
    assert 'wps'in str(pdf.metadata).lower()or'kingsoft'in str(pdf.metadata).lower(),'PDF须由WPS导出'
    assert 11<=len(pdf)<=13,'篇幅须约12页：'+str(len(pdf))
    normalize=lambda t:re.sub(r'\s+','',t).replace('−','-').replace('－','-')
    full=normalize(''.join(p.get_text()for p in pdf));doc=final_view(E.fromstring(package(root/OUT)['word/document.xml']))
    expected_full=normalize(''.join(doc.xpath('//w:body//w:t/text()',namespaces=NS)))
    assert full==expected_full,'PDF最终全文须与Word最终视图逐字一致；检查删除公式及多余符号残留'
    for p in doc.xpath('//w:body//w:p',namespaces=NS):
        t=normalize(text(p))
        assert not t or t in full,'PDF缺少最终正文或表格：'+t[:80]
    for phrase in ['式中，','Pearson','参考依据','参考文献','撰稿人：','无量纲[1]']:
        assert phrase not in full,'PDF显示了应删除的详细内容：'+phrase
    positions=[]
    for page in pdf:
        assert abs(page.rect.width-595.3)<1 and abs(page.rect.height-841.9)<1
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if span['text'].strip():
                        x0,y0,x1,y1=span['bbox'];right=522 if re.search('[，。；：？！、）”]$',span['text'])else 508
                        assert x0>=87 and x1<=right and y0>=65 and y1<=780,('文字越出版心',page.number+1,span['text'])
        for image in page.get_image_info():
            x0,y0,x1,y1=image['bbox'];assert abs((x0+x1)/2-page.rect.width/2)<=1.,'PDF图片未居中'
            positions.append({'页':page.number+1,'边界':list(image['bbox'])})
    assert len(positions)==2
    visual=root/REVIEW/'逐页审阅.json';status='待完成'
    if visual.exists():
        v=read(visual)
        assert v['WordSHA256']==sha(root/OUT)and v['PDFSHA256']==sha(root/PDF)and v['状态']=='通过'and len(v['逐页记录'])==len(pdf),'逐页记录与当前交付不符'
        status='通过'
    result.update(阶段='final',PDFSHA256=sha(root/PDF),PDF页数=len(pdf),排版引擎=pdf.metadata.get('creator'),最终正文及表格回读='通过',图形位置=positions,人工版面审阅=status,状态='通过'if status=='通过'else'待逐页审阅')
    (root/REVIEW/'最终WPS核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result
