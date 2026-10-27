"""用户WPS另存后的总结：核对真实原件、全文、数学结构、图件与批注。"""
from copy import deepcopy
from pathlib import Path
import json,re
from lxml import etree as E
from report_summary_restructure import package,final_view,signature,revision_nodes
from report_summary_math import qm
from summary_feedback import q,NS,text

MARKER=Path('研究报告/05_review/当前版/1026成果总结局部修订/1027行内公式修正/用户另存衔接.json')


def math_shape(math):
    """允许等义的数学run合并及空属性序列化，保留运算结构和非空数学属性。"""
    def walk(n):
        if n.tag in [q('rPr'),qm('rPr')]:return []
        if n.tag==qm('r'):
            val=lambda p,default='':p.get(qm('val'),default)if p is not None else default
            style=val(n.find('./'+qm('rPr')+'/'+qm('sty')))
            script=val(n.find('./'+qm('rPr')+'/'+qm('scr')))
            italic=n.find('./'+q('rPr')+'/'+q('i'))
            italic=(italic.get(q('val'),'1')if italic is not None else '')if not script else ''
            return [('字符',c,style,script,italic)for t in n.iter(qm('t'))for c in(t.text or '')]
        if n.tag==qm('t'):return [('字符',c)for c in(n.text or '')]
        children=[v for c in n for v in walk(c)]
        if E.QName(n).localname.endswith('Pr')and not children and not n.attrib:return []
        return [(n.tag,tuple(sorted(n.attrib.items())),tuple(children))]
    return walk(math)


def verify(root,current,sha,reference_check):
    marker=json.loads((root/MARKER).read_text());reference=root/marker['已核验交付原件']
    assert sha(reference)==marker['交付原件SHA256']
    assert sha(current)==marker['用户另存SHA256'],'用户另存稿变化后须重新核对'
    result=reference_check(root,reference)
    before,after=package(reference),package(current)
    a,b=(E.fromstring(p['word/document.xml'])for p in[before,after])
    assert signature(a)==signature(b),'用户另存稿改变了最终正文或表格'
    allowed={'word/document.xml','word/settings.xml','word/fontTable.xml','docProps/app.xml','docProps/core.xml'}
    for name,value in before.items():
        if name.endswith('/')or name in allowed:continue
        assert after[name]==value,'另存影响了未登记的包部件：'+name
    af,bf=final_view(a),final_view(b)
    am,bm=(d.findall('.//'+qm('oMath'))for d in[af,bf])
    assert len(am)==len(bm)==17,'两条独立公式与15个行内对象数量不符'
    assert [math_shape(m)for m in am]==[math_shape(m)for m in bm],'另存稿数学结构或符号改变'
    for m in bm:
        for run in m.iter(qm('r')):
            fonts=run.find('./'+q('rPr')+'/'+q('rFonts'))
            assert fonts is not None and fonts.get(q('ascii'))=='Times New Roman'
    for p in bf.find(q('body')).findall(q('p')):
        if p.xpath('.//w:drawing',namespaces=NS)or re.match(r'^图[0-9]+ ',text(p)):
            pr=p.find(q('pPr'));ind=pr.find(q('ind'))
            assert pr.find(q('jc')).get(q('val'))=='center'
            assert all(value=='0'for value in ind.attrib.values()),'另存稿图片存在非零缩进'
    for ident in ['0','1','2','3','4']:
        for tag in ['commentRangeStart','commentRangeEnd','commentReference']:
            assert len(b.xpath('.//w:'+tag+'[@w:id="'+ident+'"]',namespaces=NS))==1
    assert sha(current)==marker['用户另存SHA256'],'核对过程不得改写用户稿件'
    result.update(WordSHA256=sha(current),用户另存衔接='全文、数学结构、原媒体和批注部件核对通过',
        当前已有修订节点=len(revision_nodes(b)),代理新增修订=0,
        保留原有修订说明='原交付的修订保留与拒绝恢复在不可变交付原件验证；用户WPS另存后的修订重排按当前字节保留。')
    return result
