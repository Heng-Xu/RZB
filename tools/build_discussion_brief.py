"""从讨论稿源文和当前地区原始结果生成讨论用Word，支持一致性检查。"""
from pathlib import Path
import argparse,hashlib,json,re
from docx import Document
from docx.shared import Cm,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]

def material(root):
    folder=root/'研究报告/供电公司讨论稿';source=folder/'讨论稿.md';files=[source,root/'tools/build_discussion_brief.py'];annual_tables={};rows=[['地区／方案','主变容量\nMVA','容载比','储能功率\nMW','累计新增联络\n条','费用现值\n万元']];cost={}
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        for case,name in [('rigid_storage','刚性'),('elastic_storage','弹性')]:
            p=root/f'研究报告/试算/20261010_四小时案例/{region}/{case}/summary.json';files.append(p);x=json.loads(p.read_text());y=x['annual'][-1];cost[(region,case)]=x['cost_npv_10k']
            if case=='elastic_storage':
                annual_rows=[['年份','当年新购主变\nMVA','当年新增联络\n条','当年新增储能\nMW','年末主变容量\nMVA','年末容载比']]
                previous_storage=0.0
                for a in x['annual']:
                    added_storage=a['storage_nameplate_mw']-previous_storage
                    assert added_storage>=-1e-9
                    annual_rows.append([str(a['year']),f"{a['purchased_transformer_mva']:.2f}",str(a['new_lines']),f"{added_storage:.2f}",f"{a['capacity_mva']:.2f}",f"{a['clr']:.2f}"])
                    previous_storage=a['storage_nameplate_mw']
                annual_tables[region.upper()+'_ANNUAL_TABLE']=annual_rows
            rows.append([cn+name,f"{y['capacity_mva']:.2f}",f"{y['clr']:.2f}",f"{y['storage_nameplate_mw']:.2f}",str(y['cumulative_lines']),f"{x['cost_npv_10k']:.2f}"])
    rigid=sum(v for (r,c),v in cost.items() if c=='rigid_storage');elastic=sum(v for (r,c),v in cost.items() if c=='elastic_storage')
    savings=f'两地区费用现值合计由{rigid:.2f}万元降至{elastic:.2f}万元，减少{rigid-elastic:.2f}万元，约{(rigid-elastic)/rigid:.0%}。邳州和市区分别减少{cost[("pizhou","rigid_storage")]-cost[("pizhou","elastic_storage")]:.2f}万元、{cost[("city","rigid_storage")]-cost[("city","elastic_storage")]:.2f}万元。'
    matrix_path=root/'研究报告/02图表/当前版/计算表.json';files.append(matrix_path)
    matrix=json.loads(matrix_path.read_text())
    ranges=[['分布式电源\n装机渗透率','年最大净负荷\n平均增长率','初始转供率\n≤30%','初始转供率\n(30%, 50%]','初始转供率\n>50%']]
    for eta,label in enumerate(['≤1.00','(1.00, 2.00]','>2.00']):
        values=[[c.strip() for c in ln.strip('|').split('|')] for ln in matrix[f'six_matrix_0_1_{eta}'].splitlines() if ln.startswith('|')][2:]
        for growth in ['≤2%','(2%, 4%]','(4%, 7%]','>7%']:
            selected=[r for r in values if r[0]==growth and r[1]=='(1.65, 6.85]']
            assert [r[2] for r in selected]==['≤30%','(30%, 50%]','>50%']
            ranges.append([label,growth]+[r[3] for r in selected])
    tables={'RESULT_TABLE':rows,**annual_tables,'RANGE_TABLE':ranges}
    text=source.read_text().replace('[[SAVINGS]]',savings)
    assert set(re.findall(r'\[\[([A-Z_]+TABLE)\]\]',text))==set(tables)
    assert '本次讨论需核实的工程条件' not in text
    assert text.split('## 待与电力公司讨论')[1].strip()=='1、市区、邳州的转供率如何考虑？\n\n2、市区的电缆化率如何考虑（电缆和架空线比例）？'
    return folder,text,tables,{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def build(root):
    folder,text,tables,hashes=material(root);doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=sec.bottom_margin=Cm(1.8);sec.left_margin=sec.right_margin=Cm(2.0)
    def font(run,size=11.5,bold=False):
        run.font.name='Times New Roman';run.font.size=Pt(size);run.font.bold=bold;run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'方正仿宋_GBK')
    style=doc.styles['Normal'];style.font.name='Times New Roman';style.font.size=Pt(11.5);style._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'方正仿宋_GBK')
    for line in text.splitlines():
        if not line.strip():continue
        if line=='[[PAGEBREAK]]':doc.add_page_break();continue
        if line.startswith('[[') and line.endswith('TABLE]]'):
            rows=tables[line[2:-2]]
            tbl=doc.add_table(rows=0,cols=len(rows[0]));tbl.style='Table Grid'
            for i,row in enumerate(rows):
                cells=tbl.add_row().cells
                for cell,value in zip(cells,row):
                    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;p=cell.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3);p.paragraph_format.line_spacing=1.05;font(p.add_run(value),10.5,i==0)
                pr=tbl.rows[-1]._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
                if i==0:pr.append(OxmlElement('w:tblHeader'))
            continue
        p=doc.add_paragraph();pf=p.paragraph_format;pf.line_spacing=1.22;pf.space_after=Pt(5);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        if line.startswith('# '):p.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(p.add_run(line[2:]),17,True);pf.space_after=Pt(5);pf.keep_with_next=True
        elif line.startswith('> '):p.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(p.add_run(line[2:]),11);pf.space_after=Pt(12);pf.keep_with_next=True
        elif line.startswith('### '):font(p.add_run(line[4:]),11.5,True);pf.space_before=Pt(4);pf.space_after=Pt(4);pf.keep_with_next=True
        elif line.startswith('## '):font(p.add_run(line[3:]),13,True);pf.space_before=Pt(6);pf.space_after=Pt(5);pf.keep_with_next=True
        else:
            pf.first_line_indent=Pt(23) if not line.startswith('- ') else Pt(0);font(p.add_run(line[2:] if line.startswith('- ') else line))
    foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(foot.add_run('徐州地区110 kV电网弹性容载比研究  ·  '),9)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
    for part in doc.part.package.parts:
        if hasattr(part,'element'):
            for el in part.element.iter():
                for key,value in list(el.attrib.items()):
                    if value in ['Courier','Courier New']:el.set(key,'Times New Roman')
    path=folder/'供电公司讨论稿.docx';doc.save(path)
    hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();(folder/'生成登记.json').write_text(json.dumps({'来源SHA256':hashes,'表格':tables,'费用摘要':text.split('[[RESULT_TABLE]]')[1].split('[[PAGEBREAK]]')[0].strip()},ensure_ascii=False,indent=2)+'\n')
    print(path)

