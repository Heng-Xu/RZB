"""逐单元格比较当前Markdown数据表与Word，公式布局表单独由文档核验检查。"""
from pathlib import Path
import hashlib,json,re
from docx import Document

HERE=Path(__file__).resolve().parent
REPORT=HERE.parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source=REPORT/'03_MD/当前版/研究报告装配稿.md'
    word=REPORT/'04_word/研究报告终稿.docx'
    blocks=re.findall(r'^\|.*(?:\n\|.*)*',source.read_text(),re.M)
    expected=[]
    for block in blocks:
        rows=[]
        for line in block.splitlines():
            if re.fullmatch(r'[| :\-]+',line):continue
            assert '\\|' not in line,'带转义竖线的表格需扩展解析后再核验'
            rows.append([cell.strip() for cell in line.strip().strip('|').split('|')])
        expected.append(rows)
    doc=Document(word)
    tables=[t for t in doc.tables if t._tbl.xpath('./w:tblPr/w:tblCaption/@w:val')!=['ReportEquation']]
    actual=[[[cell.text for cell in row.cells] for row in table.rows] for table in tables]
    differences=[]
    if len(expected)!=len(actual):
        differences.append({'Markdown表数':len(expected),'Word数据表数':len(actual)})
    for i,(left,right) in enumerate(zip(expected,actual),1):
        if left!=right:differences.append({'数据表序号':i,'Markdown':left,'Word':right})
    result={'状态':'通过' if not differences else '未通过','表格':len(actual),
            '比较方式':'按正文顺序逐行、逐单元格精确比较全部表头及文字数值',
            '单元格':sum(len(row) for table in actual for row in table),
            '不一致':differences,'WordSHA256':sha(word),'装配稿SHA256':sha(source)}
    (HERE/'Word表格内容复核.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    assert not differences,differences
    print(json.dumps({key:result[key] for key in ('状态','表格','单元格')},ensure_ascii=False))

if __name__=='__main__':main()
