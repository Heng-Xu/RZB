"""验证局部修订保留甲方文字、原修订及拒绝修订后的内容。"""
import unittest
from lxml import etree as E
from revise_current_discussion import Reviser,qn,NS,text,accept_view,reject_xh
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
if __name__=='__main__':unittest.main()
