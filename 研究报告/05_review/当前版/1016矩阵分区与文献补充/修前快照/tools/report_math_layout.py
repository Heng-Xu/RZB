"""独立公式：对称三栏承载原生OMML，由文字段落居中，消除显示数学与表格对齐叠加。"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

MARKER='ReportEquation'
INDENTS=['firstLine','firstLineChars','hanging','hangingChars','left','right','start','end',
         'leftChars','rightChars','startChars','endChars']

def configure_equation_table(table,paragraph):
    """只改变布局；保留公式原生对象及全部字符、分式和矩阵结构。"""
    t=table._tbl;p=paragraph._p
    pr=t.tblPr
    for tag in ['tblStyle','tblLook','tblpPr','tblInd','tblCellMar','tblCaption']:
        for e in pr.findall(qn('w:'+tag)):pr.remove(e)
    ind=OxmlElement('w:tblInd');ind.set(qn('w:w'),'0');ind.set(qn('w:type'),'dxa');pr.insert(2,ind)
    mar=OxmlElement('w:tblCellMar')
    for side in ['top','left','bottom','right']:
        node=OxmlElement('w:'+side);node.set(qn('w:w'),'0');node.set(qn('w:type'),'dxa');mar.append(node)
    pr.append(mar)
    caption=OxmlElement('w:tblCaption');caption.set(qn('w:val'),MARKER);pr.append(caption)
    for cell in table.rows[0].cells:
        cp=cell._tc.get_or_add_tcPr()
        for node in cp.findall(qn('w:tcMar')):cp.remove(node)
        valign=cp.find(qn('w:vAlign'));cm=OxmlElement('w:tcMar')
        for side in ['top','left','bottom','right']:
            node=OxmlElement('w:'+side);node.set(qn('w:w'),'0');node.set(qn('w:type'),'dxa');cm.append(node)
        cp.insert(list(cp).index(valign) if valign is not None else len(cp),cm)
        for pp in cell.paragraphs:
            pi=pp._p.get_or_add_pPr()
            for node in pi.findall(qn('w:pStyle')):pi.remove(node)
            pin=pi.find(qn('w:ind'))
            if pin is None:pin=OxmlElement('w:ind');pi.append(pin)
            pin.attrib.clear()
            for name in INDENTS:pin.set(qn('w:'+name),'0')
    # 不使用oMathPara的独立数学段落对齐；独立占行的原生oMath由宿主段落居中。
    for mp in list(p.findall(qn('m:oMathPara'))):
        offset=list(p).index(mp)
        for math in mp.findall(qn('m:oMath')):
            mp.remove(math);p.insert(offset,math);offset+=1
        p.remove(mp)
    jc=p.get_or_add_pPr().find(qn('w:jc'))
    if jc is None:jc=OxmlElement('w:jc');p.get_or_add_pPr().append(jc)
    jc.set(qn('w:val'),'center')

def equation_tables(doc):
    return [t for t in doc.tables if t._tbl.xpath('./w:tblPr/w:tblCaption/@w:val')==[MARKER]]

def check_equation_layout(doc):
    tables=equation_tables(doc)
    for i,table in enumerate(tables,1):
        label=f'独立公式{i}'
        assert len(table.rows)==1 and len(table.columns)==3,label+'须采用对称三栏'
        t=table._tbl
        assert t.xpath('./w:tblPr/w:jc/@w:val')==['center'],label+'表格未居中'
        assert t.xpath('./w:tblPr/w:tblLayout/@w:type')==['fixed'],label+'须固定栏宽'
        assert not t.xpath('./w:tblPr/w:tblpPr'),label+'不得浮动'
        grid=list(map(int,t.xpath('./w:tblGrid/w:gridCol/@w:w')))
        assert grid[0]==grid[2],label+'左右栏须等宽'
        assert sum(grid)==int(t.xpath('./w:tblPr/w:tblW/@w:w')[0]),label+'栏宽总和须等于表宽'
        tc=t.xpath('./w:tr/w:tc')
        assert [int(x.xpath('./w:tcPr/w:tcW/@w:w')[0]) for x in tc]==grid,label+'单元格宽度与网格不符'
        for c in tc:
            for side in ['left','right']:
                assert c.xpath('./w:tcPr/w:tcMar/w:'+side+'/@w:w')==['0'],label+'单元格内边距须清零'
            for p in c.xpath('./w:p'):
                assert all(p.xpath('./w:pPr/w:ind/@w:'+name)==['0'] for name in INDENTS),label+'段落缩进须全部清零'
        p=tc[1].xpath('./w:p')[0]
        assert p.xpath('./w:pPr/w:jc/@w:val')==['center'],label+'公式宿主段落未居中'
        assert len(p.xpath('./m:oMath'))==1 and not p.xpath('./m:oMathPara'),label+'须由宿主段落承载单个原生公式'
        assert not p.xpath('./w:r/w:t'),label+'公式主体不得混入式号或空格'
        assert tc[2].xpath('./w:p/w:pPr/w:jc/@w:val')==['right'],label+'式号未右置'
    return tables
