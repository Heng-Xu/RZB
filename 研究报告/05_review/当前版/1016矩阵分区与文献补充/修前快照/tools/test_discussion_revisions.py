"""验证局部修订保留甲方文字、原修订及拒绝修订后的内容。"""
import unittest
from datetime import date,datetime
from lxml import etree as E
from revise_current_discussion import Reviser,qn,NS,text,accept_view,reject_xh
from adjust_discussion_revision_dates import plan,masked
class LocalRevisionTests(unittest.TestCase):
 def test_keeps_client_words_and_revision(self):
  p=E.Element(qn('p'),nsmap={'w':NS['w']});ins=E.SubElement(p,qn('ins'),{qn('id'):'3',qn('author'):'甲方'})
  E.SubElement(E.SubElement(ins,qn('r')),qn('t')).text='既有转供率为40%，并校核受端余量。'
  Reviser(p).replace(p,'既有转供率为67%，并校核受端余量。')
  self.assertEqual(text(accept_view(p)),'既有转供率为67%，并校核受端余量。')
  self.assertEqual(text(reject_xh(p)),'既有转供率为40%，并校核受端余量。')
  self.assertEqual(ins.get(qn('author')),'甲方')
  self.assertEqual(p.xpath('.//w:delText/text()',namespaces=NS),['40'])
 def test_line_break_does_not_lose_characters(self):
  p=E.Element(qn('p'),nsmap={'w':NS['w']});r=E.SubElement(p,qn('r'));E.SubElement(r,qn('t')).text='主变容量';E.SubElement(r,qn('br'));E.SubElement(r,qn('t')).text='MVA'
  Reviser(p).replace(p,'')
  self.assertEqual(text(reject_xh(p)),'主变容量MVA')
 def test_reject_current_ids_keeps_earlier_xh_revision(self):
  from revise_discussion_selection import reject_ids,revision_nodes
  p=E.Element(qn('p'),nsmap={'w':NS['w']})
  earlier=E.SubElement(p,qn('ins'),{qn('id'):'7',qn('author'):'xh',qn('date'):'2026-10-12T02:00:00Z'})
  E.SubElement(E.SubElement(earlier,qn('r')),qn('t')).text='原转供率40%。'
  revision=Reviser(p);revision.replace(p,'原转供率67%。')
  ids={n.get(qn('id')) for n in revision_nodes(p)}-{'7'}
  restored=reject_ids(p,ids)
  self.assertEqual(text(accept_view(restored)),'原转供率40%。')
  self.assertEqual(restored.xpath('.//w:ins/@w:date',namespaces=NS),['2026-10-12T02:00:00Z'])
 def test_report_copy_preserves_math_and_rejects_only_new_paragraph(self):
  from revise_discussion_report_section import mark_insert
  from revise_discussion_selection import reject_ids,revision_nodes
  root=E.Element(qn('document'),nsmap={'w':NS['w']});body=E.SubElement(root,qn('body'))
  old=E.SubElement(body,qn('p'));history=E.SubElement(old,qn('ins'),{qn('id'):'42',qn('author'):'xh',qn('date'):'2026-10-14T08:00:00Z'})
  E.SubElement(E.SubElement(history,qn('r')),qn('t')).text='既有正文'
  original=E.tostring(old)
  copied=E.Element(qn('p'));m='http://schemas.openxmlformats.org/officeDocument/2006/math'
  math=E.SubElement(copied,'{'+m+'}oMath');E.SubElement(E.SubElement(math,'{'+m+'}r'),'{'+m+'}t').text='x+1'
  body.append(mark_insert(copied,Reviser(root)))
  self.assertEqual(accept_view(root).xpath('.//*[local-name()="oMath"]//*[local-name()="t"]/text()'),['x+1'])
  ids={n.get(qn('id')) for n in revision_nodes(root)}-{'42'}
  rejected=reject_ids(root,ids)
  self.assertEqual(len(rejected.find(qn('body'))),1)
  self.assertEqual(E.tostring(rejected.find(qn('body'))[0]),original)
 def test_dates_keep_content_client_and_paired_changes(self):
  root=E.Element(qn('document'),nsmap={'w':NS['w']});body=E.SubElement(root,qn('body'))
  for i in range(4):
   p=E.SubElement(body,qn('p'))
   for j,kind in enumerate(['del','ins']):
    el=E.SubElement(p,qn(kind),{qn('id'):str(i*2+j),qn('author'):'甲方' if i==0 else 'xh',qn('date'):'2026-10-14T01:00:00Z'})
    E.SubElement(E.SubElement(el,qn('r')),qn('t')).text='保留内容'
  original=E.tostring(root,encoding='UTF-8')
  new,rows,groups=plan(original,'xh',date(2026,10,12),date(2026,10,13),8,20,'Asia/Shanghai',1234)
  self.assertEqual(groups,3);self.assertEqual(len(rows),6)
  self.assertEqual(masked(original,'xh'),masked(new,'xh'))
  self.assertIn(b'w:author="\xe7\x94\xb2\xe6\x96\xb9" w:date="2026-10-14T01:00:00Z"',new)
  for i in range(0,6,2):self.assertEqual(rows[i]['显示时间'],rows[i+1]['显示时间'])
  for row in rows:
   dt=datetime.fromisoformat(row['显示时间']);self.assertIn(dt.date(),[date(2026,10,12),date(2026,10,13)])
   self.assertTrue(8<=dt.hour<20 or (dt.hour==20 and dt.minute==dt.second==0))
   self.assertEqual(dt.utcoffset().total_seconds(),8*3600)
if __name__=='__main__':unittest.main()
