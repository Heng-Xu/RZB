"""按甲方规划应用建议局部替换成果汇报5.1页的文字，保留原版式。"""
from pathlib import Path
from lxml import etree as E
import json

BASE=Path(__file__).resolve().parents[1]
WORK=BASE/'成果汇报_规划应用建议对齐_20261027'
PATH=WORK/'authoring-svg-flat/slide_28.svg'
NS={'s':'http://www.w3.org/2000/svg'}
TEXTS={
 'shape-19':['5.1 规划应用相关工作建议'],
 'shape-9':['以五参数矩阵推进“一片一策”规划应用'],
 'shape-16':['依据：研究报告5.7、6.2'],
 'shape-42':['矩阵应用'],
 'shape-43':['目标：查表初选与设备校核衔接。','措施：统一五项参数口径，分区查表，','折算主变容量并落实到具体站点。'],
 'shape-23':['站级论证'],
 'shape-24':['目标：衔接区域储备与站级供电能力。','措施：核定转供能力，按缺口配置储能，','统一约束比选主变增容与中压联络。'],
 'shape-28':['滚动完善'],
 'shape-29':['目标：容量安排与建设进度同步。','措施：逐年更新参数与建设时序，','价格或条件变化后重算并反馈校核。'],
 'shape-33':['试用推广'],
 'shape-34':['先在徐州开展查表、论证、校核试用，','验证参数口径与应用流程后，','向其他高渗透率片区推广。'],
 'shape-38':['▪ 工作安排：查表定容、站级论证、滚动校核；先在徐州试用，再推广至其他高渗透率片区。'],
}


def main():
 tree=E.fromstring(PATH.read_bytes());changes=[]
 for ident,lines in TEXTS.items():
  choices=tree.xpath('.//s:g[@id="'+ident+'"]/s:text',namespaces=NS)
  assert len(choices)==1,ident
  element=choices[0];before=''.join(element.itertext())
  for child in list(element):element.remove(child)
  element.text=lines[0]if len(lines)==1 else None
  if len(lines)>1:
   element.set('data-pptx-text-model','lines');element.set('data-paragraph-line-height','23')
   for i,line in enumerate(lines):
    span=E.SubElement(element,'{'+NS['s']+'}tspan',{'data-paragraph-line-break':'1'}if i else{});span.text=line
  changes.append({'对象':ident,'原文':before,'修改后':lines})
 PATH.write_bytes(E.tostring(tree,xml_declaration=True,encoding='UTF-8'))
 (WORK/'notes/slide_28.md').write_text('规划应用围绕矩阵应用、站级论证和滚动完善三项工作推进。统一五项参数口径，查表得到容量初选范围后，将其落实到具体站点及设备组合。结合转供能力、双向功率缺口和支撑时长，在统一运行约束下比选主变、储能与中压联络。随源荷变化、设备价格和工程进度滚动校核，先在徐州地区试用，再向其他高渗透率片区推广。\n')
 plan={'用户明确范围':'2026-10-27：按甲方成果总结规划应用相关工作建议的逻辑、风格和内容，对齐PPT5.1页；保留原版式，普通模式修改。',
       '页数及顺序':'38页保持，仅第28页可见文字及对应备注修改',
       '内容依据':'研究报告/甲方反馈/10.26/10.26成果总结.docx，“五、规划应用相关工作建议”；研究报告5.7、6.2',
       '模块':{'备注':'仅同步第28页','配音':'关闭','转场动画':'保留原有'},
       '逐页映射':[{'输出页':i,'来源页':i,'处理':'edited'if i==28 else'referenced',
                   '原因':'三项工作建议及徐州试用推广'if i==28 else'本轮不涉及，原生保留'}for i in range(1,39)],
       '局部文字替换':changes}
 (WORK/'内容映射与修正计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 print('仅第28页文字与备注已按甲方规划应用建议对齐。')


if __name__=='__main__':main()
