from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import json,hashlib,shutil,csv
R=Path.cwd();O=R/'研究报告/PPT/制作准备_20261019';D=O/'数据依据';D.mkdir(exist_ok=True)
tables=json.loads((O/'研究报告终稿_表格.json').read_text())
picked={}
for x in tables:
    if x['preceding'].startswith('表'):
        key=x['preceding'].split(' ')[0]
        picked[key]=x
        with (D/(key+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(x['rows'])
(D/'报告表格索引.json').write_text(json.dumps(picked,ensure_ascii=False,indent=2))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
f=R/'研究报告/04_word/研究报告终稿.docx';imgs=[]
with ZipFile(f) as z:
    body=E.fromstring(z.read('word/document.xml')).find('w:body',ns)
    rels={n.get('Id'):n.get('Target') for n in E.fromstring(z.read('word/_rels/document.xml.rels'))}
    imdir=O/'报告原图';imdir.mkdir(exist_ok=True)
    for i,el in enumerate(body):
        for rid in el.xpath('.//a:blip/@r:embed',namespaces=ns):
            target=rels[rid];caption=''
            for nxt in list(body)[i+1:i+4]:
                tx=''.join(nxt.xpath('.//w:t/text()',namespaces=ns))
                if tx.startswith('图'):caption=tx;break
            stem=caption.split(' ')[0] if caption else '图_'+str(i)
            dest=imdir/(stem+Path(target).suffix);blob=z.read('word/'+target);dest.write_bytes(blob)
            imgs.append({'caption':caption,'body_index':i,'file':str(dest.relative_to(R)),'sha256':hashlib.sha256(blob).hexdigest()})
(O/'报告图件索引.json').write_text(json.dumps(imgs,ensure_ascii=False,indent=2))
proof={'status':'preparation_only_not_deck_delivery','source_docx_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'data_tables':len(picked),'source_figures':len(imgs),'checks':[]}
for key in ['表5-9','表5-10','表5-11']:
    proof['checks'].append({'table':key,'rows':picked[key]['rows']})
rig=98006.53;ela=95107.86
proof['arithmetic']={'rigid_total_万元':rig,'elastic_total_万元':ela,'difference_万元':round(rig-ela,2),'saving_percent':round((rig-ela)/rig*100,2)}
proof['report_scope_checks']=['正文统计输入与历史模型回算分别标明','原报告及三份参考材料仅作读取','正式PPT、科研图和讲稿尚未制作，等待PPT Master §4.3方案确认']
(O/'准备阶段核验.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
for src in ['inspect_ppt_materials_1019.py','preview_ppt_template_1019.py','prepare_ppt_sources_1019.py']:
    shutil.copyfile(Path('/tmp')/src,O/src)
print(json.dumps({'data_tables':len(picked),'figures':len(imgs),'saving_percent':proof['arithmetic']['saving_percent']},ensure_ascii=False))
