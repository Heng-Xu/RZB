"""只读提取10.23成果总结的批注、逐处修订及对应上下文。"""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('研究报告/甲方反馈/10.23/成果总结.docx')
REVIEW=Path('研究报告/05_review/当前版/1023成果总结重构')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W};q=lambda n:'{'+W+'}'+n

def text(node):
    return ''.join(node.xpath('.//w:t[not(ancestor::w:del)]/text()',namespaces=NS))

def extract(root=ROOT):
    path=root/BASE
    with ZipFile(path)as z:
        doc=E.fromstring(z.read('word/document.xml'))
        comments=E.fromstring(z.read('word/comments.xml'))
    blocks=list(doc.find(q('body')));revisions=[];paragraphs=[]
    for i,block in enumerate(blocks):
        nodes=block.xpath('.//w:ins|.//w:del',namespaces=NS)
        if not nodes:continue
        old=''.join(block.xpath('.//w:t[not(ancestor::w:ins) and not(ancestor::w:del)]/text() | .//w:delText[not(ancestor::w:ins)]/text()',namespaces=NS))
        paragraphs.append({'基线块':i,'修订前':old,'甲方修订后':text(block),'修订ID':[n.get(q('id'))for n in nodes]})
        for n in nodes:
            revisions.append({'基线块':i,'ID':n.get(q('id')),'类型':'插入'if n.tag==q('ins')else'删除','作者':n.get(q('author')),'原始日期':n.get(q('date')),'文本':''.join(n.xpath('.//w:t/text()|.//w:delText/text()',namespaces=NS)),'段落标记':n.getparent().tag==q('rPr')})
    notes=[]
    for c in comments:
        cid=c.get(q('id'));active=False;anchor=[]
        for node in doc.iter():
            if node.tag==q('commentRangeStart')and node.get(q('id'))==cid:active=True
            elif node.tag==q('commentRangeEnd')and node.get(q('id'))==cid:active=False
            elif active and node.tag==q('t'):anchor.append(node.text or '')
        notes.append({'ID':cid,'作者':c.get(q('author')),'原始日期':c.get(q('date')),'批注':text(c),'锚定文本':''.join(anchor)})
    result={'基线':str(BASE),'SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'批注数':len(notes),'修订数':len(revisions),'批注':notes,'逐处修订':revisions,'按段落汇总':paragraphs}
    review=root/REVIEW;review.mkdir(parents=True,exist_ok=True)
    (review/'甲方批注与修订提取.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    lines=['# 10.23成果总结：甲方批注与修订提取','',f'基线：`{BASE}`。原文件只读保留；共{len(notes)}条批注、{len(revisions)}处修订。日期保留原文件记录，不作时区推断或改写。','',
    '## 本轮采用的修改依据','',
    '- 批注明确要求“不要参考文献”，正文取消文献编号和文末参考依据，来源另存核验记录。',
    '- 开篇将问题由单一增容判断调整为年最大净负荷平均增长率难以单独确定区域容载比，强调“多参数弹性容载比推荐矩阵”。',
    '- 删除容载比定义和增长率详细计算介绍，压缩基期容量、年度承接等过程细节。',
    '- 导则表述取消月份和具体条款号，保留导则名称及供电安全、转供要求。',
    '- 转供段落已着手压缩，原稿存在未完成句和重复用词，本轮依据原报告补全技术关系。',
    '- 用户追加要求：参照10.22模板重构为约12页的凝练成果总结，优先呈现研究成果和工程含义，适量复用已有图件。','',
    '## 批注原文','']
    for c in notes:lines += [f"批注{c['ID']}｜{c['作者']}｜{c['原始日期']}",f"锚定：{c['锚定文本']}",f"原文：{c['批注']}",'']
    lines += ['## 按段落核对前后文','']
    for p in paragraphs:lines += [f"基线块{p['基线块']}，修订ID：{','.join(p['修订ID'])}",f"修订前：{p['修订前']}",f"甲方修订后：{p['甲方修订后'] or '（本段删除）'}",'']
    lines += ['## 逐处修订原文','']
    for r in revisions:lines += [f"- ID {r['ID']}｜基线块{r['基线块']}｜{r['类型']}｜{r['作者']}｜{r['原始日期']}：{r['文本'] or '（段落标记）'}"]
    (review/'甲方批注与修订提取.md').write_text('\n'.join(lines)+'\n')
    return result

if __name__=='__main__':
    r=extract();print(json.dumps({k:r[k]for k in ['基线','SHA256','批注数','修订数']},ensure_ascii=False))
