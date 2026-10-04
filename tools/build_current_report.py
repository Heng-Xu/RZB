"""当前六章报告唯一维护入口；默认核验，--rebuild 明确重建。"""
from pathlib import Path
import argparse, os, shutil, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]

def run(script,root):
 subprocess.run([sys.executable,str(root/'研究报告/05_review/当前版'/script)],cwd=root,check=True)

def export_pdf(root):
 requested=os.environ.get('XUZHOU_LIBREOFFICE')
 program=Path(requested or shutil.which('libreoffice') or shutil.which('soffice') or '/tmp/xuzhou_lo/root/usr/lib/libreoffice/program/soffice')
 if not program.is_file():raise RuntimeError('请安装 LibreOffice，或设置 XUZHOU_LIBREOFFICE 为 soffice 路径。')
 env=os.environ.copy();env['SAL_USE_VCLPLUGIN']='svp';env['GSETTINGS_BACKEND']='memory'
 if str(program).startswith('/tmp/xuzhou_lo/'):
  env['LD_LIBRARY_PATH']=str(program.parent)+':/tmp/xuzhou_lo/root/usr/lib/x86_64-linux-gnu'+(':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
  env['FONTCONFIG_FILE']='/tmp/xuzhou_lo/fonts.conf'
  env['LIBLANGTAG_DATA_DIR']='/tmp/xuzhou_lo/root/usr/share/liblangtag'
 out=root/'研究报告/04_word'
 with tempfile.TemporaryDirectory(prefix='xuzhou-lo-') as profile:
  result=subprocess.run([str(program),'-env:UserInstallation='+Path(profile).as_uri(),'--headless','--norestore','--convert-to','pdf','--outdir',str(out),str(out/'PDF排版副本.docx')],env=env,cwd=root,capture_output=True,text=True,timeout=180)
  (root/'研究报告/05_review/当前版/PDF导出日志.txt').write_text(result.stdout+result.stderr)
  result.check_returncode()
 pdf=out/'PDF排版副本.pdf'
 if not pdf.is_file():raise RuntimeError('LibreOffice 未生成 PDF。')
 shutil.copy2(pdf,out/'研究报告终稿.pdf')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--root',type=Path,default=ROOT,help='完整项目副本的根目录，可用于试构建')
 parser.add_argument('--rebuild',action='store_true',help='修改六章源后重建 Word、目录和 PDF，会覆盖当前成果')
 parser.add_argument('--pdf-only',action='store_true',help='保留原生 Word，仅更新配套 PDF')
 parser.add_argument('--check-only',action='store_true',help='仅核验；不重建 Word 或 PDF')
 args=parser.parse_args();root=args.root.resolve()
 if args.check_only and (args.rebuild or args.pdf_only):parser.error('--check-only 不能与重建选项同时使用')
 if args.rebuild:
  run('装配Word.py',root)
 if args.rebuild or args.pdf_only:
  run('PDF数学排版副本.py',root);export_pdf(root)
 if args.rebuild:
  run('更新目录缓存.py',root)
  run('PDF数学排版副本.py',root);export_pdf(root)
 run('校核当前基准.py',root)
 run('外推独立复核.py',root)
 run('核验报告.py',root)

if __name__=='__main__':main()
