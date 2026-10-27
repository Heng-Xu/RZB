"""在当前修订稿上局部明确导则名称、衔接费用表述。"""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,shutil
from unittest.mock import patch
from lxml import etree as E
from summary_feedback import ROOT,q,text
from report_summary_amendment import spec,amend_text
from report_summary_amendment import format_change
from report_summary_case_structure import (NS,package,save,serialize,final_view,signature,
 revision_nodes,revision_identity,reject_new,sha,read)
from revise_current_discussion import Reviser
import report_summary_case_detail as previous
import report_summary_amendment as amendment

OUT=Path('研究报告/04_word/10.26成果总结_修订稿.docx');PDF=OUT.with_suffix('.pdf')
SOURCE=Path('研究报告/03_MD/成果总结/成果总结.md')
REVIEW=Path('研究报告/05_review/当前版/1027成果总结第三部分表述修正')
BASE=REVIEW/'修前原件'/OUT;PRIOR_SOURCE=REVIEW/'修前原件'/SOURCE
BASE_SHA='5fe743af870d99e427dbf703a6d11c03a0d4973ece2f2bf9cf81a6d3b89cafce'
CHANGED={54,73,77}

def active(root=ROOT):return read(root/'tools/report_policy.json')['summary'].get('mode')=='case_structure_prose'

def old_spec(root):
    with patch.object(amendment,'SOURCE',PRIOR_SOURCE):return spec(root)

def source_check(root=ROOT):
    assert sha(root/BASE)==BASE_SHA
    old=old_spec(root);new=spec(root)
    assert [(x['mode'],x['index'],x['seq'])for x in old]==[(x['mode'],x['index'],x['seq'])for x in new]
    changed=[]
    for a,b in zip(old,new):
        if a['text']!=b['text']:
            assert a['mode']=='base'and a['index']in CHANGED;changed.append(a['index'])
    assert set(changed)==CHANGED
    raw=(root/SOURCE).read_text();assert '2025年4月《配电网规划设计技术导则（修订稿）》分档' in raw
    assert '两地的源荷、网架和建设时序不同，费用结果分别说明。'not in raw
    from check_report_policy import body_policy_errors
    from report_summary import summary_prose_errors
    policy=read(root/'tools/report_policy.json')
    errors=body_policy_errors([(str(SOURCE),raw)],{},{},policy['forbidden_body_patterns'])+summary_prose_errors(raw,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    result={'状态':'通过','阶段':'source','底稿SHA256':BASE_SHA,'正文源SHA256':sha(root/SOURCE),
            '修改':'明确2025年4月导则修订稿名称；调整费用分析衔接；删除配置表前重复的概括；原数值保持'}
    (root/REVIEW/'源稿核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def build(root=ROOT):
    source_check(root);parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml']);revision=Reviser(doc)
    revision.date='2026-10-27T08:23:00+08:00';oldids={n.get(q('id'))for n in revision_nodes(doc)}
    old={x['index']:x['text']for x in old_spec(root)if x['mode']=='base'};new={x['index']:x['text']for x in spec(root)if x['mode']=='base'}
    # 前两处已产生的修订身份保持，新的表述删除追加在末尾。
    for i in [54,77,73]:
        matches=[p for p in doc.xpath('//w:body/w:p',namespaces=NS)if text(p)==old[i]]
        assert len(matches)==1;amend_text(matches[0],new[i],revision)
    # 导则分档在当前版面被拆到两页，整段保持同页以便比较两地结果。
    p=next(p for p in doc.xpath('//w:body/w:p',namespaces=NS)if text(p)==new[77])
    format_change(p,revision);pr=p.find(q('pPr'));keep=E.Element(q('keepLines'));pr.insert(0,keep)
    parts['word/document.xml']=serialize(doc);save(root/OUT,parts)
    reg={'底稿':str(BASE),'底稿SHA256':BASE_SHA,'WordSHA256':sha(root/OUT),'正文源SHA256':sha(root/SOURCE),
        '新增修订ID':[n.get(q('id'))for n in revision_nodes(doc)if n.get(q('id'))not in oldids],
        '原有修订数':len(oldids),'实际操作UTC':datetime.now(timezone.utc).isoformat(),
        '显示日期':'2026-10-27T08:23:00+08:00，沿用用户指定显示时段','修改锚点':sorted(CHANGED)}
    (root/REVIEW/'局部修订登记.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2));return docx_check(root)

def docx_check(root=ROOT):
    result=source_check(root);reg=read(root/REVIEW/'局部修订登记.json');old=package(root/BASE);new=package(root/OUT)
    before=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml']);ids=set(reg['新增修订ID'])
    assert reg['WordSHA256']==sha(root/OUT)and reg['正文源SHA256']==sha(root/SOURCE)
    a=revision_nodes(before);b=revision_nodes(doc);assert len({n.get(q('id'))for n in b})==len(b)
    assert {revision_identity(n)for n in a}<={revision_identity(n)for n in b}
    restored=reject_new(doc,ids);assert signature(restored)==signature(before)
    events=lambda d:{(revision_identity(n),''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for n in revision_nodes(d)}
    assert events(restored)==events(before)
    for name in old:
        if name!='word/document.xml':assert old[name]==new[name],name
    original=list(before.find(q('body')));updated=list(doc.find(q('body')));assert len(original)==len(updated)
    old={x['index']:x['text']for x in old_spec(root)if x['mode']=='base'};new={x['index']:x['text']for x in spec(root)if x['mode']=='base'}
    observed=[]
    for x,y in zip(original,updated):
        if E.tostring(x,method='c14n')==E.tostring(y,method='c14n'):continue
        hit=[i for i in CHANGED if text(x)==old[i]and text(y)==new[i]]
        assert len(hit)==1,'非目标段落被修改';observed+=hit
    assert set(observed)==CHANGED
    f=final_view(doc);bf=final_view(before)
    for tag in ['drawing','commentRangeStart','commentRangeEnd','commentReference']:
        assert len(f.findall('.//'+q(tag)))==len(bf.findall('.//'+q(tag))),tag
    from summary_saved_copy import math_shape
    assert [math_shape(m)for m in f.xpath('.//m:oMath',namespaces=NS)]==[math_shape(m)for m in bf.xpath('.//m:oMath',namespaces=NS)]
    for n in b:
        if n.get(q('id'))in ids:assert n.get(q('author'))=='xh'and n.get(q('date'))=='2026-10-27T08:23:00+08:00'
    result.update(阶段='docx',WordSHA256=sha(root/OUT),保留原有修订=len(a),新增修订=len(ids),批注数=5,
                  拒绝本轮恢复='通过',其余正文及原批注部件='字节一致',原生公式与图表='保持')
    (root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def final_check(root=ROOT):
    with patch.object(amendment,'REVIEW',REVIEW),patch.object(amendment,'docx_check',docx_check):return amendment.final_check(root)

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--rebuild',action='store_true');parser.add_argument('--stage',choices=['source','docx','final'],default='final');parser.add_argument('--accept-wps-pdf',type=Path)
    a=parser.parse_args(argv);root=a.root.resolve()
    if a.rebuild:print(json.dumps(build(root),ensure_ascii=False));return
    if a.accept_wps_pdf:shutil.copy2(a.accept_wps_pdf,root/PDF)
    result={'source':source_check,'docx':docx_check,'final':final_check}[a.stage](root)
    if a.stage=='final'and not a.accept_wps_pdf:assert result['人工版面审阅']=='通过'
    print(json.dumps(result,ensure_ascii=False,indent=2))
