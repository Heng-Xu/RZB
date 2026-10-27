"""在10.26反馈原包上局部修订；正文源锚点、原修订、批注和拒绝恢复独立核验。"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile
import argparse, csv, hashlib, json, re, shutil
from lxml import etree as E
from report_summary_restructure import (package, save, serialize, final_view, rows,
    reject_new, signature, zero_center, INDENTS, revision_nodes, revision_identity)
from summary_feedback import ROOT, NS, q, text
from revise_current_discussion import Reviser

BASE = Path('研究报告/甲方反馈/10.26/10.26成果总结.docx')
BASE_SHA = '095b5216557357eff555f5541a1e42d361c6d3e985451ab0f45104ebfd40759b'
SOURCE = Path('研究报告/03_MD/成果总结/成果总结.md')
OUT = Path('研究报告/04_word/10.26成果总结_修订稿.docx')
PDF = OUT.with_suffix('.pdf')
REVIEW = Path('研究报告/05_review/当前版/1026成果总结局部修订')
TABLES = {69:'final_measures',115:'lookup_matrix_0_low',118:'lookup_matrix_2_high'}
FIGURES = ['plan_cost_difference','annual_clr','indicator_correlation_strength',
           'five_parameter_correlation_map','typical_transfer_response']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())


def active(root=ROOT):
    return read(root/'tools/report_policy.json')['summary'].get('mode') == 'feedback_amendment'


def spec(root=ROOT):
    raw=(root/SOURCE).read_text();result=[]
    pattern=r'<!-- (base|after):(\d+)(?::(\d+))? -->\n(.*?)(?=\n\n<!-- |\Z)'
    for mode,index,seq,value in re.findall(pattern,raw,re.S):
        kind='body';value=value.strip()
        for prefix,tag in [('### ','h2'),('## ','h1'),('# ','title')]:
            if value.startswith(prefix):kind=tag;value=value[len(prefix):];break
        if value.startswith('[[KEEP_TABLE:'):kind='table'
        elif value.startswith('[[PICTURE:'):kind='picture'
        elif value.startswith('[[FIG:'):kind='figure'
        elif value.startswith('$$'):kind='equation'
        elif value=='[[DELETE]]':kind='delete';value=''
        elif value=='[[PARAGRAPH_BREAK]]':kind='break';value=''
        elif re.match('^[图表][0-9]+ ',value):kind='caption'
        elif value.startswith('式中，'):kind='symbols'
        result.append(dict(mode=mode,index=int(index),seq=int(seq or 0),text=value,kind=kind))
    assert not re.sub(pattern,'',raw,flags=re.S).strip(),'源稿存在未解析内容'
    assert len({(a['mode'],a['index'],a['seq'])for a in result})==len(result)
    return result


def data(root=ROOT):
    from report_summary import inputs, f
    from case_horizon import through_year
    tables,plans,proof=inputs(root)
    plans={k:through_year(p,2030)for k,p in plans.items()}
    measures=[]
    for r,cn in [('pizhou','邳州'),('city','市区')]:
        for c,lab in [('rigid','刚性'),('elastic_capacity','弹性')]:
            a=plans[r,c]['annual'][-1]
            measures.append([cn,lab,*[f(a[k])for k in ['capacity_mva','storage_nameplate_mw','storage_mwh']],str(a['cumulative_lines'])])
    tables['final_measures']['rows']=measures
    return tables,plans,proof


def extract(root=ROOT):
    from collections import Counter
    parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml'])
    blocks=list(doc.find(q('body')));revs=[];notes=[]
    for i,b in enumerate(blocks):
        for n in revision_nodes(b):
            revs.append({'块':i,'类型':E.QName(n).localname,'ID':n.get(q('id')),
                '作者':n.get(q('author')),'原始日期':n.get(q('date')),
                '文本':''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS))})
    for c in E.fromstring(parts['word/comments.xml']):
        cid=c.get(q('id'));locations=[]
        for i,b in enumerate(blocks):
            if b.xpath('.//w:commentReference[@w:id="'+cid+'"]',namespaces=NS):locations.append(i)
        notes.append({'ID':cid,'作者':c.get(q('author')),'原始日期':c.get(q('date')),
                      '批注':text(c),'引用块':locations})
    result={'基线':str(BASE),'SHA256':sha(root/BASE),'批注':notes,'逐处修订':revs,
            '批注数':len(notes),'修订节点数':len(revs),'修订类型':dict(Counter(r['类型']for r in revs))}
    (root/REVIEW/'甲方批注与修订提取.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    md=['# 10.26成果总结批注及修订提取','',f'原稿只读保留，{len(notes)}条批注、{len(revs)}个修订节点。','']
    for n in notes:md += [f"- 批注{n['ID']}｜{n['作者']}｜{n['原始日期']}｜原引用块{n['引用块']}：{n['批注']}"]
    md += ['', '逐处修订、作者及日期完整列于同名JSON。原有修订不接受、不拒绝，新增修订仅按本轮ID区分。','']
    (root/REVIEW/'甲方批注与修订提取.md').write_text('\n'.join(md))
    return result


def source_check(root=ROOT):
    from report_summary import f, summary_prose_errors
    from check_report_policy import body_policy_errors
    from report_summary_math import latex_key
    assert sha(root/BASE)==BASE_SHA,'甲方基线发生变化'
    (root/REVIEW).mkdir(parents=True,exist_ok=True)
    items=spec(root);raw=(root/SOURCE).read_text();policy=read(root/'tools/report_policy.json')
    errors=body_policy_errors([(str(SOURCE),raw)],{},{},policy['forbidden_body_patterns'])
    errors+=summary_prose_errors(raw,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    assert '2035'not in raw and '两地区刚性方案费用现值合计'not in raw
    assert all(x in raw for x in ['0.40','0.70','0.29','1.7～1.9','1.5～1.7'])
    assert [i['text'][:2]for i in items if i['kind']=='h1']==['一、','二、','三、','四、','五、']
    tables,plans,proof=data(root)
    for r in ['pizhou','city']:
        for c in ['rigid','elastic_capacity']:
            assert f(plans[r,c]['cost_npv_10k'])+'万元'in raw
        for key in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']:
            difference=sum(a[key]for a in plans[r,'rigid']['annual'])-sum(a[key]for a in plans[r,'elastic_capacity']['annual'])
            assert f(abs(difference))+'万元'in raw
    # 公式内容只能从现有报告复用。
    chapter=next((root/'研究报告/03_MD/当前版').glob('04 *.md')).read_text()
    equations=[x['text']for x in items if x['kind']=='equation']
    for eq,tag in zip(equations,['4-10','4-11']):
        original=next(e for e in re.findall(r'\$\$([\s\S]*?)\$\$',chapter)if r'\tag{'+tag+'}'in e)
        assert latex_key(eq)==latex_key(original)
    assert len(equations)==2
    from report_summary_math import inline_segments
    symbols=[x for x in items if x['kind']=='symbols']
    assert [sum(s[0]for s in inline_segments(x['text']))for x in symbols]==[9,6], '两处式中释义须使用15个原生行内符号'
    base=list(final_view(E.fromstring(package(root/BASE)['word/document.xml'])).find(q('body')))
    # 表格原矩阵不改值；本轮配置表仅取同一锁定序列的2030年。
    original=E.fromstring(package(root/BASE)['word/document.xml'])
    for index,key in TABLES.items():
        if index!=69:assert rows(final_view(list(original.find(q('body')))[index]))==[tables[key]['headers']]+tables[key]['rows']
    source=root/'研究报告/数据来源/当前版/1026案例2030同步'
    for row in csv.DictReader((source/'annual_clr.csv').open()):
        assert int(row['年份'])<=2030
        r={'邳州':'pizhou','市区':'city'}[row['地区']];c={'刚性':'rigid','弹性':'elastic_capacity'}[row['方案']]
        a=next(a for a in plans[r,c]['annual']if a['year']==int(row['年份']))
        assert abs(float(row['容载比'])-a['clr'])<1e-9
    figures=[{'图件':name,'SHA256':sha(root/'研究报告/02图表/当前版'/(name+'.png'))}for name in FIGURES]
    result={'状态':'通过','阶段':'source','基线SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),
            '案例终年':2030,'费用评价截止年':2041,'数据核验':proof,'图件复用':figures,'推荐矩阵数':2}
    (root/REVIEW/'源稿核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def amend_text(p,value,revision):
    """保留原格式修订的单一身份，避免字符差分复制其ID。"""
    first=revision.next
    revision.replace(p,value)
    # 新插入文字的格式副本不承载旧历史，否则拒绝插入时会带走旧修订。
    for ins in list(p.xpath('.//w:ins',namespaces=NS)):
        if int(ins.get(q('id'))) < first:continue
        for n in list(revision_nodes(ins)):
            if int(n.get(q('id'))) < first and n.getparent()is not None:n.getparent().remove(n)
    seen=set()
    for n in list(revision_nodes(p)):
        ident=n.get(q('id'))
        if ident in seen:
            assert n.tag in [q('rPrChange'),q('pPrChange'),q('ins'),q('del')]
            assert not n.xpath('.//w:t|.//w:delText',namespaces=NS),'不能删除带正文的重复修订'
            n.getparent().remove(n)
        else:seen.add(ident)


def clean_properties(pr):
    pr=deepcopy(pr)
    for n in list(revision_nodes(pr)):
        if n.getparent()is not None:n.getparent().remove(n)
    return pr


def format_change(p,revision,center=False,keep=False):
    pp=p.find(q('pPr'));old=deepcopy(pp);current=clean_properties(pp)
    p.replace(pp,current)
    if center:zero_center(p)
    if keep:
        e=current.find(q('keepNext'))
        if e is None:e=E.SubElement(current,q('keepNext'))
        e.set(q('val'),'1')
    mark=revision.mark('pPrChange');mark.append(old);current.append(mark)


def paragraph(template,value,kind,revision,root=ROOT):
    p=E.Element(q('p'));pp=clean_properties(template.find(q('pPr')));p.append(pp)
    # 新段落只继承有效格式，不复制旧修订、书签或批注。
    for old in list(pp.findall(q('rPr'))):pp.remove(old)
    for old in list(pp.findall(q('pageBreakBefore'))):pp.remove(old)
    rp=E.SubElement(pp,q('rPr'));rp.append(revision.mark('ins'))
    ins=revision.mark('ins');r=E.SubElement(ins,q('r'));pr=E.SubElement(r,q('rPr'))
    font='方正楷体_GBK'if kind=='h2'else'方正仿宋_GBK'
    E.SubElement(pr,q('rFonts'),{q('ascii'):'Times New Roman',q('hAnsi'):'Times New Roman',q('eastAsia'):font,q('cs'):'Times New Roman'})
    E.SubElement(pr,q('sz'),{q('val'):'24'if kind=='caption'else'32'})
    if kind=='h2':E.SubElement(pr,q('b'))
    from report_summary_math import inline_segments,inline_math
    for is_math,token,plain in inline_segments(value):
        if is_math:ins.append(inline_math(root,token))
        else:
            piece=deepcopy(r);E.SubElement(piece,q('t'),{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=plain;ins.append(piece)
    p.append(ins)
    if kind=='caption':zero_center(p)
    if kind=='symbols':
        for old in list(pp.findall(q('ind'))):pp.remove(old)
        E.SubElement(pp,q('ind'),{q(k):'0'for k in INDENTS})
    return p


def dates(index):
    tz=timezone(timedelta(hours=8))
    if index<107:return(datetime(2026,10,26,18,2,tzinfo=tz)+timedelta(minutes=81*index/106)).isoformat(timespec='seconds')
    return(datetime(2026,10,27,7,23,tzinfo=tz)+timedelta(minutes=60*(index-107)/36)).isoformat(timespec='seconds')


def build(root=ROOT):
    proof=source_check(root);feedback=extract(root);parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml'])
    base=list(doc.find(q('body')));items=spec(root);tables,_,_=data(root);revision=Reviser(doc)
    oldids={n.get(q('id'))for n in revision_nodes(doc)};changes=[];time_map=[];actual=datetime.now(timezone.utc).isoformat()
    newblocks={};new_equations=[]
    for i,b in enumerate(base):
        revision.date=dates(i);first=revision.next
        rule=next((r for r in items if r['index']==i and r['mode']=='base'),None)
        if rule and rule['kind']not in ['table','picture']:
            before=text(b)
            if rule['text']!=before:amend_text(b,rule['text'],revision);changes.append({'块':i,'原文':before,'修改后':rule['text']})
        if i==69:
            for tr,values in zip(b.findall(q('tr')),[tables['final_measures']['headers']]+tables['final_measures']['rows']):
                for cell,value in zip(tr.findall(q('tc')),values):
                    ps=cell.findall(q('p'));assert len(ps)==1;amend_text(ps[0],value,revision)
        if rule and rule['kind']=='picture':
            from discussion_expansion import image_paragraph
            key=re.fullmatch(r'\[\[PICTURE:(.+)\]\]',rule['text'])[1]
            image=image_paragraph(root/'研究报告/02图表/当前版'/(key+'.png'),revision,parts)
            for run in list(b.xpath('.//w:r[w:drawing and not(ancestor::w:del)]',namespaces=NS)):
                parent=run.getparent();at=parent.index(run);parent.remove(run);mark=revision.mark('del');mark.append(run);parent.insert(at,mark)
            for ins in list(image.findall(q('ins'))):b.append(ins)
            format_change(b,revision,center=True,keep=True)
        if i in [55,72]:format_change(b,revision,center=True)
        if i in [27,28]:
            pr=b.find(q('pPr'));rp=pr.find(q('rPr'))
            if rp is None:rp=E.SubElement(pr,q('rPr'))
            rp.append(revision.mark('del'))
        anchor=b
        for item in [x for x in items if x['index']==i and x['mode']=='after']:
            kind=item['kind'];value=item['text']
            if kind=='figure':
                from discussion_expansion import image_paragraph
                key,caption=re.fullmatch(r'\[\[FIG:([^|]+)\|(.+)\]\]',value).groups()
                node=image_paragraph(root/'研究报告/02图表/当前版'/(key+'.png'),revision,parts)
                anchor.addnext(node);anchor=node
                node=paragraph(base[55],caption,'caption',revision,root)
            elif kind=='equation':
                from report_summary_math import equation_table
                node=equation_table(root,value)
                for tr in node.findall(q('tr')):
                    pr=tr.find(q('trPr'));pr.append(revision.mark('ins'))
                new_equations.append(node)
            else:node=paragraph(base[111]if kind=='h2'else base[17],value,kind,revision,root)
            anchor.addnext(node);anchor=node;newblocks[i,item['seq']]=node
        ids=[n.get(q('id'))for n in revision_nodes(doc)if int(n.get(q('id')))>=first and n.get(q('id'))not in oldids]
        if ids:time_map.append({'块':i,'新增修订ID':ids,'显示日期':revision.date})
    # 原有无范围批注补上有效范围；原引用节点及批注部件保留。
    comment_targets={'1':newblocks[26,2],'2':base[70],'3':base[110],'4':newblocks[110,5]}
    for cid,p in comment_targets.items():
        for n in list(doc.xpath('.//w:commentRangeStart[@w:id="'+cid+'"]|.//w:commentRangeEnd[@w:id="'+cid+'"]',namespaces=NS)):n.getparent().remove(n)
        start=E.Element(q('commentRangeStart'),{q('id'):cid});end=E.Element(q('commentRangeEnd'),{q('id'):cid})
        p.insert(1,start);p.append(end)
    settings=E.fromstring(parts['word/settings.xml']);tracking=settings.find(q('trackRevisions'))
    if tracking is None:tracking=E.SubElement(settings,q('trackRevisions'))
    tracking.set(q('val'),'1');parts['word/settings.xml']=serialize(settings);parts['word/document.xml']=serialize(doc)
    save(root/OUT,parts)
    ids=[n.get(q('id'))for n in revision_nodes(doc)if n.get(q('id'))not in oldids]
    manifest={'基线':str(BASE),'基线SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),'WordSHA256':sha(root/OUT),
        '原有修订数':len(oldids),'新增修订ID':ids,'实际操作UTC':actual,'显示时间说明':'用户指定的显示元数据，原有日期不变',
        '时间映射':time_map,'局部文字修改':changes,'原始提取':{'批注数':feedback['批注数'],'修订数':feedback['修订节点数']},
        '图件来源':proof['图件复用'],'批注处理':'原部件字节保留；原范围缺失或位于删除文字中的批注就近锚定有效内容'}
    (root/REVIEW/'局部修订登记.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    docx_check(root)


def amend_inline_math(root=ROOT):
    """仅在当前用户另存稿的两处释义中转换符号，不重建底稿。"""
    from report_summary_math import inline_segments,inline_math
    audit=root/REVIEW/'1027行内公式修正';backup=audit/'修前原件'/OUT
    assert backup.exists()and sha(backup)==sha(root/OUT),'当前增量底稿与备份不一致'
    parts=package(root/OUT);doc=E.fromstring(parts['word/document.xml']);revision=Reviser(doc)
    revision.date='2026-10-27T08:10:00+08:00';oldids={n.get(q('id'))for n in revision_nodes(doc)};changed=[]
    for item in [x for x in spec(root)if x['kind']=='symbols']:
        segments=inline_segments(item['text']);plain=''.join(x[2]for x in segments)
        matches=[p for p in doc.xpath('//w:body/w:p',namespaces=NS)if text(p)==plain]
        assert len(matches)==1,'释义未唯一对应当前稿件'
        p=matches[0];runs=p.xpath('.//w:r[w:t and not(ancestor::w:del)]',namespaces=NS)
        assert len(runs)==1 and text(runs[0])==plain,'释义段落含其他修订，须单独核对'
        run=runs[0];parent=run.getparent();at=parent.index(run);parent.remove(run);nodes=[]
        for is_math,token,value in segments:
            piece=deepcopy(run);piece.find(q('t')).text=value
            if not is_math:nodes.append(piece);continue
            piece.find(q('t')).tag=q('delText');deletion=revision.mark('del');deletion.append(piece)
            insertion=revision.mark('ins');insertion.append(inline_math(root,token));nodes.extend([deletion,insertion])
        for n in nodes:parent.insert(at,n);at+=1
        changed.append({'锚点':f"{item['mode']}:{item['index']}:{item['seq']}",'原文':plain,'源':item['text'],'行内公式数':sum(x[0]for x in segments)})
    # 当前WPS另存会省略部分显式零缩进，补齐原图及图题属性，显示位置保持。
    normalized=[]
    for p in doc.find(q('body')).findall(q('p')):
        if not(p.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(p))):continue
        ind=p.find(q('pPr')).find(q('ind'))
        if all(ind.get(q(k))=='0'for k in INDENTS):continue
        assert all(ind.get(q(k),'0')=='0'for k in INDENTS),'原稿图片段落存在非零缩进'
        format_change(p,revision,center=True);normalized.append(text(p)or'图片段落')
    assert signature(doc)==signature(E.fromstring(parts['word/document.xml'])),'转换行内公式改变了字符内容'
    parts['word/document.xml']=serialize(doc);save(root/OUT,parts)
    ids=[n.get(q('id'))for n in revision_nodes(doc)if n.get(q('id'))not in oldids]
    reg=read(root/REVIEW/'局部修订登记.json')
    reg.update(当前增量底稿=str(backup.relative_to(root)),当前增量底稿SHA256=sha(backup),
        正文源SHA256=sha(root/SOURCE),WordSHA256=sha(root/OUT),新增修订ID=ids,
        增量说明='在用户WPS另存的当前稿上，仅将两处式中解释的15个符号改为原生行内OMML。',
        实际操作UTC=datetime.now(timezone.utc).isoformat(),原有修订数=len(oldids),行内公式修正=changed,零缩进属性补齐=normalized)
    (root/REVIEW/'局部修订登记.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
    (audit/'增量修订登记.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
    docx_check(root)


def docx_check(root=ROOT,path=None):
    from summary_saved_copy import MARKER,verify as verify_saved
    if path is None and(root/MARKER).exists():
        result=verify_saved(root,root/OUT,sha,docx_check)
        (root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        return result
    result=source_check(root);reg=read(root/REVIEW/'局部修订登记.json')
    target=path or root/OUT
    incremental=reg.get('当前增量底稿');old=package(root/(incremental or BASE));new=package(target)
    baseline=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml'])
    ids=set(reg['新增修订ID'])
    if incremental:assert sha(root/incremental)==reg['当前增量底稿SHA256']
    assert reg['WordSHA256']==sha(target)and reg['正文源SHA256']==sha(root/SOURCE)
    oldrevs=revision_nodes(baseline);revs=revision_nodes(doc)
    assert len({n.get(q('id'))for n in revs})==len(revs),'修订ID重复'
    assert {revision_identity(n)for n in oldrevs}<={revision_identity(n)for n in revs},'原有修订身份丢失'
    restored=reject_new(doc,ids)
    assert signature(restored)==signature(baseline),'拒绝本轮未恢复底稿完整内容'
    events=lambda d:{(revision_identity(n),''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for n in revision_nodes(d)}
    assert events(restored)==events(baseline),'原有修订文本未恢复'
    for name,value in old.items():
        allowed=['word/document.xml']if incremental else['word/document.xml','word/settings.xml','word/_rels/document.xml.rels']
        if name not in allowed:assert new[name]==value,'原部件发生非必要变化：'+name
    if incremental:
        before=list(baseline.find(q('body')));after=list(doc.find(q('body')))
        assert len(before)==len(after)
        changed=[(a,b)for a,b in zip(before,after)if E.tostring(a)!=E.tostring(b)]
        explanations=[(a,b)for a,b in changed if text(a).startswith('式中，')]
        assert len(explanations)==2,'两处释义未完整修正'
        for a,b in changed:
            if text(a).startswith('式中，'):continue
            # 其余差异只允许将WPS省略的图段零缩进属性显式写回。
            assert a.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(a))
            ca,cb=deepcopy(a),deepcopy(b)
            ca.remove(ca.find(q('pPr')));cb.remove(cb.find(q('pPr')))
            assert E.tostring(ca)==E.tostring(cb),'图段内容发生额外变化'
        assert signature(doc)==signature(baseline),'符号格式修改改变了正文内容'
    for n in revs:
        if n.get(q('id'))not in ids:continue
        assert n.get(q('author'))=='xh';date=datetime.fromisoformat(n.get(q('date')))
        assert(datetime.fromisoformat('2026-10-26T18:02:00+08:00')<=date<=datetime.fromisoformat('2026-10-26T19:23:00+08:00'))or(datetime.fromisoformat('2026-10-27T07:23:00+08:00')<=date<=datetime.fromisoformat('2026-10-27T08:23:00+08:00'))
    final=final_view(doc);body=final.find(q('body'));tables,_,_=data(root)
    ts=[t for t in body.findall(q('tbl'))if not t.xpath('.//*[local-name()="oMath"]')]
    assert len(ts)==3
    for t,key in zip(ts,TABLES.values()):assert rows(t)==[tables[key]['headers']]+tables[key]['rows']
    assert len(body.xpath('.//w:drawing',namespaces=NS))==len(FIGURES)
    for p in body.findall(q('p')):
        if p.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(p)):
            assert p.find(q('pPr')).find(q('jc')).get(q('val'))=='center'
            assert all(p.find(q('pPr')).find(q('ind')).get(q(k))=='0'for k in INDENTS)
    # 逐公式复用同一原生OMML；不把公式转成图片或纯文字。
    from report_summary_math import reference_math,math_text
    eqs=[t for t in body.findall(q('tbl'))if t.xpath('.//*[local-name()="oMath"]')]
    assert len(eqs)==2
    for i,t in enumerate(eqs,1):assert math_text(t)==math_text(reference_math(root,str(i)))
    from report_summary_math import inline_segments,qm,inline_math
    for item in [s for s in spec(root)if s['kind']=='symbols']:
        segments=inline_segments(item['text']);plain=''.join(x[2]for x in segments)
        matches=[p for p in body.findall(q('p'))if ''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces={**NS,'m':qm('')[1:-1]}))==plain]
        assert len(matches)==1,'释义文字或行内公式不对应源稿'
        maths=matches[0].findall('.//'+qm('oMath'));expected=[s[1]for s in segments if s[0]]
        assert len(maths)==len(expected)
        for m,token in zip(maths,expected):
            assert E.tostring(m,method='c14n',exclusive=True)==E.tostring(inline_math(root,token),method='c14n',exclusive=True),'释义行内公式与源式字形不一致'
    for cid in ['0','1','2','3','4']:
        for tag in ['commentRangeStart','commentRangeEnd']:
            assert len(doc.xpath('.//w:'+tag+'[@w:id="'+cid+'"]',namespaces=NS))==1
            expected_count=len(final_view(baseline).xpath('.//w:'+tag+'[@w:id="'+cid+'"]',namespaces=NS))if incremental else 1
            assert len(final.xpath('.//w:'+tag+'[@w:id="'+cid+'"]',namespaces=NS))==expected_count
        assert len(doc.xpath('.//w:commentReference[@w:id="'+cid+'"]',namespaces=NS))==1
    result.update(阶段='docx',WordSHA256=sha(target),保留原有修订=len(oldrevs),新增修订=len(ids),原批注数=5,
                  拒绝本轮恢复='通过',原批注部件='字节一致',表格逐格及原生公式='通过',式中行内公式数=15)
    if path is None:(root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def final_check(root=ROOT):
    import pymupdf
    result=docx_check(root);pdf=pymupdf.open(root/PDF)
    assert 'wps'in str(pdf.metadata).lower()or'kingsoft'in str(pdf.metadata).lower()
    import unicodedata
    compact=lambda s:re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).replace('−','-').replace('－','-')
    full=compact(''.join(p.get_text()for p in pdf));doc=final_view(E.fromstring(package(root/OUT)['word/document.xml']))
    for p in doc.xpath('//w:body//w:p',namespaces=NS):
        if p.xpath('ancestor::w:tbl[.//*[local-name()="oMath"]]',namespaces=NS):continue
        s=compact(''.join(p.xpath('.//w:t/text()|.//*[local-name()="oMath"]//*[local-name()="t"]/text()',namespaces=NS)))
        if s:assert s in full,'PDF缺少最终文字：'+s[:100]
    assert '2035'not in full,'最终视图残留2035年案例'
    pictures=[]
    for page in pdf:
        for im in page.get_image_info():
            x0,y0,x1,y1=im['bbox'];assert abs((x0+x1)/2-page.rect.width/2)<1
            pictures.append({'页':page.number+1,'边界':list(im['bbox'])})
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if not span['text'].strip():continue
                    x0,y0,x1,y1=span['bbox'];assert x0>=86 and x1<=525 and y0>=65 and y1<=785,('越出版心',page.number+1,span['text'])
    assert len(pictures)==len(FIGURES)
    from report_summary_math import check_pdf
    from io import BytesIO
    checked_parts=package(root/OUT);checked_parts['word/document.xml']=serialize(doc)
    temporary=BytesIO()
    from zipfile import ZIP_DEFLATED
    with ZipFile(temporary,'w',ZIP_DEFLATED)as z:
        for name,value in checked_parts.items():z.writestr(name,value)
    temporary.seek(0)
    formulas=check_pdf(root,temporary,pdf)
    v=root/REVIEW/'逐页审阅.json';status='待逐页审阅'
    if v.exists():
        audit=read(v);assert audit['WordSHA256']==sha(root/OUT)and audit['PDFSHA256']==sha(root/PDF)and audit['状态']=='通过'and len(audit['逐页记录'])==len(pdf)
        status='通过'
    result.update(阶段='final',PDFSHA256=sha(root/PDF),PDF页数=len(pdf),图件位置=pictures,原生公式位置=formulas,
                  人工版面审阅=status,状态='通过'if status=='通过'else'待逐页审阅')
    (root/REVIEW/'最终WPS核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--inline-math',action='store_true',help='在当前成果总结增量修正两处式中行内公式')
    parser.add_argument('--rebuild',action='store_true');parser.add_argument('--stage',choices=['source','docx','final'],default='final')
    parser.add_argument('--accept-wps-pdf',type=Path);args=parser.parse_args(argv);root=args.root.resolve()
    if args.inline_math:amend_inline_math(root);print('两处释义行内公式局部修正完成，待WPS核验');return
    if args.rebuild:build(root);print('10.26成果总结局部修订完成，待WPS核验');return
    if args.accept_wps_pdf:shutil.copy2(args.accept_wps_pdf,root/PDF)
    result={'source':source_check,'docx':docx_check,'final':final_check}[args.stage](root)
    if args.stage=='final'and not args.accept_wps_pdf:assert result['人工版面审阅']=='通过'
    print(json.dumps(result,ensure_ascii=False,indent=2))
