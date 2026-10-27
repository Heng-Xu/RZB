"""成果总结修订的恢复核验，以及WPS数学段落删除的结构回归。"""
from copy import deepcopy
from lxml import etree as E
from revise_current_discussion import Reviser
from report_summary_restructure import q,NS,revision_nodes,reject_new,text,delete_table,final_view,format_paragraph

def document():
    doc=E.Element(q('document'),nsmap={'w':NS['w']});body=E.SubElement(doc,q('body'))
    return doc,body

def test_amending_client_insertion_keeps_history_and_restores_format():
    doc,body=document();p=E.SubElement(body,q('p'))
    ins=E.SubElement(p,q('ins'),{q('id'):'8',q('author'):'甲方',q('date'):'2026-10-23T11:00:00Z'})
    r=E.SubElement(ins,q('r'));pr=E.SubElement(r,q('rPr'));E.SubElement(pr,q('b'));E.SubElement(r,q('t')).text='既有转供率40%，受端余量已校核。'
    before=deepcopy(doc);rev=Reviser(doc);rev.replace(p,'既有转供率60%，受端余量已校核。')
    format_paragraph(p,text(p),'body',rev)
    ids={n.get(q('id'))for n in revision_nodes(doc)}-{'8'}
    restored=reject_new(doc,ids)
    assert text(restored)==text(before)
    assert restored.xpath('.//w:ins/@w:author',namespaces=NS)==['甲方']
    assert all(r.find('./'+q('rPr')+'/'+q('b'))is not None for r in restored.xpath('.//w:ins/w:r',namespaces=NS))

def test_equation_deletion_wraps_math_inside_math_paragraph():
    doc,body=document();tbl=E.SubElement(body,q('tbl'));row=E.SubElement(tbl,q('tr'));cell=E.SubElement(row,q('tc'));p=E.SubElement(cell,q('p'))
    m='http://schemas.openxmlformats.org/officeDocument/2006/math';mq=lambda n:'{'+m+'}'+n
    para=E.SubElement(p,mq('oMathPara'));math=E.SubElement(para,mq('oMath'));run=E.SubElement(math,mq('r'));E.SubElement(run,mq('t')).text='x'
    original=E.tostring(math);rev=Reviser(doc);delete_table(tbl,rev)
    assert para.find('./'+q('del')+'/'+mq('oMath'))is not None
    assert not final_view(doc).xpath('.//*[local-name()="oMath"]')
    ids={n.get(q('id'))for n in revision_nodes(doc)}
    restored=reject_new(doc,ids)
    assert E.tostring(restored.xpath('.//*[local-name()="oMath"]')[0])==original


def test_rejecting_amendment_keeps_client_format_history():
    from report_summary_amendment import amend_text
    doc,body=document();p=E.SubElement(body,q('p'));r=E.SubElement(p,q('r'))
    pr=E.SubElement(r,q('rPr'));change=E.SubElement(pr,q('rPrChange'),
        {q('id'):'9',q('author'):'甲方',q('date'):'2026-10-26T11:00:00Z'})
    E.SubElement(change,q('rPr'));E.SubElement(r,q('t')).text='2035年配置，原有技术说明。'
    before=deepcopy(doc);revision=Reviser(doc);amend_text(p,'2030年配置，原有技术说明。',revision)
    assert len({n.get(q('id'))for n in revision_nodes(doc)})==len(revision_nodes(doc))
    ids={n.get(q('id'))for n in revision_nodes(doc)}-{'9'}
    restored=reject_new(doc,ids)
    assert text(restored)==text(before)
    assert restored.xpath('.//w:rPrChange/@w:id',namespaces=NS)==['9']


def test_horizon_extraction_preserves_locked_plan_and_common_valuation():
    from case_horizon import through_year
    original={'annual':[{'year':2030,'added_lifecycle_npv_10k':8.,'cumulative_lifecycle_npv_10k':8.},
                        {'year':2035,'added_lifecycle_npv_10k':3.,'cumulative_lifecycle_npv_10k':11.}],
              'cost_npv_10k':11.,'evaluation_end_year':2041}
    result=through_year(original,2030)
    assert result['cost_npv_10k']==8. and result['evaluation_end_year']==2041
    result['annual'][0]['year']=2029
    assert original['annual'][0]['year']==2030 and original['cost_npv_10k']==11.


def test_saved_math_accepts_equal_runs_but_preserves_subscript():
    from summary_saved_copy import math_shape
    from report_summary_math import qm
    def symbol(split=False,subscript=True):
        m=E.Element(qm('oMath'));parent=m
        if subscript:
            s=E.SubElement(m,qm('sSub'));base=E.SubElement(s,qm('e'))
            r=E.SubElement(base,qm('r'));E.SubElement(r,qm('t')).text='C'
            parent=E.SubElement(s,qm('sub'))
        for value in list('plan')if split else['plan']:
            r=E.SubElement(parent,qm('r'));E.SubElement(r,qm('t')).text=value
        return m
    assert math_shape(symbol(True))==math_shape(symbol())
    assert math_shape(symbol())!=math_shape(symbol(subscript=False))


def test_saved_math_does_not_hide_loss_of_calligraphic_symbol():
    from summary_saved_copy import math_shape
    from report_summary_math import qm
    a=E.Element(qm('oMath'));r=E.SubElement(a,qm('r'));pr=E.SubElement(r,qm('rPr'))
    E.SubElement(pr,qm('scr'),{qm('val'):'script'});E.SubElement(r,qm('t')).text='E'
    b=deepcopy(a);b.find('.//'+qm('scr')).getparent().remove(b.find('.//'+qm('scr')))
    assert math_shape(a)!=math_shape(b)
