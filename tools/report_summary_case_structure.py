"""以10.27甲方原件为基线，仅重排成果总结第三部分，拒绝新增修订可恢复。"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse, json, re, shutil, unicodedata
from lxml import etree as E
from report_summary_restructure import (package, save, serialize, final_view, signature,
    revision_nodes, revision_identity, reject_new, delete_table, rows, INDENTS)
from report_summary_amendment import amend_text, format_change, paragraph, spec, sha, read, data
from revise_current_discussion import Reviser
from summary_feedback import ROOT, NS, q, text
NS={**NS,'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}

BASE=Path('研究报告/甲方反馈/10.27/10.27成果总结.docx')
BASE_SHA='853c5e453ec9228dd64c7a2ed5f3997c78618af67e69fd9b07e1021078ce8763'
SOURCE=Path('研究报告/03_MD/成果总结/成果总结.md')
OUT=Path('研究报告/04_word/10.26成果总结_修订稿.docx');PDF=OUT.with_suffix('.pdf')
REVIEW=Path('研究报告/05_review/当前版/1027成果总结第三部分重排')
MOVED=[63,64,69,70,73,74,75]
HEADS=['（一）两地区刚性、弹性方案均满足供电能力要求',
       '（二）以主变增容替代部分中压联络与储能',
       '（三）与导则容载比推荐值的比较']
SAFETY='2022—2030年，邳州和市区的刚性、弹性方案均满足模型规定的正常运行和主变N-1供电能力要求。'
fulltext=lambda b:''.join(b.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))

def active(root=ROOT):
    return read(root/'tools/report_policy.json')['summary'].get('mode')=='case_structure'

def visible(b):
    f=final_view(b)
    return bool(fulltext(f)or f.xpath('.//w:drawing',namespaces=NS))

def source_check(root=ROOT):
    assert sha(root/BASE)==BASE_SHA,'甲方原件发生变化'
    items=spec(root);doc=E.fromstring(package(root/BASE)['word/document.xml'])
    blocks=list(doc.find(q('body')));actual=[i['text']for i in items if i['kind']=='h2'and i['text']in HEADS]
    assert actual==HEADS,'第三部分须按供电能力、工程替代和经济性、导则比较组织'
    assert next(i['text']for i in items if i['index']==53 and i['mode']=='after'and i['seq']==1)==SAFETY
    for item in items:
        if item['mode']=='after'or item['index']==53:continue
        value=item['text'];b=final_view(blocks[item['index']])
        if value.startswith('[[NATIVE_'):continue
        if item['kind']=='symbols':
            from report_summary_math import inline_segments
            value=''.join(s[2]for s in inline_segments(value))
        assert value==fulltext(b),'第三部分以外或原有正文有额外改写：'+str(item['index'])
    assert {i['index']for i in items if i['mode']=='base'}=={i for i,b in enumerate(blocks)if visible(b)}-{62}
    from check_report_policy import body_policy_errors
    from report_summary import summary_prose_errors,f
    policy=read(root/'tools/report_policy.json');raw=(root/SOURCE).read_text()
    errors=body_policy_errors([(str(SOURCE),raw)],{},{},policy['forbidden_body_patterns'])
    errors+=summary_prose_errors(raw,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    assert '2035'not in raw
    tables,plans,proof=data(root)
    for r in ['pizhou','city']:
        for c in ['rigid','elastic_capacity']:assert f(plans[r,c]['cost_npv_10k'])+'万元'in raw
    assert rows(final_view(blocks[75]))==[tables['final_measures']['headers']]+tables['final_measures']['rows']
    result={'状态':'通过','阶段':'source','基线':str(BASE),'基线SHA256':BASE_SHA,
        '正文源SHA256':sha(root/SOURCE),'案例终年':2030,'费用评价截止年':2041,
        '修改范围':'仅第三部分结构重排、三个小标题和一句供电能力概括；原有数值、图表、其余正文保持',
        '数据核验':proof,'文字复核':'逐段核对；保留区县费用差异，不概括两地费用均下降'}
    (root/REVIEW/'源稿核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def insert_clone(block,revision):
    node=final_view(block)
    for n in list(revision_nodes(node)):
        if n.getparent()is not None:n.getparent().remove(n)
    assert not node.xpath('.//w:commentRangeStart|.//w:commentRangeEnd|.//w:commentReference',namespaces=NS)
    if node.tag==q('tbl'):
        for row in node.findall(q('tr')):
            pr=row.find(q('trPr'))
            if pr is None:pr=E.Element(q('trPr'));row.insert(0,pr)
            pr.append(revision.mark('ins'))
    else:
        pp=node.find(q('pPr'));rp=pp.find(q('rPr'))
        if rp is None:rp=E.SubElement(pp,q('rPr'))
        rp.append(revision.mark('ins'));ins=revision.mark('ins')
        for child in list(node):
            if child is not pp:node.remove(child);ins.append(child)
        node.append(ins)
    return node

def delete_paragraph(p,revision):
    amend_text(p,'',revision);format_change(p,revision)
    pp=p.find(q('pPr'));rp=pp.find(q('rPr'))
    if rp is None:rp=E.SubElement(pp,q('rPr'))
    rp.append(revision.mark('del'))

def build(root=ROOT):
    source_check(root);parts=package(root/BASE);doc=E.fromstring(parts['word/document.xml'])
    base=list(doc.find(q('body')));revision=Reviser(doc);revision.date='2026-10-27T08:20:00+08:00'
    oldids={n.get(q('id'))for n in revision_nodes(doc)}
    amend_text(base[53],HEADS[0],revision)
    anchor=base[53]
    additions=[paragraph(base[54],SAFETY,'body',revision,root)]
    additions += [insert_clone(base[i],revision)for i in MOVED]
    additions += [paragraph(base[53],HEADS[1],'h2',revision,root)]
    for n in additions:anchor.addnext(n);anchor=n
    for i in [62]+MOVED:
        if base[i].tag==q('tbl'):delete_table(base[i],revision)
        else:delete_paragraph(base[i],revision)
    base[75].addnext(paragraph(base[53],HEADS[2],'h2',revision,root))
    # WPS另存会省略等效为零的属性；显式补齐，保持原显示位置。
    normalized=[]
    for b in list(doc.find(q('body'))):
        f=final_view(b)
        if b.tag==q('p')and(f.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(f))):
            targets=[b]
        elif b.tag==q('tbl')and f.xpath('.//m:oMath',namespaces=NS):targets=b.findall('.//'+q('p'))
        else:continue
        for p in targets:
            ind=p.find(q('pPr')).find(q('ind'))
            assert all(ind.get(q(k),'0')=='0'for k in INDENTS)
            if all(ind.get(q(k))=='0'for k in INDENTS):continue
            format_change(p,revision);pr=p.find(q('pPr'));pr.remove(pr.find(q('ind')))
            E.SubElement(pr,q('ind'),{q(k):'0'for k in INDENTS});normalized.append(text(p)or'图件/公式段落')
    parts['word/document.xml']=serialize(doc)
    settings=E.fromstring(parts['word/settings.xml']);t=settings.find(q('trackRevisions'))
    if t is None:t=E.SubElement(settings,q('trackRevisions'))
    t.set(q('val'),'1');parts['word/settings.xml']=serialize(settings);save(root/OUT,parts)
    reg={'基线':str(BASE),'基线SHA256':BASE_SHA,'WordSHA256':sha(root/OUT),
        '正文源SHA256':sha(root/SOURCE),'新增修订ID':[n.get(q('id'))for n in revision_nodes(doc)if n.get(q('id'))not in oldids],
        '原有修订数':len(oldids),'移动原块':MOVED,'实际操作UTC':datetime.now(timezone.utc).isoformat(),
        '零缩进属性补齐':normalized,
        '显示日期':'2026-10-27T08:20:00+08:00，沿用用户指定时段；非实际操作时间',
        '修订方式':'原位置标记删除，新位置标记插入；原有修订完整保留，可拒绝本轮恢复'}
    (root/REVIEW/'局部修订登记.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
    comments=E.fromstring(parts['word/comments.xml'])
    notes=[{'ID':c.get(q('id')),'作者':c.get(q('author')),'日期':c.get(q('date')),'内容':text(c)}for c in comments]
    (root/REVIEW/'甲方批注提取.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2))
    return docx_check(root)

def docx_check(root=ROOT):
    result=source_check(root);reg=read(root/REVIEW/'局部修订登记.json')
    old=package(root/BASE);new=package(root/OUT);base=E.fromstring(old['word/document.xml']);doc=E.fromstring(new['word/document.xml'])
    assert reg['WordSHA256']==sha(root/OUT)and reg['正文源SHA256']==sha(root/SOURCE)
    ids=set(reg['新增修订ID']);revs=revision_nodes(doc);oldrevs=revision_nodes(base)
    assert len({n.get(q('id'))for n in revs})==len(revs),'修订ID重复'
    assert {revision_identity(n)for n in oldrevs}<={revision_identity(n)for n in revs}
    restored=reject_new(doc,ids)
    assert signature(restored)==signature(base),'拒绝本轮未恢复原件'
    events=lambda d:{(revision_identity(n),''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)))for n in revision_nodes(d)}
    assert events(restored)==events(base),'拒绝后原有修订文本变化'
    for name,value in old.items():
        if name not in ['word/document.xml','word/settings.xml']:assert new[name]==value,name
    before=list(base.find(q('body')));after=list(reject_new(doc,ids).find(q('body')))
    restored_blocks={E.tostring(a,method='c14n')for a in after}
    for b in before[:53]+before[76:]:
        assert E.tostring(b,method='c14n')in restored_blocks,'无关原块被改动'
    fdoc=final_view(doc);fb=list(fdoc.find(q('body')));items=spec(root)
    expected=[]
    for item in items:
        value=item['text']
        if value.startswith('[[NATIVE_'):
            b=before[item['index']];expected.append((E.QName(b).localname,fulltext(final_view(b))))
        else:
            if item['kind']=='symbols':
                from report_summary_math import inline_segments
                value=''.join(s[2]for s in inline_segments(value))
            expected.append(('p',value))
    assert [(E.QName(b).localname,fulltext(b))for b in fb if visible(b)]==expected,'Word最终顺序未对应源稿'
    for tag in ['drawing','commentRangeStart','commentRangeEnd','commentReference']:
        assert len(fdoc.findall('.//'+q(tag)))==len(final_view(base).findall('.//'+q(tag))),tag
    for p in fb:
        if p.tag==q('p')and(p.xpath('.//w:drawing',namespaces=NS)or re.match('^图[0-9]+ ',text(p))):
            pp=p.find(q('pPr'));assert pp.find(q('jc')).get(q('val'))=='center'
            assert all(pp.find(q('ind')).get(q(k))=='0'for k in INDENTS)
    assert fdoc.xpath('count(.//m:oMath)',namespaces=NS)==final_view(base).xpath('count(.//m:oMath)',namespaces=NS)
    result.update(阶段='docx',WordSHA256=sha(root/OUT),保留原有修订=len(oldrevs),新增修订=len(ids),
        拒绝本轮恢复='通过',原批注数=5,原批注及媒体部件='字节一致',其余正文原块='仅补全图及公式段落零缩进，拒绝本轮后字节一致')
    (root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result

def final_check(root=ROOT):
    # 复用原生公式几何和WPS逐段/图件核验，独立使用本轮源及Word核验。
    import report_summary_amendment as a
    from unittest.mock import patch
    with patch.object(a,'REVIEW',REVIEW),patch.object(a,'docx_check',docx_check):
        return a.final_check(root)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--rebuild',action='store_true');parser.add_argument('--stage',choices=['source','docx','final'],default='final')
    parser.add_argument('--accept-wps-pdf',type=Path);args=parser.parse_args(argv);root=args.root.resolve()
    if args.rebuild:print(json.dumps(build(root),ensure_ascii=False));return
    if args.accept_wps_pdf:shutil.copy2(args.accept_wps_pdf,root/PDF)
    result={'source':source_check,'docx':docx_check,'final':final_check}[args.stage](root)
    if args.stage=='final'and not args.accept_wps_pdf:assert result['人工版面审阅']=='通过'
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
