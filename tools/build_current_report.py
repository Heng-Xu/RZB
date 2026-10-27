"""当前六章报告唯一维护入口；默认核验，--rebuild 明确重建。"""
from pathlib import Path
import argparse, shutil, subprocess, sys, hashlib, json

ROOT=Path(__file__).resolve().parents[1]

def run(script,root):
 subprocess.run([sys.executable,str(root/'研究报告/05_review/当前版'/script)],cwd=root,check=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--summary',action='store_true',help='按10.22指定模板维护独立成果总结，不改六章研究报告')
 parser.add_argument('--inline-math',action='store_true',help='仅对当前成果总结的符号解释作原生行内公式修正')
 parser.add_argument('--discussion',action='store_true',help='维护当前讨论稿；以终稿DOCX为内容依据')
 parser.add_argument('--feedback-report',action='store_true',help='在10.17甲方原文件内以xh增量修订；保留批注和甲方既有修订')
 parser.add_argument('--plain-report',action='store_true',help='在已交付清稿基础上局部修改，保留批注，全部历史修订接受')
 parser.add_argument('--root',type=Path,default=ROOT,help='完整项目副本的根目录，可用于试构建')
 parser.add_argument('--rebuild',action='store_true',help='修改六章源后装配原生Word，随后须用WPS导出PDF并接收')
 parser.add_argument('--pdf-only',action='store_true',help='旧选项；现须从WPS原生导出PDF')
 parser.add_argument('--check-only',action='store_true',help='仅核验；不重建 Word 或 PDF')
 parser.add_argument('--docx-only',action='store_true',help='装配原生DOCX，供WPS打开导出；完成导出后使用--accept-wps-pdf')
 parser.add_argument('--accept-wps-pdf',type=Path,help='接收由当前原生DOCX在WPS中直接导出的PDF，并同步目录缓存')
 args=parser.parse_args();root=args.root.resolve()
 if args.inline_math and not args.summary:parser.error('--inline-math须与--summary同时使用')
 if args.summary:
  from report_summary import main as summary_main
  options=['--root',str(root)]
  if args.inline_math:options.append('--inline-math')
  if args.rebuild or args.docx_only:options.append('--rebuild')
  if args.accept_wps_pdf:options+=['--accept-wps-pdf',str(args.accept_wps_pdf)]
  return summary_main(options)
 from archive_log_evidence import temporary_logs
 with temporary_logs(root):return maintain(args,parser,root)

def maintain(args,parser,root):
 from report_plain_revision import active as plain_active
 plain=args.plain_report or plain_active(root)
 if plain and args.feedback_report:parser.error('本轮普通模式清稿与历史修订稿模式不能同时使用')
 subprocess.run([sys.executable,str(root/'tools/verify_future_case_results.py'),'--root',str(root)],cwd=root,check=True)
 if args.discussion:
  if args.rebuild:
   parser.error('讨论稿须在甲方反馈原文件上以xh修订，禁止调用历史生成器重建；核验使用--discussion --check-only')
  subprocess.run([sys.executable,str(root/'tools/revise_current_discussion.py')],cwd=root,check=True)
  return
 if args.docx_only or args.rebuild:
  if args.pdf_only or args.check_only or args.accept_wps_pdf:parser.error('--docx-only/--rebuild须单独使用')
  run('装配Word.py',root)
  if args.feedback_report:
   # 先用现有WPS PDF回填实际目录页码；重导出后仍须逐项重新核验。
   run('更新目录缓存.py',root)
   review=root/'研究报告/05_review/当前版/1017甲方批注与逐年案例更新'
   shutil.copy2(root/'研究报告/04_word/研究报告终稿.docx',review/'目标清稿.docx')
   subprocess.run([sys.executable,str(root/'tools/revise_report_in_place.py')],cwd=root,check=True)
   subprocess.run([sys.executable,str(root/'tools/verify_annual_report_update.py')],cwd=root,check=True)
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
 if plain:
  from report_plain_revision import verify_release
  verify_release()
  return
 if (root/'研究报告/05_review/当前版/1017甲方批注与逐年案例更新/原文件修订核验.json').exists():
  subprocess.run([sys.executable,str(root/'tools/verify_annual_report_update.py'),'--final'],cwd=root,check=True)
  return
 run('Word表格内容复核.py',root)
 subprocess.run([sys.executable,str(root/'tools/verify_current_report.py')],cwd=root,check=True)
 subprocess.run([sys.executable,str(root/'tools/verify_report_review.py')],cwd=root,check=True)

if __name__=='__main__':main()