def check(root,pdf=False):
    folder,text,tables,hashes=material(root);record=json.loads((folder/'生成登记.json').read_text());assert tables==record['表格']
    for name,sha in record['来源SHA256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,('讨论稿需重新生成',name)
    assert all(record['来源SHA256'][k]==v for k,v in hashes.items())
    doc=Document(folder/'供电公司讨论稿.docx')
    assert len(doc.tables)==len(tables)
    for table,rows in zip(doc.tables,tables.values(),strict=True):
        assert [[c.text for c in r.cells] for r in table.rows]==rows,'讨论稿表格与来源不一致'
    expected=[re.sub(r'^(?:#{1,3}|>|-) ','',l) for l in text.splitlines() if l.strip() and not l.startswith('[[')]
    assert [p.text for p in doc.paragraphs if p.text.strip()]==expected
    if pdf:
        import pymupdf
        d=pymupdf.open(folder/'供电公司讨论稿.pdf');assert len(d)==text.count('[[PAGEBREAK]]')+1,('讨论稿出现意外跨页',len(d));assert 'wps' in str(d.metadata).lower()
        norm=lambda s:re.sub(r'\s+','',s);alltext=norm(''.join(p.get_text() for p in d))
        assert all(norm(l) in alltext for l in expected),'简稿PDF内容缺失'
        assert all(norm(c) in alltext for rows in tables.values() for row in rows for c in row),'简稿PDF表格内容缺失'
    print('讨论稿来源、正文与结果表一致性通过')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--check',action='store_true');ap.add_argument('--pdf',action='store_true');a=ap.parse_args();check(a.root,a.pdf) if a.check else build(a.root)
