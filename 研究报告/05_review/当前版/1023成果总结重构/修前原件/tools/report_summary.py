"""成果总结：原模板填充、锁定数据提取与源稿/Word/WPS三阶段核验。"""
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json
import re
import shutil
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
Q=lambda name:'{'+W+'}'+name
SOURCE=Path('研究报告/03_MD/成果总结/成果总结.md')
TEMPLATE=Path('研究报告/甲方反馈/10.22/绿电进园区需求分析与服务策略研究 0905.docx')
OUT=Path('研究报告/04_word/成果总结.docx')
PDF=OUT.with_suffix('.pdf')
REVIEW=Path('研究报告/05_review/当前版/1022成本模型与约束补充')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def f(v):return str(Decimal(str(round(float(v),9))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def xml(e):return E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
def node(tag,**attrs):
    e=E.Element(Q(tag))
    for k,v in attrs.items():e.set(Q(k),str(v))
    return e

def md_rows(value):return [[x.strip()for x in line.strip('|').split('|')]for line in value.splitlines()if line.startswith('|')][2:]

def inputs(root=ROOT):
    from verify_future_case_results import verify
    proof=verify(root)
    assets=read(root/'研究报告/02图表/当前版/计算表.json')
    plans={(region,scheme):read(root/f'研究报告/试算/20261017_逐年需求驱动2035/{region}/{scheme}/summary.json')for region in ['pizhou','city']for scheme in ['rigid','elastic_capacity']}
    tables={}
    rows=[]
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        for scheme,label in [('rigid','刚性'),('elastic_capacity','弹性')]:
            p=plans[region,scheme]
            rows.append([cn,label]+[f(sum(a[k]for a in p['annual']))for k in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']]+[f(p['cost_npv_10k'])])
        table_rows=[]
        for year in [2021,2022,2023,2025,2030,2035]:
            rigid=next(a for a in plans[region,'rigid']['annual']if a['year']==year)
            elastic=next(a for a in plans[region,'elastic_capacity']['annual']if a['year']==year)
            table_rows.append([str(year),f(rigid['peak_mw']),f(rigid['capacity_mva']),f(rigid['clr']),f(elastic['capacity_mva']),f(elastic['clr'])])
        tables[region+'_years']={'headers':['年份','网供峰值/MW','刚性容量/MVA','刚性容载比','弹性容量/MVA','弹性容载比'],'rows':table_rows,'widths':[650,1620,1640,1370,1640,1386]}
    tables['cost_components']={'headers':['地区','方案','主变/万元','储能/万元','联络/万元','合计/万元'],'rows':rows,'widths':[650,650,1750,1750,1750,1756]}
    rows=[]
    for region,cn in [('pizhou','邳州'),('city','市区')]:
        for scheme,label in [('rigid','刚性'),('elastic_capacity','弹性')]:
            a=plans[region,scheme]['annual'][-1]
            rows.append([cn,label,f(a['capacity_mva']),f(a['storage_nameplate_mw']),f(a['storage_mwh']),str(a['cumulative_lines'])])
    tables['final_measures']={'headers':['地区','方案','主变容量/MVA','储能功率/MW','储能能量/MWh','累计新增联络/条'],'rows':rows,'widths':[650,650,1750,1750,1750,1756]}
    tables['correlations']={'headers':['指标','有效组数','有效节点数','Pearson','容量响应组占比'],'rows':md_rows(assets['current_controlled_correlations']),'widths':[2950,1150,1400,1150,1656]}
    tables['redundancy']={'headers':['候选指标','对应基础参数','Pearson','代表参数'],'rows':md_rows(assets['parameter_redundancy_groups']),'widths':[2400,2400,900,2606]}
    tables['input_correlations']={'headers':['参数','装机渗透率','年最大净负荷平均增长率','电缆长度占比','初始转供率','负荷分散系数'],'rows':md_rows(assets['current_input_correlations']),'widths':[1700,1321,1321,1321,1321,1322]}
    for c in range(3):
        for kd in ['low','high']:
            key=f'lookup_matrix_{c}_{kd}'
            tables[key]={'headers':['年最大净负荷平均增长率','装机渗透率','≤30%','(30%,50%]','(50%,70%]','>70%'],'rows':md_rows(assets[key]),'widths':[1450,1050,1451,1451,1451,1453]}
    return tables,plans,proof


def source_check(root=ROOT):
    text=(root/SOURCE).read_text()
    policy=read(root/'tools/report_policy.json')
    from check_report_policy import body_policy_errors
    errors=body_policy_errors([(str(SOURCE),text)],{},{},policy['forbidden_body_patterns'])
    errors+=summary_prose_errors(text,str(SOURCE),policy['summary']['forbidden_patterns'])
    assert not errors,'\n'.join(errors)
    from report_summary_math import source_check as math_source_check
    equations=math_source_check(root,text)
    tables,plans,proof=inputs(root)
    # 从有效原始节点独立重建六张窗口表，不能只比较Word与复制出的JSON。
    import pandas as pd
    from matrix_planning_windows import records
    matrix_source=root/policy['matrix_display']['source_csv']
    raw_cells=records(pd.read_csv(matrix_source))
    for key in [k for k in tables if k.startswith('lookup_matrix_')]:
        cells=[r for r in raw_cells if r['表键']==key]
        actual=[v for row in tables[key]['rows']for v in row[2:]]
        assert actual==[r['推荐窗口']for r in cells],'原始节点与矩阵窗口不一致：'+key
    keys=re.findall(r'\[\[SUMMARY_TABLE:([^|]+)\|',text)
    assert len(keys)==len(set(keys))==13 and set(keys)==set(tables),'成果总结表格引用与当前结果不一致'
    heads=re.findall(r'^## (.+)$',text,re.M)
    assert len(heads)==4 and [s[:2]for s in heads]==['一、','二、','三、','四、']
    assert not re.search('常州|武高新|待填|TODO|撰稿人：',text)
    # 同一来源重复沿用同号；源稿与最终视图分别核对引用首次出现顺序。
    check_citations(text)
    costs={c:sum(plans[r,c]['cost_npv_10k']for r in ['pizhou','city'])for c in ['rigid','elastic_capacity']}
    diff=costs['rigid']-costs['elastic_capacity']
    for amount in [f(costs['rigid']),f(costs['elastic_capacity']),f(diff),f(diff/costs['rigid']*100)]:assert amount in text,'正文未对应锁定费用：'+amount
    for r in ['pizhou','city']:
        a,b=plans[r,'rigid'],plans[r,'elastic_capacity']
        for k in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']:
            value=f(abs(sum(x[k]for x in b['annual'])-sum(x[k]for x in a['annual'])))
            assert value+'万元' in text,'措施费用差未按完整精度计算：'+r+'/'+value
    return dict(状态='通过',阶段='source',数据核验=proof,表格数=len(keys),推荐矩阵单元数=288,公式来源核验=equations,正文源SHA256=sha(root/SOURCE))


def summary_prose_errors(text,location,patterns):
    errors=[]
    for i,line in enumerate(text.splitlines(),1):
        for rule,pattern in patterns.items():
            if re.search(pattern,line):errors.append(f'{location}:{i}: {rule}: {line}')
    return errors


def check_citations(text):
    body,refs=text.split('参考依据',1)
    first=[]
    for mark in re.findall(r'\[([\d,，—–-]+)\]',body):
        for part in re.split('[,，]',mark):
            ends=re.split('[—–-]',part)
            nums=range(int(ends[0]),int(ends[-1])+1)
            for num in nums:
                if num not in first:first.append(num)
    records=[int(n)for n in re.findall(r'(?:^|\n)\s*\[(\d+)\]',refs)]
    assert first==records==list(range(1,7)),('引文次序或参考文献对应错误',first,records)


def template_parts(root):
    with ZipFile(root/TEMPLATE)as z:parts={n:z.read(n)for n in z.namelist()}
    doc=E.fromstring(parts['word/document.xml']);body=doc.find(Q('body'));paras=list(body)
    prototypes={kind:deepcopy(paras[i])for kind,i in [('title',0),('unit',1),('body',4),('h1',5),('h2',6),('caption',38)]}
    return parts,doc,prototypes


def run_from(proto,text,bold=False,size=None):
    r=E.Element(Q('r'));base=proto.find('.//'+Q('rPr'))
    pr=deepcopy(base)if base is not None else E.Element(Q('rPr'))
    for n in list(pr):
        if E.QName(n).localname in ['highlight','ligatures']:pr.remove(n)
    if size:
        for name in ['sz','szCs']:
            old=pr.find(Q(name))
            if old is not None:pr.remove(old)
            pr.append(node(name,val=size))
    if bold and pr.find(Q('b'))is None:pr.append(node('b'))
    r.append(pr);t=node('t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text;r.append(t)
    return r


def paragraph(proto,text,kind):
    p=deepcopy(proto)
    for e in list(p):
        if e.tag!=Q('pPr'):p.remove(e)
    pp=p.find(Q('pPr'))
    if pp is None:pp=node('pPr');p.insert(0,pp)
    # 模板原排版参数原样保留；仅补标题与后段同页及段内孤行控制。
    if kind in ['h1','h2','caption'] and pp.find(Q('keepNext'))is None:pp.append(node('keepNext'))
    if pp.find(Q('widowControl'))is None:pp.append(node('widowControl'))
    if kind=='caption':
        for n in list(pp):
            if n.tag in [Q('ind'),Q('jc')]:pp.remove(n)
        pp.append(node('ind',firstLine=0,firstLineChars=0,hanging=0,hangingChars=0,left=0,right=0,leftChars=0,rightChars=0,start=0,end=0,startChars=0,endChars=0))
        pp.append(node('jc',val='center'))
    if text.startswith('式中'):
        from report_summary_math import INDENTS
        for old in list(pp.findall(Q('ind'))):pp.remove(old)
        pp.append(node('ind',**{name:0 for name in INDENTS}))
    # “一是…”沿用模板的楷体加粗领句，后接仿宋正文。
    if kind=='title':
        left,right=text.split('电网',1)
        r=run_from(proto,left+'电网');r.append(node('br'));p.append(r)
        p.append(run_from(proto,right))
        return p
    for token in re.split(r'(\*\*.*?\*\*)',text):
        if not token:continue
        if token.startswith('**'):
            r=run_from(proto,token[2:-2],True)
            fonts=r.find(Q('rPr')).find(Q('rFonts'))
            for a in ['ascii','hAnsi','eastAsia','cs']:fonts.set(Q(a),'方正楷体_GBK')
        else:r=run_from(proto,token)
        if text.startswith('式中') and not token.startswith('**'):
            # 简单行内变量保留可编辑文字，显式设置字形及上下标。
            symbols={'Cplan':('C','plan','subscript'),'Ce':('C','e','subscript'),
                     'ET':('E','T','subscript'),'EB':('E','B','subscript'),'EL':('E','L','subscript'),
                     'qout':('q','out','superscript'),'qin':('q','in','superscript'),
                     'B+':('B','+','superscript'),'B−':('B','−','superscript'),
                     'Si,j':('S','i,j','subscript'),'Si':('S','i','subscript'),
                     'Sav':('S','av','superscript')}
            pattern='('+'|'.join(map(re.escape,sorted(symbols,key=len,reverse=True)))+r'|cosφ|MVA|MW|[A-Za-zωφ])'
            for segment in re.split(pattern,token):
                if not segment:continue
                entries=[(segment,None,False)]
                if segment in symbols:
                    base,index,align=symbols[segment]
                    entries=[(base,None,True),(index,align,index in ['e','i','i,j'])]
                elif segment=='cosφ':entries=[('cos',None,False),('φ',None,True)]
                elif re.fullmatch('[A-Za-zωφ]',segment):entries=[(segment,None,True)]
                for value,align,italic in entries:
                    sr=run_from(proto,value);rp=sr.find(Q('rPr'))
                    if re.search('[A-Za-zωφ]',value):
                        fonts=rp.find(Q('rFonts'))
                        for name in ['ascii','hAnsi','cs']:fonts.set(Q(name),'Times New Roman')
                        for name in ['i','iCs']:
                            for old in list(rp.findall(Q(name))):rp.remove(old)
                            rp.append(node(name,val=int(italic)))
                    if align:rp.append(node('vertAlign',val=align))
                    p.append(sr)
        else:p.append(r)
    return p


def make_table(data,proto):
    t=node('tbl');pr=node('tblPr');pr.append(node('tblW',w=8306,type='dxa'));pr.append(node('jc',val='center'));pr.append(node('tblLayout',type='fixed'))
    borders=node('tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:borders.append(node(side,val='single',sz=4,color='000000'))
    pr.append(borders);m=node('tblCellMar')
    for side,v in [('top',20),('bottom',20),('left',35),('right',35)]:m.append(node(side,w=v,type='dxa'))
    pr.append(m);t.append(pr);grid=node('tblGrid')
    assert sum(data['widths'])==8306
    for width in data['widths']:grid.append(node('gridCol',w=width))
    t.append(grid)
    allrows=[data['headers']]+data['rows']
    for ri,values in enumerate(allrows):
        tr=node('tr');rp=node('trPr');rp.append(node('cantSplit'))
        if ri==0:rp.append(node('tblHeader'))
        tr.append(rp)
        for value,width in zip(values,data['widths']):
            tc=node('tc');cp=node('tcPr');cp.append(node('tcW',w=width,type='dxa'));cp.append(node('vAlign',val='center'));tc.append(cp)
            p=node('p');pp=node('pPr');pp.append(node('jc',val='center'));pp.append(node('ind',firstLine=0,firstLineChars=0,left=0,right=0,hanging=0,hangingChars=0,leftChars=0,rightChars=0));pp.append(node('spacing',before=0,after=0,line=370,lineRule='exact'));pp.append(node('snapToGrid',val=0))
            if ri<len(allrows)-1:pp.append(node('keepNext'))
            p.append(pp);p.append(run_from(proto,str(value),bold=ri==0,size=24));tc.append(p);tr.append(tc)
        t.append(tr)
    return t


def build(root=ROOT):
    result=source_check(root);tables,plans,proof=inputs(root);parts,doc,protos=template_parts(root);body=doc.find(Q('body'));sect=deepcopy(body.find(Q('sectPr')))
    for e in list(body):body.remove(e)
    blocks=[]
    for block in (root/SOURCE).read_text().split('\n\n'):
        block=block.strip()
        if not block:continue
        if block.startswith('$$'):
            from report_summary_math import equation_table,formula_number
            body.append(equation_table(root,block));blocks.append({'type':'equation','number':formula_number(block)})
            continue
        if block.startswith('# '):kind='title';s=block[2:]
        elif block.startswith('## '):kind='h1';s=block[3:]
        elif block.startswith('### '):kind='h2';s=block[4:]
        elif block.startswith('（供稿单位'):kind='unit';s=block
        elif block.startswith('[[SUMMARY_TABLE:'):
            key,title=re.fullmatch(r'\[\[SUMMARY_TABLE:([^|]+)\|(.+)\]\]',block).groups()
            body.append(paragraph(protos['caption'],title,'caption'));body.append(make_table(tables[key],protos['body']));blocks.append({'type':'table','key':key,'title':title,'rows':len(tables[key]['rows'])});continue
        else:kind='body';s=block
        body.append(paragraph(protos[kind],s,kind));blocks.append({'type':kind,'text':re.sub(r'\*\*','',s)})
    body.append(sect);parts['word/document.xml']=xml(doc)
    settings=E.fromstring(parts['word/settings.xml'])
    for e in list(settings.findall(Q('trackRevisions'))):settings.remove(e)
    from report_summary_math import qm
    math_pr=settings.find(qm('mathPr'))
    if math_pr is None:math_pr=E.SubElement(settings,qm('mathPr'))
    math_font=math_pr.find(qm('mathFont'))
    if math_font is None:math_font=E.SubElement(math_pr,qm('mathFont'))
    math_font.set(qm('val'),'Times New Roman')
    parts['word/settings.xml']=xml(settings)
    # 继承模板的字体、段落样式、节与纸张属性；不把模板旧图像带入新成果。
    relpath='word/_rels/document.xml.rels';rels=E.fromstring(parts[relpath])
    for rel in list(rels):
        if rel.get('Type','').endswith(('/image','/comments')):rels.remove(rel)
    parts[relpath]=xml(rels)
    for name in list(parts):
        if name.startswith('word/media/')or name.startswith('word/comments'):parts.pop(name)
    core=E.fromstring(parts['docProps/core.xml']);dcn={'dc':'http://purl.org/dc/elements/1.1/','cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
    for tag,value in [('dc:title','徐州地区110千伏电网容载比弹性指标优化研究成果总结'),('dc:creator','徐州公司'),('cp:lastModifiedBy','xh')]:
        pre,local=tag.split(':');e=core.find('{'+dcn[pre]+'}'+local)
        if e is None:e=E.SubElement(core,'{'+dcn[pre]+'}'+local)
        e.text=value
    parts['docProps/core.xml']=xml(core)
    # 旧模板页数缓存清空，实际页数由WPS导出登记。
    app=E.fromstring(parts['docProps/app.xml'])
    for e in app:
        if E.QName(e).localname in ['Pages','Words','Characters','CharactersWithSpaces']:e.text='0'
    parts['docProps/app.xml']=xml(app)
    path=root/OUT;path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w',ZIP_DEFLATED)as z:
        for name,value in parts.items():z.writestr(name,value)
    rv=root/REVIEW;rv.mkdir(parents=True,exist_ok=True)
    (rv/'表格数据.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    files=[SOURCE,TEMPLATE,Path('研究报告/甲方反馈/10.11/供电公司讨论稿.docx'),Path('研究报告/04_word/研究报告终稿.docx'),Path('研究报告/02图表/当前版/计算表.json'),Path('研究报告/01研究推荐/当前版/后续报告案例采用版本.json'),Path('skills/11.md')]
    manifest={'用途':'成果总结原始内容、模板及锁定数据依据','输入':{str(p):sha(root/p)for p in files},'成果总结DOCX':sha(path),'表格数据':sha(rv/'表格数据.json'),'段落与表格':blocks,'数据核验':proof,'格式说明':'继承模板标题22磅小标宋、一级标题18磅黑体、二级标题16磅楷体加粗、正文16磅仿宋、28磅固定行距、A4及左右3.175厘米上下2.54厘米页边距。模板未含表格，新增表格按项目居中规则采用12磅仿宋、18.5磅固定行距。保留模板四部分结构及一是领句语体。'}
    manifest['公式依据']=result['公式来源核验']
    manifest['维护代码SHA256']={name:sha(root/name)for name in ['tools/report_summary.py','tools/report_summary_math.py','tools/build_current_report.py']}
    (rv/'来源及构建登记.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    docx_check(root)
    print(json.dumps({'状态':'源稿及原生Word检查通过','输出':str(OUT)},ensure_ascii=False))


def docx_check(root=ROOT):
    result=source_check(root);tables,_,_=inputs(root);_,template,protos=template_parts(root)
    with ZipFile(root/OUT)as z:
        doc=E.fromstring(z.read('word/document.xml'));settings=E.fromstring(z.read('word/settings.xml'))
        assert not doc.xpath('//w:ins|//w:del|//w:commentRangeStart',namespaces=NS)
        assert not settings.findall(Q('trackRevisions'))
        with ZipFile(root/TEMPLATE)as t:assert z.read('word/styles.xml')==t.read('word/styles.xml'),'模板样式须完整继承'
    assert E.tostring(doc.find('.//'+Q('sectPr')))==E.tostring(template.find('.//'+Q('sectPr'))),'纸张与页边距变化'
    body=doc.find(Q('body'));texts=[''.join(e.xpath('.//w:t/text()',namespaces=NS))for e in body if e.tag==Q('p')]
    expected=[]
    for block in (root/SOURCE).read_text().split('\n\n'):
        block=block.strip()
        if not block:continue
        if block.startswith('$$'):continue
        if block.startswith('[[SUMMARY_TABLE:'):block=block.split('|',1)[1][:-2]
        else:block=re.sub(r'^#{1,3} ','',block);block=block.replace('**','')
        expected.append(block)
    assert texts==expected,'源稿与Word段落/图表题不一致'
    actual=doc.xpath('//w:body/w:tbl[not(w:tblPr/w:tblCaption[@w:val="ReportEquation"])]',namespaces=NS)
    keys=re.findall(r'\[\[SUMMARY_TABLE:([^|]+)\|',(root/SOURCE).read_text())
    for table,key in zip(actual,keys):
        values=[[''.join(c.xpath('.//w:t/text()',namespaces=NS))for c in tr.findall(Q('tc'))]for tr in table.findall(Q('tr'))]
        assert values==[tables[key]['headers']]+tables[key]['rows'],'Word表格数据错误：'+key
        assert table.find('./'+Q('tblPr')+'/'+Q('jc')).get(Q('val'))=='center'
    assert len(actual)==13
    for p in body.findall(Q('p')):
        text=''.join(p.xpath('.//w:t/text()',namespaces=NS));pp=p.find(Q('pPr'))
        if re.match(r'^表[0-9]+ ',text):
            assert pp.find(Q('jc')).get(Q('val'))=='center'
            assert all(v=='0'for v in pp.find(Q('ind')).attrib.values())
        if text.startswith(('一、','二、','三、','四、')):proto=protos['h1']
        elif text.startswith('（')and not text.startswith('（供稿'):proto=protos['h2']
        elif text in texts[:1]:proto=protos['title']
        else:continue
        for tag in ['spacing','ind','jc']:
            expected_prop=proto.find('./'+Q('pPr')+'/'+Q(tag));actual_prop=pp.find(Q(tag))
            assert (expected_prop is None and actual_prop is None)or(dict(expected_prop.attrib)==dict(actual_prop.attrib)),('段落未继承模板',text,tag)
    from report_summary_math import check_native
    math_result=check_native(root,root/OUT)
    for p in body.findall(Q('p')):
        if ''.join(p.xpath('.//w:t/text()',namespaces=NS)).startswith('式中'):
            from report_summary_math import INDENTS
            assert all(p.find('./'+Q('pPr')+'/'+Q('ind')).get(Q(name))=='0' for name in INDENTS),'式中段落缩进须归零'
    result.update(阶段='docx',WordSHA256=sha(root/OUT),表格数=len(actual),表格数据逐格核验='通过',原生公式核验=math_result,模板样式及版心='通过')
    (root/REVIEW/'原生Word核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def final_check(root=ROOT):
    import pymupdf
    result=docx_check(root);p=root/PDF;pdf=pymupdf.open(p)
    assert 'wps' in str(pdf.metadata).lower()or'kingsoft'in str(pdf.metadata).lower(),'须由WPS原生导出'
    normal=lambda s:re.sub(r'\s+','',s).replace('−','-').replace('－','-')
    alltext=normal(''.join(page.get_text()for page in pdf))
    with ZipFile(root/OUT)as z:doc=E.fromstring(z.read('word/document.xml'))
    missing=[]
    for p in doc.xpath('//w:body//w:p',namespaces=NS):
        t=normal(''.join(p.xpath('.//w:t/text()',namespaces=NS)))
        if t and t not in alltext:missing.append(t)
    assert not missing,'PDF未完整显示Word内容：'+str(missing[:8])
    findings=[]
    for i,page in enumerate(pdf):
        assert abs(page.rect.width-595.3)<1 and abs(page.rect.height-841.9)<1
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if span['text'].strip():
                        x0,y0,x1,y1=span['bbox']
                        # 模板允许行末中文标点悬挂；保留字形外框至一个汉字宽度。
                        right=522 if re.search('[，。；：？！、）”]$',span['text']) else 508
                        if x0<87 or x1>right or y0<65 or y1>780:findings.append([i+1,span['text'],span['bbox']])
    assert not findings,('PDF文字越出版心',findings[:6])
    check_citations('\n'.join(page.get_text()for page in pdf))
    from report_summary_math import check_pdf as check_math_pdf
    result['PDF公式位置核验']=check_math_pdf(root,root/OUT,pdf)
    result.update(阶段='final',PDFSHA256=sha(root/PDF),PDF页数=len(pdf),排版引擎=pdf.metadata.get('creator'),逐段与逐格文本回读='通过',版心边界='通过')
    visual=root/REVIEW/'逐页审阅.json'
    if visual.exists():
        v=read(visual);assert v['PDFSHA256']==sha(root/PDF)and v['WordSHA256']==sha(root/OUT)and v['状态']=='通过'and len(v['逐页记录'])==len(pdf),'逐页审阅须对应最终Word及PDF'
        result['人工版面审阅']='通过'
    else:result['人工版面审阅']='待完成'
    if result['人工版面审阅']!='通过':result['状态']='待逐页复核'
    (root/REVIEW/'最终WPS核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--rebuild',action='store_true');parser.add_argument('--stage',choices=['source','docx','final'],default='final');parser.add_argument('--accept-wps-pdf',type=Path)
    args=parser.parse_args(argv);root=args.root.resolve()
    if args.rebuild:build(root);return
    if args.accept_wps_pdf:
        assert args.accept_wps_pdf.is_file()
        if args.accept_wps_pdf.resolve()!=(root/PDF).resolve():shutil.copy2(args.accept_wps_pdf,root/PDF)
    result={'source':source_check,'docx':docx_check,'final':final_check}[args.stage](root)
    if args.stage=='final' and not args.accept_wps_pdf:
        assert result['人工版面审阅']=='通过','最终检查须先完成对应PDF的逐页审阅'
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
