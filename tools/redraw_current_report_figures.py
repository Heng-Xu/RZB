"""Re-render final admitted chart data using the user's report presentation rules."""
from pathlib import Path
import importlib.util,json,shutil,hashlib,tempfile,re
ROOT=Path.cwd();OUT=ROOT/'研究报告/02图表/final_figures';OUT.mkdir(parents=True,exist_ok=True)
QA=ROOT/'研究报告/05_review'
spec=importlib.util.spec_from_file_location('frozen_stage1',ROOT/'研究报告/02图表/scripts/generate_stage1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.fm.fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
m.plt.rcParams['font.family']=['Times New Roman','FZFangSong-Z02']
from matplotlib.text import Text
from matplotlib.figure import Figure
registry=json.loads((ROOT/'研究报告/03_MD/图表引用登记.json').read_text())
def clean(txt):
 txt=txt.replace('（支撑层）','').replace('(支撑层)','')
 txt=txt.replace('区县源荷比（降压峰近似，%）','区县源荷比 / %')
 return txt
def header(fig,note):
 for ax in fig.axes:
  for which in ['x','y']:
   labels=getattr(ax,'get_'+which+'ticklabels')()
   if any('支撑层' in t.get_text() for t in labels):getattr(ax,'set_'+which+'ticks')(getattr(ax,'get_'+which+'ticks')(),[clean(t.get_text()) for t in labels])
 for t in fig.findobj(Text):t.set_text(clean(t.get_text()))
m.header=header
save=Figure.savefig
def savefig(self,*args,**kwargs):
 kwargs.update(bbox_inches='tight',pad_inches=.08)
 return save(self,*args,**kwargs)
Figure.savefig=savefig
checks=[]
for r in registry:
 if not r['number'].startswith('图'):continue
 old,new=r['source_number'],r['number'];source=ROOT/r['source'];original=json.loads(source.read_text())
 with tempfile.TemporaryDirectory(prefix='stage3-chart-',dir='/tmp') as tmp:
  m.OUT=Path(tmp)
  for f in ['final_figures','final_tables','source_data']:(m.OUT/f).mkdir()
  m.draw(next(p for p in m.PLANS if p['规划编号']==old))
  trace=json.loads((m.OUT/'source_data'/f'{old}.json').read_text())
  assert trace['data']==original['data'],new
  assert not m.QA[-1]['text_outside_canvas'],m.QA[-1]
  assert not any('资料来源' in t or '支撑层' in t or re.match(r'^图\d+-\d+ ',t) for t in trace['display_text']),trace['display_text']
  for ext in ['png','svg','pdf']:shutil.copy2(m.OUT/'final_figures'/f'{old}.{ext}',OUT/f'{new}.{ext}')
  checks.append({'number':new,'stage1_number':old,'stage1_data_file':r['source'],'stage1_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'data_unchanged':True,'display_text':trace['display_text'],'original_note':original['note'],'original_title':original['title'],'new_rules':['图内不包含整体图名、图注或资料来源','删除支撑层括注','保留单位、图例及必要子图标识'],'figure_sha256':hashlib.sha256((OUT/f'{new}.png').read_bytes()).hexdigest(),'font_families':['FZFangSong-Z02','Times New Roman'],'chinese_font_file':'/usr/share/fonts/wps-office/FZFSK.TTF','dpi':600})
(QA/'图件展示修订核验.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print('17张图已生成；原始数据逐图一致。')
