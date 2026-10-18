"""在甲方原DOCX包内增量修订，保留批注与既有修订，并检验接受/拒绝视图。"""
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import argparse,json,re,shutil
from lxml import etree as E

from report_annual_update import ROOT,REVIEW
from revise_current_discussion import Reviser,qn,NS

TARGET=ROOT/'研究报告/甲方反馈/10.17/10.17研究报告.docx'
BASE=REVIEW/'修前原件/研究报告/甲方反馈/10.17/10.17研究报告.docx'
CLEAN=REVIEW/'目标清稿.docx'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
ALLNS={**NS,'m':M,'a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}

def package(path):
    with ZipFile(path) as z:return {i.filename:z.read(i) for i in z.infolist()}

def xml(data):return E.fromstring(data)
def dump(node):return E.tostring(node,encoding='UTF-8',xml_declaration=True,standalone=True)
def text(node):return ''.join(node.xpath('.//w:t[not(ancestor::w:del)]/text()|.//m:t[not(ancestor::w:del)]/text()',namespaces=ALLNS))
def fingerprint(node,parts):
    result=E.QName(node).localname+':'+text(node)
    if node.tag==qn('tbl') and node.xpath('./w:tblPr/w:tblCaption[@w:val="ReportEquation"]',namespaces=NS):
        result+=':display-math-container:'+str(bool(node.xpath('.//m:oMathPara',namespaces=ALLNS)))
    for rid in node.xpath('.//@r:embed',namespaces={'r':R}):
        rels=xml(parts['word/_rels/document.xml.rels'])
        rel=next(r for r in rels if r.get('Id')==rid)
        result+=':image:'+sha256(parts['word/'+rel.get('Target')]).hexdigest()
    return result

def descriptor(node):
    value=text(node)
    if node.tag==qn('tbl'):
        if node.xpath('.//m:oMath',namespaces=ALLNS):return 'equation:'+value[-12:]
        return 'table:'+str(len(node.find(qn('tr')).findall(qn('tc'))))
    if node.xpath('.//w:drawing',namespaces=ALLNS):return 'drawing'
    if re.match(r'^[图表]\d+-\d+',value):return value.split(' ')[0]
    return E.QName(node).localname

class Editor(Reviser):
    def delete_block(self,node):
        paragraphs=[node] if node.tag==qn('p') else node.findall('.//'+qn('p'))
        if node.tag==qn('tbl'):
            for row in node.findall(qn('tr')):
                pr=row.find(qn('trPr'))
                if pr is None:pr=E.Element(qn('trPr'));row.insert(0,pr)
                pr.append(self.mark('del'))
        for p in paragraphs:
            pr=p.find(qn('pPr'))
            if pr is None:pr=E.Element(qn('pPr'));p.insert(0,pr)
            rp=pr.find(qn('rPr'))
            if rp is None:rp=E.SubElement(pr,qn('rPr'))
            rp.append(self.mark('del'))
            for child in list(p):
                if child.tag in [qn('pPr'),qn('commentRangeStart'),qn('commentRangeEnd'),qn('bookmarkStart'),qn('bookmarkEnd')]:continue
                pos=p.index(child);p.remove(child)
                for t in child.iter(qn('t')):t.tag=qn('delText')
                mark=self.mark('del');mark.append(child);p.insert(pos,mark)

    def insert_block(self,node):
        paragraphs=[node] if node.tag==qn('p') else node.findall('.//'+qn('p'))
        if node.tag==qn('tbl'):
            for row in node.findall(qn('tr')):
                pr=row.find(qn('trPr'))
                if pr is None:pr=E.Element(qn('trPr'));row.insert(0,pr)
                pr.append(self.mark('ins'))
        for p in paragraphs:
            pr=p.find(qn('pPr'))
            if pr is None:pr=E.Element(qn('pPr'));p.insert(0,pr)
            rp=pr.find(qn('rPr'))
            if rp is None:rp=E.SubElement(pr,qn('rPr'))
            rp.append(self.mark('ins'))
            for child in list(p):
                if child.tag in [qn('pPr'),qn('bookmarkStart'),qn('bookmarkEnd')]:continue
                pos=p.index(child);p.remove(child);mark=self.mark('ins');mark.append(child);p.insert(pos,mark)
        return node

def view(root,accept=True):
    root=deepcopy(root)
    for change in list(root.xpath('.//w:pPrChange[@w:author="xh"]',namespaces=NS)):
        parent=change.getparent()
        if accept:parent.remove(change)
        else:parent.getparent().replace(parent,deepcopy(change[0]))
    target='del' if accept else 'ins'
    for row in list(root.xpath('.//w:tr',namespaces=NS)):
        if row.xpath('./w:trPr/w:'+target+'[@w:author="xh"]',namespaces=NS):row.getparent().remove(row)
    for p in list(root.xpath('.//w:p',namespaces=NS)):
        if p.xpath('./w:pPr/w:rPr/w:'+target+'[@w:author="xh"]',namespaces=NS):p.getparent().remove(p)
    for tbl in list(root.xpath('.//w:tbl[not(w:tr)]',namespaces=NS)):tbl.getparent().remove(tbl)
    for change in list(root.xpath('.//w:ins[@w:author="xh"]|.//w:del[@w:author="xh"]',namespaces=NS)):
        parent=change.getparent()
        if parent is None:continue
        if E.QName(change).localname==target:
            parent.remove(change);continue
        pos=parent.index(change)
        for child in list(change):
            for item in child.iter(qn('delText')):item.tag=qn('t')
            parent.insert(pos,child);pos+=1
        parent.remove(change)
    return root

def apply():
    if TARGET.exists():
        known={sha256(BASE.read_bytes()).hexdigest()}
        previous=REVIEW/'原文件修订核验.json'
        if previous.exists():known.add(json.loads(previous.read_text())['修后SHA256'])
        assert sha256(TARGET.read_bytes()).hexdigest() in known,'原文件已被外部编辑，须先保留并合并用户改动'
    old,new=package(BASE),package(CLEAN)
    root=xml(old['word/document.xml']);goal=xml(new['word/document.xml'])
    body=root.find(qn('body'));wanted=goal.find(qn('body'))
    original_expected=list(deepcopy(body))
    oldnodes=list(body);newnodes=list(wanted)
    editor=Editor(root)
    rels=xml(old['word/_rels/document.xml.rels']);newrels=xml(new['word/_rels/document.xml.rels'])
    contenttypes=xml(old['[Content_Types].xml']);newtypes=xml(new['[Content_Types].xml'])
    replacements={};relmap={}
    styles=xml(old['word/styles.xml']);goal_styles=xml(new['word/styles.xml'])
    old_style_ids={n.get(qn('styleId')) for n in styles}
    old_style_names={n.find(qn('name')).get(qn('val')):n.get(qn('styleId')) for n in styles if n.find(qn('name')) is not None}
    stylemap={}
    for style in goal_styles:
        ident=style.get(qn('styleId'));name=style.find(qn('name'))
        if ident in old_style_ids:stylemap[ident]=ident
        elif name is not None and name.get(qn('val')) in old_style_names:stylemap[ident]=old_style_names[name.get(qn('val'))]
        else:stylemap[ident]='Report1017_'+ident
    added_style_ids=set()
    def map_styles(node):
        for prop in node.xpath('.//w:pStyle|.//w:rStyle|.//w:tblStyle',namespaces=NS):
            ident=prop.get(qn('val'));mapped=stylemap.get(ident,ident);prop.set(qn('val'),mapped)
            if mapped in old_style_ids or mapped in added_style_ids:continue
            source=deepcopy(next(s for s in goal_styles if s.get(qn('styleId'))==ident));source.set(qn('styleId'),mapped)
            for link in source.xpath('./w:basedOn|./w:next|./w:link',namespaces=NS):link.set(qn('val'),stylemap.get(link.get(qn('val')),link.get(qn('val'))))
            styles.append(source);added_style_ids.add(mapped)
    used_bookmarks={n.get(qn('name')) for n in root.findall('.//'+qn('bookmarkStart'))}
    max_bookmark=max([int(n.get(qn('id'))) for n in root.findall('.//'+qn('bookmarkStart'))]+[0])
    max_drawing=max([int(v) for v in root.xpath('.//wp:docPr/@id',namespaces=ALLNS)]+[0])
    def copy_node(node):
        nonlocal max_bookmark,max_drawing
        node=deepcopy(node)
        map_styles(node)
        for item in node.iter():
            for attr,val in list(item.attrib.items()):
                if not attr.startswith('{'+R+'}') or attr.endswith('}anchor'):continue
                if val not in relmap:
                    rel=deepcopy(next(r for r in newrels if r.get('Id')==val));newid='rIdReportRevision'+str(len(relmap)+1);rel.set('Id',newid)
                    if rel.get('TargetMode')!='External':
                        target=rel.get('Target');source='word/'+target
                        assert source in new and '..' not in target,target
                        target='media/report_revision_'+sha256(new[source]).hexdigest()[:16]+Path(target).suffix
                        replacements['word/'+target]=new[source];rel.set('Target',target)
                        extension=Path(target).suffix[1:]
                        if not any(t.get('Extension')==extension for t in contenttypes):
                            contenttypes.append(deepcopy(next(t for t in newtypes if t.get('Extension')==extension)))
                    rels.append(rel);relmap[val]=newid
                item.set(attr,relmap[val])
        # 沿用原章节书签；新复制段落不引入同名或同ID书签。
        bmap={}
        for mark in list(node.findall('.//'+qn('bookmarkStart'))):
            name=mark.get(qn('name'));oldid=mark.get(qn('id'))
            if name in used_bookmarks:
                bmap[oldid]=None;mark.getparent().remove(mark)
            else:
                used_bookmarks.add(name);max_bookmark+=1;bmap[oldid]=str(max_bookmark);mark.set(qn('id'),str(max_bookmark))
        for mark in list(node.findall('.//'+qn('bookmarkEnd'))):
            new_id=bmap.get(mark.get(qn('id')))
            if new_id is None:mark.getparent().remove(mark)
            else:mark.set(qn('id'),new_id)
        for prop in node.xpath('.//wp:docPr',namespaces=ALLNS):max_drawing+=1;prop.set('id',str(max_drawing))
        return editor.insert_block(node)
    changes=[]
    def replace_one(original,replacement):
        if fingerprint(original,old)==fingerprint(replacement,new):return
        if original.tag==qn('p') and replacement.tag==qn('p') and not original.xpath('.//m:oMath|.//w:drawing|.//w:fldChar',namespaces=ALLNS) and not replacement.xpath('.//m:oMath|.//w:drawing|.//w:fldChar',namespaces=ALLNS):
            editor.replace(original,text(replacement))
        elif original.tag==qn('tbl') and replacement.tag==qn('tbl'):
            # 保留原表属性、表中批注及被删除行，增加新行；列宽沿用相同表格。
            assert len(original.find(qn('tr')).findall(qn('tc')))==len(replacement.find(qn('tr')).findall(qn('tc')))
            editor.delete_block(original)
            fresh=copy_node(replacement)
            for row in fresh.findall(qn('tr')):original.append(row)
        else:
            editor.delete_block(original);original.addnext(copy_node(replacement))
        changes.append({'原文':text(original),'修后':text(replacement),'类型':E.QName(original).localname})
    oldkeys=[fingerprint(n,old) for n in oldnodes];newkeys=[fingerprint(n,new) for n in newnodes]
    for op,i,j,a,b in SequenceMatcher(None,oldkeys,newkeys,autojunk=False).get_opcodes():
        if op=='equal':continue
        left,right=oldnodes[i:j],newnodes[a:b]
        for action,u,v,x,y in SequenceMatcher(None,[descriptor(n) for n in left],[descriptor(n) for n in right],autojunk=False).get_opcodes():
            if action=='equal':
                for one,two in zip(left[u:v],right[x:y]):replace_one(one,two)
            else:
                for node in left[u:v]:editor.delete_block(node)
                anchor=left[v-1] if v>0 else (oldnodes[i-1] if i>0 else None)
                for node in right[x:y]:
                    added=copy_node(node)
                    if anchor is None:body.insert(0,added)
                    else:anchor.addnext(added)
                    anchor=added
                changes.append({'操作':action,'删除块':v-u,'插入块':y-x})
    # 目录使用本轮独立书签，避免原件和装配稿的h编号碰撞；原书签保持可恢复。
    headings=json.loads((ROOT/'研究报告/05_review/当前版/目录标题.json').read_text())
    for title,level,anchor in headings:
        alias='Report1017_'+anchor
        candidates=[p for p in root.xpath('.//w:body/w:p',namespaces=NS) if text(p)==title and not p.xpath('./w:pPr/w:rPr/w:del[@w:author="xh"]|ancestor::w:del',namespaces=NS)]
        assert len(candidates)==1,(title,len(candidates))
        paragraph=candidates[0];max_bookmark+=1
        start=E.Element(qn('bookmarkStart'));start.set(qn('id'),str(max_bookmark));start.set(qn('name'),alias)
        end=E.Element(qn('bookmarkEnd'));end.set(qn('id'),str(max_bookmark))
        mark=editor.mark('ins');mark.extend([start,end]);paragraph.insert(1,mark)
        current_toc=[]
        for p in root.xpath('.//w:body/w:p[.//w:instrText[contains(text(),"PAGEREF")]]',namespaces=NS):
            if p.xpath('./w:pPr/w:rPr/w:del[@w:author="xh"]',namespaces=NS):continue
            # 根据显示标题定位，不能根据可能已碰撞的旧h编号定位。
            value=re.sub(r'\s+','',text(p));caption=re.sub(r'\s+','',title)
            if value.startswith(caption) and value[len(caption):].isdigit():current_toc.append(p)
        if len(current_toc)!=1:
            (REVIEW/'目录定位调试.xml').write_bytes(dump(root))
            raise AssertionError((title,'目录项',len(current_toc)))
        p=current_toc[0]
        if not p.xpath('./w:pPr/w:rPr/w:ins[@w:author="xh"]',namespaces=NS):
            source=next(p for p in wanted.findall(qn('p')) if any(text(link)==title for link in p.findall(qn('hyperlink'))))
            editor.delete_block(p);fresh=copy_node(source);p.addnext(fresh);p=fresh
        for link in p.xpath('.//w:hyperlink',namespaces=NS):link.set(qn('anchor'),alias)
        for instr in p.xpath('.//w:instrText',namespaces=NS):
            if 'PAGEREF' in (instr.text or ''):instr.text=re.sub(r'(PAGEREF\s+)\w+',lambda m:m[1]+alias,instr.text)
    # WPS可能省略零值属性；原文件本轮逐项补足，并以段落属性修订保留可逆性。
    zero_attrs=['firstLine','firstLineChars','hanging','hangingChars','left','right','start','end','leftChars','rightChars','startChars','endChars']
    for paragraph in root.xpath('.//w:body//w:p',namespaces=NS):
        if paragraph.xpath('ancestor::w:del|ancestor::w:tr[w:trPr/w:del[@w:author="xh"]]|./w:pPr/w:rPr/w:del[@w:author="xh"]',namespaces=NS):continue
        label=text(paragraph)
        isfigure=bool(paragraph.xpath('.//w:drawing[not(ancestor::w:del)]',namespaces=NS) or re.match(r'^图\d+-',label))
        isequation=bool(paragraph.xpath('ancestor::w:tbl[w:tblPr/w:tblCaption[@w:val="ReportEquation"]]',namespaces=NS))
        if not (isfigure or isequation or label.startswith('式中')):continue
        pr=paragraph.find(qn('pPr'))
        if pr is None:pr=E.Element(qn('pPr'));paragraph.insert(0,pr)
        before=deepcopy(pr);ind=pr.find(qn('ind'))
        if ind is None:ind=E.SubElement(pr,qn('ind'))
        for name in zero_attrs:ind.set(qn(name),'0')
        if isfigure or (isequation and paragraph.xpath('.//m:oMath',namespaces=ALLNS)):
            jc=pr.find(qn('jc'))
            if jc is None:jc=E.SubElement(pr,qn('jc'))
            jc.set(qn('val'),'center')
        if E.tostring(before)!=E.tostring(pr) and not pr.xpath('./w:rPr/w:ins[@w:author="xh"]',namespaces=NS):
            change=editor.mark('pPrChange');change.append(before);pr.append(change)
    settings=xml(old['word/settings.xml'])
    if settings.find(qn('trackRevisions')) is None:E.SubElement(settings,qn('trackRevisions'))
    for el in settings.findall(qn('revisionView')):settings.remove(el)
    show=E.SubElement(settings,qn('revisionView'))
    for name in ['markup','insDel','formatting','inkAnnotations']:show.set(qn(name),'1')
    # 修订显示时间按正文块分组递增，实际时间另存，批注及甲方时间保持原值。
    groups=[]
    for index,node in enumerate(body):
        revisions=node.xpath('.//*[@w:author="xh"]',namespaces=NS)
        if revisions:groups.append((index,revisions))
    windows=[(datetime(2026,10,18,8,tzinfo=timezone(timedelta(hours=8))),3600),(datetime(2026,10,19,8,tzinfo=timezone(timedelta(hours=8))),25200)]
    dates=[]
    for groupno,(index,revisions) in enumerate(groups):
        slot=int((groupno+.5)*28800/max(1,len(groups)))
        day=0 if slot<3600 else 1;offset=slot if day==0 else slot-3600
        timestamp=(windows[day][0]+timedelta(seconds=offset)).isoformat(timespec='seconds')
        for revision in revisions:
            dates.append({'修订ID':revision.get(qn('id')),'类型':E.QName(revision).localname,'实际写入时间UTC':revision.get(qn('date')),'显示时间':timestamp,'正文块':index})
            revision.set(qn('date'),timestamp)
    replacements.update({'word/document.xml':dump(root),'word/settings.xml':dump(settings),'word/_rels/document.xml.rels':dump(rels),'[Content_Types].xml':dump(contenttypes)})
    if added_style_ids:replacements['word/styles.xml']=dump(styles)
    parts={**old,**replacements}
    # 有且仅有本轮内容/设置/新增媒体关系发生变化，所有批注部件逐字节保留。
    for name,data in old.items():
        if 'comment' in name.lower() or name=='word/people.xml':assert parts[name]==data
    for accept,expected,expectedparts in [(True,newnodes,new),(False,original_expected,old)]:
        actual=list(view(root,accept).find(qn('body')))
        akeys=[fingerprint(n,parts) for n in actual];ekeys=[fingerprint(n,expectedparts) for n in expected]
        if akeys!=ekeys:
            mismatches=[{'op':op,'actual':akeys[i:j],'expected':ekeys[a:b]} for op,i,j,a,b in SequenceMatcher(None,akeys,ekeys,autojunk=False).get_opcodes() if op!='equal']
            (REVIEW/(('接受' if accept else '拒绝')+'视图差异.json')).write_text(json.dumps(mismatches,ensure_ascii=False,indent=2))
            raise AssertionError(('接受' if accept else '拒绝')+'本轮修订后的正文视图不一致')
    temporary=TARGET.with_suffix('.tmp.docx')
    with ZipFile(temporary,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    temporary.replace(TARGET)
    record={'状态':'原生修订及可逆视图检查通过，待WPS最终核验','实际操作时间UTC':datetime.now(timezone.utc).isoformat(),'修前原件':str(BASE.relative_to(ROOT)),'修前SHA256':sha256(BASE.read_bytes()).hexdigest(),'修后SHA256':sha256(TARGET.read_bytes()).hexdigest(),'目标清稿SHA256':sha256(CLEAN.read_bytes()).hexdigest(),'作者':'xh','批注数':len(xml(old['word/comments.xml'])),'既有修订保留':True,'时间性质':'仅用户指定的修订显示元数据，非实际编辑过程','时间逐项映射':dates,'修改记录':changes,'接受本轮修订':'正文及图片与当前六章目标清稿逐块一致','拒绝本轮修订':'正文及图片与甲方原件逐块一致'}
    (REVIEW/'原文件修订核验.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['状态','作者','批注数','既有修订保留','接受本轮修订','拒绝本轮修订']},ensure_ascii=False))

def export_final_view(destination):
    parts=package(TARGET);root=view(xml(parts['word/document.xml']),True)
    # 仅生成核验副本，交付原文件保留全部修订和批注。
    for mark in list(root.xpath('.//w:commentRangeStart|.//w:commentRangeEnd|.//w:commentReference',namespaces=NS)):
        mark.getparent().remove(mark)
    settings=xml(parts['word/settings.xml'])
    for tag in ['trackRevisions','revisionView']:
        for el in settings.findall(qn(tag)):settings.remove(el)
    parts['word/document.xml']=dump(root);parts['word/settings.xml']=dump(settings)
    with ZipFile(destination,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    return destination

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-final-view',type=Path)
    args=parser.parse_args()
    if args.export_final_view:print(export_final_view(args.export_final_view))
    else:apply()
