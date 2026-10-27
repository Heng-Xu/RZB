"""在当前10.26成果总结修订稿上增量细修第三部分。"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,re,shutil
from lxml import etree as E
from report_summary_case_structure import (ROOT,NS,q,text,fulltext,visible,sha,read,package,save,serialize,
 final_view,signature,revision_nodes,revision_identity,reject_new,paragraph,delete_paragraph,amend_text,data,SOURCE,OUT,PDF,REVIEW)
from report_summary_amendment import spec
from revise_current_discussion import Reviser

BASE=REVIEW/'本次细节修前'/OUT
BASE_SHA='4ca5d4115cd1528d42907ce04fd032f3ad1e0db3bdc7220b4dffac5264f85f6a'
PRIOR_SOURCE=REVIEW/'本次细节修前'/SOURCE
REPORT=Path('研究报告/04_word/研究报告终稿.docx')
CHANGED=[63,69,57,58,131,133,135,136,138]
DELETED=[64,70]

def active(root=ROOT):return read(root/'tools/report_policy.json')['summary'].get('mode')=='case_structure_detail'

def prior_spec(root):
    from unittest.mock import patch
    import report_summary_amendment as a
    with patch.object(a,'SOURCE',PRIOR_SOURCE):return spec(root)

def table_from_report(root):
    doc=final_view(E.fromstring(package(root/REPORT)['word/document.xml']))
    tables=[t for t in doc.findall('.//'+q('tbl')) if '饱和期' in fulltext(t)and '较快增长' in fulltext(t)]
    assert len(tables)==1
    table=tables[0];expected=[['负荷增长情况','年最大净负荷平均增长率KP','容载比建议范围'],['饱和期','KP≤2%','1.5～1.7'],['较慢增长','2%＜KP≤4%','1.6～1.8'],['中等增长','4%＜KP≤7%','1.7～1.9'],['较快增长','KP＞7%','1.8～2.0']]
    assert [[fulltext(c)for c in row.findall(q('tc'))]for row in table.findall(q('tr'))]==expected
    return table

def source_check(root=ROOT):
    assert sha(root/BASE)==BASE_SHA
    old=prior_spec(root);new=spec(root);lookup={(x['mode'],x['index'],x['seq']):x for x in new}
    for x in old:
        k=(x['mode'],x['index'],x['seq'])
        if x['mode']=='base'and x['index']in DELETED:assert k not in lookup;continue
        if x['mode']=='base'and x['index']in CHANGED:continue
        assert k in lookup and lookup[k]['text']==x['text'],'非授权正文改动: '+str(k)
    assert set(lookup)-{(x['mode'],x['index'],x['seq'])for x in old}=={('after',76,1),('after',76,2)}
    assert lookup['after',76,2]['text']=='[[GUIDELINE_TABLE]]'
    from check_report_policy import body_policy_errors
    from report_summary import summary_prose_errors,f
    raw=(root/SOURCE).read_text();policy=read(root/'tools/report_policy.json')
    errors=body_policy_errors([(str(SOURCE),raw)],{},{},policy['forbidden_body_patterns'])+summary_prose_errors(raw,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    _,plans,proof=data(root)
    for r in ['pizhou','city']:
        for case in ['rigid','elastic_capacity']:assert f(plans[r,case]['cost_npv_10k'])+'万元'in raw
    assert '2035'not in raw
    table_from_report(root)
    result={'状态':'通过','阶段':'source','底稿SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),
     '复用导则表':'研究报告5.4.3；引用2025年4月《配电网规划设计技术导则（修订稿）》',
     '范围':'合并供电能力短段，去除费用分析分点，插入原有导则表并顺延表号','数据核验':proof}
    (root/REVIEW/'细节源稿核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def build(root=ROOT):
    source_check(root);parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml']);revision=Reviser(doc)
    revision.date='2026-10-27T08:22:00+08:00';oldids={n.get(q('id'))for n in revision_nodes(doc)}
    old=prior_spec(root);new=spec(root);before={x['index']:x['text']for x in old if x['mode']=='base'};after={x['index']:x['text']for x in new if x['mode']=='base'}
    blocks=list(doc.find(q('body')))
    def target(value):
        found=[p for p in blocks if p.tag==q('p')and text(p)==value]
        assert len(found)==1,(value[:60],len(found));return found[0]
    for index in CHANGED:amend_text(target(before[index]),after[index],revision)
    for index in DELETED:delete_paragraph(target(before[index]),revision)
    at=target(before[76]);caption=next(x['text']for x in new if x['mode']=='after'and x['index']==76 and x['seq']==1)
    title=paragraph(at,caption,'caption',revision,root);at.addnext(title)
    table=deepcopy(table_from_report(root))
    for n in list(revision_nodes(table)):
        if n.getparent()is not None:n.getparent().remove(n)
    # 表内容、行列与研究报告一致；使用总结原有表格样式。
    target_style=next(t for t in blocks if t.tag==q('tbl')and '累计新增联络' in text(t)).find('./'+q('tblPr')+'/'+q('tblStyle'))
    source_style=table.find('./'+q('tblPr')+'/'+q('tblStyle'))
    if source_style is not None and target_style is not None:source_style.set(q('val'),target_style.get(q('val')))
    # 研究报告原表为9磅，按成果总结表格字号放大以便阅读。
    for run in table.findall('.//'+q('r')):
        pr=run.find(q('rPr'))
        if pr is None:pr=E.Element(q('rPr'));run.insert(0,pr)
        for tag in ['sz','szCs']:
            node=pr.find(q(tag))
            if node is None:node=E.SubElement(pr,q(tag))
            node.set(q('val'),'24')
    for row in table.findall(q('tr')):
        pr=row.find(q('trPr'))
        if pr is None:pr=E.Element(q('trPr'));row.insert(0,pr)
        pr.append(revision.mark('ins'))
    title.addnext(table)
    parts['word/document.xml']=serialize(doc);save(root/OUT,parts)
    reg={'底稿':str(BASE),'底稿SHA256':BASE_SHA,'WordSHA256':sha(root/OUT),'正文源SHA256':sha(root/SOURCE),
     '新增修订ID':[n.get(q('id'))for n in revision_nodes(doc)if n.get(q('id'))not in oldids],
     '原有修订节点':len(oldids),'实际操作UTC':datetime.now(timezone.utc).isoformat(),
     '显示时间':'2026-10-27T08:22:00+08:00（用户指定的修订显示时段）','导则表来源':str(REPORT),'导则表来源SHA256':sha(root/REPORT)}
    (root/REVIEW/'细节修订登记.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));return docx_check(root)

def docx_check(root=ROOT):
    result=source_check(root);reg=read(root/REVIEW/'细节修订登记.json');old=package(root/BASE);new=package(root/OUT)
    before=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml']);ids=set(reg['新增修订ID'])
    assert sha(root/OUT)==reg['WordSHA256']and sha(root/SOURCE)==reg['正文源SHA256']
    oldrevs=revision_nodes(before);newrevs=revision_nodes(doc)
    assert len({n.get(q('id'))for n in newrevs})==len(newrevs)
    assert {revision_identity(n)for n in oldrevs}<={revision_identity(n)for n in newrevs}
    restored=reject_new(doc,ids);assert signature(restored)==signature(before)
    events=lambda d:{(revision_identity(n),''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for n in revision_nodes(d)}
    assert events(restored)==events(before)
    # 字符级修订可能拆分run；未涉及段落仍须逐块字节一致。
    protected={x['text']for x in prior_spec(root)if x['mode']=='base'and x['index']in CHANGED+DELETED}
    oldblocks=list(before.find(q('body')));restoredblocks=list(restored.find(q('body')))
    assert len(oldblocks)==len(restoredblocks)
    for x,y in zip(oldblocks,restoredblocks):
        if text(x)not in protected:assert E.tostring(x,method='c14n')==E.tostring(y,method='c14n'),'无关原块变化'
    for name in old:
        if name!='word/document.xml':assert old[name]==new[name],name
    f=final_view(doc);fb=[b for b in f.find(q('body'))if visible(b)];base=E.fromstring(package(root/'研究报告/甲方反馈/10.27/10.27成果总结.docx')['word/document.xml']);baseblocks=list(base.find(q('body')))
    expected=[]
    for item in spec(root):
        value=item['text']
        if value.startswith('[[NATIVE_'):
            b=final_view(baseblocks[item['index']]);expected.append((E.QName(b).localname,fulltext(b)))
        elif value=='[[GUIDELINE_TABLE]]':expected.append(('tbl',fulltext(table_from_report(root))))
        else:
            if item['kind']=='symbols':
                from report_summary_math import inline_segments
                value=''.join(s[2]for s in inline_segments(value))
            expected.append(('p',value))
    assert [(E.QName(b).localname,fulltext(b))for b in fb]==expected,'正文源与Word最终视图不一致'
    for tag in ['drawing','commentRangeStart','commentRangeEnd','commentReference']:
        assert len(f.findall('.//'+q(tag)))==len(final_view(before).findall('.//'+q(tag))),tag
    from summary_saved_copy import math_shape
    oldmath=final_view(before).xpath('.//m:oMath',namespaces=NS);newmath=f.xpath('.//m:oMath',namespaces=NS)
    assert [math_shape(m)for m in oldmath]==[math_shape(m)for m in newmath],'原有公式内容变化'
    from report_summary_restructure import INDENTS
    for p in f.xpath('//w:body/w:p',namespaces=NS):
        if p.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(p)):
            pp=p.find(q('pPr'));assert pp.find(q('jc')).get(q('val'))=='center'
            assert all(pp.find(q('ind')).get(q(k))=='0'for k in INDENTS)
    for n in newrevs:
        if n.get(q('id'))in ids:assert n.get(q('author'))=='xh'and n.get(q('date'))=='2026-10-27T08:22:00+08:00'
    result.update(阶段='docx',WordSHA256=sha(root/OUT),原有修订=len(oldrevs),新增修订=len(ids),批注=5,拒绝本轮恢复='通过',导则表='逐格与研究报告一致')
    (root/REVIEW/'细节Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def final_check(root=ROOT):
    import report_summary_amendment as a
    from unittest.mock import patch
    with patch.object(a,'REVIEW',REVIEW),patch.object(a,'docx_check',docx_check):return a.final_check(root)

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--rebuild',action='store_true');parser.add_argument('--stage',choices=['source','docx','final'],default='final');parser.add_argument('--accept-wps-pdf',type=Path)
    args=parser.parse_args(argv);root=args.root.resolve()
    if args.rebuild:print(json.dumps(build(root),ensure_ascii=False));return
    if args.accept_wps_pdf:shutil.copy2(args.accept_wps_pdf,root/PDF)
    r={'source':source_check,'docx':docx_check,'final':final_check}[args.stage](root)
    if args.stage=='final'and not args.accept_wps_pdf:assert r['人工版面审阅']=='通过'
    print(json.dumps(r,ensure_ascii=False,indent=2))
