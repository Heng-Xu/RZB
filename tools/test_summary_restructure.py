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
