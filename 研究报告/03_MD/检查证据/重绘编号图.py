"""只调整正式图内题号；读取阶段1准入数据，不求解模型、不生成Word。"""
from pathlib import Path
import importlib.util,json,shutil,hashlib,tempfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'研究报告/03_MD'
spec=importlib.util.spec_from_file_location('stage1_plot',ROOT/'研究报告/02图表/scripts/generate_stage1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
registry=json.loads((OUT/'图表引用登记.json').read_text())
original_header=m.header
lookup={r['source_number']:r['number'] for r in registry}
def header(fig,note):
 original_header(fig,note)
 fig._suptitle.set_text(lookup[m.CURRENT['规划编号']]+' '+m.CURRENT['图表名称'])
m.header=header
assetroot=OUT/'图表';(assetroot/'final_figures').mkdir(parents=True,exist_ok=True);(assetroot/'source_data').mkdir(exist_ok=True)
checks=[]
for r in registry:
 old,new=r['source_number'],r['number']
 src=ROOT/r['source'];original=json.loads(src.read_text())
 if old.startswith('图'):
  with tempfile.TemporaryDirectory(prefix='report-plot-',dir='/tmp') as tmp:
   m.OUT=Path(tmp)
   for folder in ['final_figures','final_tables','source_data']: (m.OUT/folder).mkdir()
   m.draw(next(p for p in m.PLANS if p['规划编号']==old))
   trace=json.loads((m.OUT/'source_data'/f'{old}.json').read_text())
   assert trace['data']==original['data'],f'图表数据漂移：{old}'
   assert not m.QA[-1]['text_outside_canvas'],m.QA[-1]
   for ext in ['png','svg','pdf']:
    shutil.copy2(m.OUT/'final_figures'/f'{old}.{ext}',assetroot/'final_figures'/f'{new}.{ext}')
   trace['number']=new;trace['source_number']=old;trace['source_file']=r['source'];trace['source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
   trace['files']=[f'final_figures/{new}.{ext}' for ext in ['png','svg','pdf']]
   (assetroot/'source_data'/f'{new}.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
   checks.append({'number':new,'source_number':old,'data_unchanged':True,'canvas_check':m.QA[-1],'display_title':trace['display_text'][0] if trace['display_text'] else None})
 else:
  trace=original.copy();trace.update(number=new,source_number=old,source_file=r['source'],source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),files=[])
  (assetroot/'source_data'/f'{new}.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
 csvsrc=src.with_suffix('.csv')
 if csvsrc.exists():shutil.copy2(csvsrc,assetroot/'source_data'/f'{new}.csv')
# Synchronize display metadata with the current chapter layout, retaining source identities.
import re
for r in registry:
 p=assetroot/'source_data'/f"{r['number']}.json"
 trace=json.loads(p.read_text());original=json.loads((ROOT/r['source']).read_text())
 trace['source_chapter']=original['chapter'];trace['chapter']=r['chapter'][3:-3]
 chapter=(OUT/r['chapter']).read_text()
 token='!['+r['number']+' ' if r['number'].startswith('图') else '\n'+r['number']+' '
 headings=re.findall(r'^#{2,3} (.+)$',chapter[:chapter.index(token)],re.M)
 trace['source_section']=original.get('section');trace['section']=headings[-1] if headings else None
 if r['number'].startswith('表'):
  trace['display_text']=[re.sub(r'(?:图|表)\d+-\d+(?!\d)',lambda m:lookup.get(m[0],m[0]),t) for t in original.get('display_text',[])]
 trace['scripts']=['研究报告/02图表/scripts/generate_stage1.py','研究报告/03_MD/检查证据/重绘编号图.py']
 p.write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
(OUT/'检查证据/图内编号核验.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print('完成17张正式图；数据不变、画布检查通过。')
