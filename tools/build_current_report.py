"""当前六章报告唯一维护入口；默认核验，--rebuild 明确重建。"""
from pathlib import Path
import argparse, shutil, subprocess, sys, hashlib, json

ROOT=Path(__file__).resolve().parents[1]

def run(script,root):
 subprocess.run([sys.executable,str(root/'研究报告/05_review/当前版'/script)],cwd=root,check=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--discussion',action='store_true',help='维护当前讨论稿；以终稿DOCX为内容依据')
 parser.add_argument('--root',type=Path,default=ROOT,help='完整项目副本的根目录，可用于试构建')
 parser.add_argument('--rebuild',action='store_true',help='修改六章源后装配原生Word，随后须用WPS导出PDF并接收')
 parser.add_argument('--pdf-only',action='store_true',help='旧选项；现须从WPS原生导出PDF')
 parser.add_argument('--check-only',action='store_true',help='仅核验；不重建 Word 或 PDF')
 parser.add_argument('--docx-only',action='store_true',help='装配原生DOCX，供WPS打开导出；完成导出后使用--accept-wps-pdf')
 parser.add_argument('--accept-wps-pdf',type=Path,help='接收由当前原生DOCX在WPS中直接导出的PDF，并同步目录缓存')
 args=parser.parse_args();root=args.root.resolve()
 if args.discussion:
  script=root/'tools/build_discussion_brief.py'
  if args.rebuild:
   subprocess.run([sys.executable,str(script),'--root',str(root)],check=True)
  subprocess.run([sys.executable,str(script),'--root',str(root),'--check'],check=True)
  return
 if args.docx_only or args.rebuild:
  if args.pdf_only or args.check_only or args.accept_wps_pdf:parser.error('--docx-only/--rebuild须单独使用')
  run('装配Word.py',root)
  print('原生DOCX已装配。请在WPS重新打开并导出PDF，再用--accept-wps-pdf接收。')
  return
 if args.pdf_only:
  parser.error('正式PDF已改为WPS从原生DOCX直接导出；导出后使用--accept-wps-pdf。旧图像公式副本只供历史复查。')
 if args.accept_wps_pdf:
  if args.rebuild or args.pdf_only or args.check_only:parser.error('--accept-wps-pdf须单独使用')
  import pymupdf
  path=args.accept_wps_pdf.resolve();pdf=pymupdf.open(path)
  assert 'wps' in str(pdf.metadata).lower() or 'kingsoft' in str(pdf.metadata).lower(),pdf.metadata
  out=root/'研究报告/04_word';native=out/'研究报告终稿.docx'
  before=hashlib.sha256(native.read_bytes()).hexdigest()
  if path!=out/'研究报告终稿.pdf':shutil.copy2(path,out/'研究报告终稿.pdf')
  run('更新目录缓存.py',root)
  record={'排版引擎':'WPS Office，原生DOCX直接导出','页数':len(pdf),'PDF元数据':pdf.metadata,
   '导出前WordSHA256':before,'WordSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),
   'PDFSHA256':hashlib.sha256((out/'研究报告终稿.pdf').read_bytes()).hexdigest(),
   '说明':'目录缓存更新后须重新打开DOCX导出并接收一次；最终检查同时核对PDF中印出的目录页码。'}
  (root/'研究报告/05_review/当前版/WPS原生导出登记.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
  print('WPS PDF及Word目录缓存已同步。请核对印出的目录并完成版面检查，再运行--check-only。')
  return
 subprocess.run([sys.executable,str(root/'tools/check_report_policy.py'),'--root',str(root),'--stage','final'],cwd=root,check=True)
 run('Word表格内容复核.py',root)
 subprocess.run([sys.executable,str(root/'tools/verify_current_report.py')],cwd=root,check=True)

if __name__=='__main__':main()
