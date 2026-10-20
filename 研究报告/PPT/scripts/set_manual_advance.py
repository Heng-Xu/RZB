"""Apply PPT Master's public motion API to clear inherited template timings.

Round-trip sidecar null does not clear timing-only transitions in this template.
This post-export step owns only slide advance and runs before final validation.
"""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import sys,re,json,hashlib

K=Path('/home/xh/.codex/skills/ppt-master/scripts');sys.path.insert(0,str(K))
from pptx_transitions import apply_slide_motion_xml,EnterUpdate,AdvanceUpdate
B=Path(__file__).resolve().parents[1];W=B/'成果汇报_20261019'
p=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx'
before=p.read_bytes();temporary=p.with_suffix('.manual.tmp')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main'};changed=[]
def content_tree(raw):
    r=E.fromstring(raw)
    for tr in r.findall('.//p:transition',ns):tr.getparent().remove(tr)
    return E.tostring(r,method='c14n')
with ZipFile(p)as zin,ZipFile(temporary,'w')as zout:
    for info in zin.infolist():
        raw=zin.read(info.filename);new=raw
        if re.fullmatch(r'ppt/slides/slide\d+\.xml',info.filename):
            xml,_=apply_slide_motion_xml(raw.decode(),enter=EnterUpdate(policy='none'),advance=AdvanceUpdate(mode='click'))
            new=xml.encode()
            assert content_tree(raw)==content_tree(new),info.filename
            if new!=raw:changed.append(info.filename)
        zout.writestr(info,new)
temporary.replace(p)
r={'method':'PPT Master public apply_slide_motion_xml API, EnterUpdate(none), AdvanceUpdate(click)','reason':'现场手动翻页；清除模板继承的自动换页时间','before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed_slides':changed,'all_other_parts_byte_identical':True,'all_slide_content_except_transitions_unchanged':True}
(W/'validation/manual_advance.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps({'changed_slides':len(changed),'manual_advance':True}))
