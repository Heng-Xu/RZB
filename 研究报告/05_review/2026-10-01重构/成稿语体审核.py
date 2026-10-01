"""只对明确命中 lieflat-less-ai-tone 白名单的句子作最小改写。"""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'研究报告/03_MD/2026-10-01重构';OUT=Path(__file__).parent
EDITS=[
('01 第一章 绪论.md',1,'累计采购量可能明显超过末年净增容量，这并不构成重复计量，而是不同年度更换事件的结果。','累计采购量可能明显超过末年净增容量，其差异来自不同年度更换事件，各次采购没有重复计量。'),
('04 第四章 基于实际工程的建设成本模型.md',1,'模型系数不是单独取王庄23.02万元/MVA，而是把王庄与鲁庙的静态投资合计除以新购容量合计，形成16.573333万元/MVA。','模型系数将王庄23.02万元/MVA对应工程与鲁庙工程合并，以静态投资合计除以新购容量合计，形成16.573333万元/MVA。'),
('02 第二章 国内外研究现状.md',2,'国内外相关研究围绕分布式电源承载力、源荷运行特征、灵活资源协同配置、工程费用与规划评价展开。','国内外相关研究围绕分布式电源承载力与源荷运行特征，以及灵活资源协同配置、工程费用与规划评价展开。'),
('02 第二章 国内外研究现状.md',2,'国内研究已形成多电压等级容量协同、下级网络供电能力分析、分层承载力评估和源网储联合规划等方法。','国内研究已形成多电压等级容量协同与下级网络供电能力分析，以及分层承载力评估和源网储联合规划等方法。'),
('02 第二章 国内外研究现状.md',2,'后续章节分别给出数据处理、系数计算、目标函数和推荐矩阵，','后续章节分别给出数据处理及系数计算，以及目标函数和推荐矩阵，'),
('01 第一章 绪论.md',2,'核查包括原表换算、区县容量汇总、年度资产不减、负荷转接守恒、储能整数规模、正反向容量及单台主变退出容量。','核查包括原表换算和区县容量汇总，也检查年度资产不减、负荷转接守恒及储能整数规模，并复算正反向容量和单台主变退出容量。'),
('05 第五章 弹性容载比规划建议与寻优结果.md',2,'参数定义优先采用导则已有术语。容载比、网供负荷、供电区域类别与转供能力按DL/T 5729—2023列示[4]。','参数定义优先采用导则已有术语。容载比与网供负荷，以及供电区域类别和转供能力，按DL/T 5729—2023列示[4]。'),
]
def structure(s):
 return {'paragraphs':len(re.split(r'\n\s*\n',s.strip())),'headings':re.findall(r'^#+ .+$',s,re.M),'markers':re.findall(r'\[\[(?:TABLE|FIG|SECTION):[^\]]+\]\]',s),'formulae':re.findall(r'\$\$[\s\S]*?\$\$',s),'numbers':re.findall(r'\d+(?:\.\d+)?',s),'citations':re.findall(r'\[[\d—,-]+\]',s)}
def main():
 backups=OUT/'语体审核前正文';backups.mkdir(exist_ok=True)
 log=[];initial={};texts={}
 for p in sorted(D.glob('0[1-6] *.md')):
  texts[p.name]=p.read_text();initial[p.name]=structure(texts[p.name])
  if not (backups/p.name).exists():(backups/p.name).write_text(texts[p.name])
 for name,rule,old,new in EDITS:
  s=texts[name]
  if old not in s:
   assert new in s,(name,old);status='此前已执行'
  else:
   assert s.count(old)==1;(texts.__setitem__(name,s.replace(old,new,1)));status='已执行'
  log.append({'文件':name,'规则':rule,'原句':old,'改句':new,'状态':status})
 for name,s in texts.items():
  assert structure(s)==initial[name],('结构或数值发生改变',name)
  (D/name).write_text(s)
 report={'skill':'/home/xh/.agents/skills/lieflat-less-ai-tone/SKILL.md','风格依据':'研究报告/范文与语料/国网宿迁公司宿迁市“十五五”电网侧新型储能发展项目研究报告-初稿.docx及提取语料.zip','改动':log,'验收':{'标题与段落顺序':'保持','段落数量':'保持','数字及引文':'保持','公式表格图件位置':'保持','未命中句子':'逐字保持'},'保留项':['供电条件、设备配置及财务科目的完整列举属于技术清单，按规则2例外保留','年度逐站校核按相同指标组织，属于清单式平行条款，按规则3例外保留','真实统计口径、标准和研究边界的区别用于限定结论，保留技术含义','章节规范编号符合原Word体裁，按规则6例外保留']}
 (OUT/'成稿语体审核记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('语体改动',len(log),'结构、数字、公式、引文均保持')
if __name__=='__main__':main()
