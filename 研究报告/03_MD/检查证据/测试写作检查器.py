"""验证LaTeX、参考文献边界及旧口径检查，避免正文检查被错误绕过。"""
from pathlib import Path
import importlib.util,tempfile,unittest,contextlib,io
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('writing',ROOT/'实验/研究/scripts/check_report_writing_quality.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE='规划参考容载比。2022至2041年增量费用现值。单台主变停运承载代理。样本内一致性检查。'
class WritingChecks(unittest.TestCase):
 def check_text(self,text):
  with tempfile.TemporaryDirectory(dir='/tmp') as d:
   p=Path(d)/'sample.md';p.write_text(text)
   with contextlib.redirect_stdout(io.StringIO()):
    return m.run_check(p,ROOT/'研究报告/终稿/写作与科学表达硬约束.md',None)
 def test_current_basis_passes(self):self.assertTrue(self.check_text(BASE)['passed'])
 def test_latex_identifiers_do_not_trigger(self):
  self.assertTrue(self.check_text(BASE+'\n\\[S_N/P_max\\]\n其中变量说明。\\(C_model\\)单位万元。')['passed'])
 def test_prose_identifiers_still_fail(self):self.assertFalse(self.check_text(BASE+'\n这里出现storage_modules。')['passed'])
 def test_bibliography_does_not_hide_later_chapter(self):
  self.assertFalse(self.check_text(BASE+'\n## 参考文献\n[1] 文献。\n# 第三章 研究对象与数据基础\n这里出现storage_modules。')['passed'])
 def test_old_basis_fails(self):self.assertFalse(self.check_text(BASE+'\n2022—2025年规划期累计在役等年成本。')['passed'])
 def test_evidence_links_do_not_trigger(self):self.assertTrue(self.check_text(BASE+'\n[资料](source_data.csv)。')['passed'])
if __name__=='__main__':unittest.main()
