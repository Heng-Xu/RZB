"""定位正文短句衔接和分号待复核点；语义判断由编辑完成，不按句长自动改文。"""
from pathlib import Path
import re,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
LOGIC_RULES={'正文避免以分号代替转折条件或推论衔接','正文避免费用条件与比较用途碎句堆叠'}
def is_explanatory_line(line):
 s=line.strip()
 return bool(not s or s.startswith(('#','|','$$','[[FIG:')) or re.match(r'^(?:式中[，：:]|注[：:]|图\s*\d+(?:[-－]\d+)?\s|表\s*\d+(?:[-－]\d+)?\s|\[\d+\])',s) or re.match(r'^(?:表中符号|各项计算分别采用|ηC、ḡ、α、r₀)',s))
def collect(root=ROOT):
 assets=root/'研究报告/02图表/当前版';sections=json.loads((assets/'生成段落.json').read_text());tables=json.loads((assets/'计算表.json').read_text());entries=[]
 def walk(value,loc,stack=()):
  in_math=False
  for i,line in enumerate(value.splitlines(),1):
   if "$$" in line:
    if line.count("$$")%2:in_math=not in_math
    continue
   if in_math:continue
   refs=re.findall(r'\[\[(SECTION|TABLE):([^]]+)\]\]',line)
   for kind,key in refs:
    token=(kind,key)
    if token in stack:raise ValueError('正文引用循环')
    walk((sections if kind=='SECTION' else tables)[key],f'{loc}:{i} → '+('生成段落.json' if kind=='SECTION' else '计算表.json')+f'[{key}]',stack+(token,))
   if refs or is_explanatory_line(line):continue
   sents=[s for s in re.split('。',line) if s.strip()];short=sum(len(re.sub(r'\[[\d—–,、]+\]|\$[^$]*\$','',s))<=35 for s in sents)
   flags=[]
   if re.search('[；;]',line):flags.append('正文分号逐处复核')
   if len(sents)>=3 and short>=2:flags.append('多句衔接逐段复核')
   entries.append({'位置':f'{loc}:{i}','正文':line,'SHA256':hashlib.sha256(line.encode()).hexdigest(),'复核提示':flags})
 for p in sorted((root/'研究报告/03_MD/当前版').glob('0[1-6] *.md')):walk(p.read_text(),str(p.relative_to(root)))
 # 最终视图，以修订后的可见内容为准。
 import sys
 sys.path.insert(0,str(root/'tools'))
 import revise_current_discussion as r
 from zipfile import ZipFile
 with ZipFile(r.TARGET) as z:body=r.accept_view(r.xml(z.read('word/document.xml'))).find(r.qn('body'))
 walk('\n'.join(r.text(p) for p in body.findall(r.qn('p'))),'供电公司讨论稿.docx最终视图')
 return entries

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();rows=collect();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'说明':'提示用于定位，句长和分号数量不是质量判据；说明性段落不适用正文分号提示。','正文段落':rows},ensure_ascii=False,indent=2)+'\n');print('正文段落',len(rows),'待复核',sum(bool(r['复核提示']) for r in rows))
if __name__=='__main__':main()
