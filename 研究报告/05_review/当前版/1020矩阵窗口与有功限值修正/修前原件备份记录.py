from pathlib import Path
import shutil,json,hashlib
root=Path.cwd();old=root/'研究报告/05_review/当前版/1019推广矩阵扩展';new=root/'研究报告/05_review/当前版/1020矩阵窗口与有功限值修正';new.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((old/'交付登记.json').read_text());mapping={}
for name,digest in r['当前文件SHA256'].items():
 p=root/name
 # prompt.md is user-owned and has received the latest feedback; preserve both committed parent and new input.
 if sha(p)!=digest:
  assert name=='prompt.md',name
  import subprocess
  data=subprocess.check_output(['git','show','HEAD:'+name]);assert hashlib.sha256(data).hexdigest()==digest
 else:data=p.read_bytes()
 q=new/'上一版交付原件'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);mapping[name]={'path':str(q.relative_to(root)),'SHA256':digest}
(new/'上一版交付衔接.json').write_text(json.dumps({'父交付登记':str((old/'交付登记.json').relative_to(root)),'父交付登记SHA256':sha(old/'交付登记.json'),'原件映射':mapping},ensure_ascii=False,indent=2)+'\n')
for name in ['研究报告/04_word/研究报告终稿.docx','研究报告/04_word/研究报告终稿.pdf','研究报告/02图表/当前版/计算表.json','研究报告/02图表/当前版/生成段落.json']+[str(p.relative_to(root)) for p in (root/'研究报告/03_MD/当前版').glob('*.md')]:
 q=new/'修前原件'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,q)
for name in ['独立LP核验.json','扩展数据独立核验.json']:
 shutil.copy2(old/name,new/name)
mode=json.loads((old/'交付模式.json').read_text());mode['用户依据']='2026-10-20四项修正：8MW有功限值、局部缩窄窗口、容量平台合并及采样11点同步。';mode['允许更新表键'].append('extended_parameter_nodes')
(new/'交付模式.json').write_text(json.dumps(mode,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(root/'memory/current.md',root/'memory/archive/2026-10-20-矩阵窗口与有功限值修正前.md')
print('已保留并校验上一版',len(mapping),'项及当前Word/PDF/source baseline')
