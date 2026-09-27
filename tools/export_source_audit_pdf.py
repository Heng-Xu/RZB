from pathlib import Path
import os,sys,subprocess,time,json
import uno
from com.sun.star.beans import PropertyValue
def prop(k,v):
 p=PropertyValue();p.Name=k;p.Value=v;return p
base=Path('/tmp/huaweibei-lo/root/usr/lib/libreoffice/program')
log=open('/tmp/rzb-stage3/uno-office.log','w')
p=None
ctx=uno.getComponentContext();resolver=ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx)
for _ in range(60):
 try:remote=resolver.resolve('uno:socket,host=127.0.0.1,port=20884;urp;StarOffice.ComponentContext');break
 except Exception:time.sleep(.3)
else:raise RuntimeError('UNO unavailable')
desktop=remote.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',remote)

root=Path.cwd();source=(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'研究报告/数据来源/当前报告数据来源与计算审查.docx')
doc=desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(source)), '_blank',0,(prop('Hidden',True),prop('ReadOnly',True)))
doc.refresh()
output=source.with_suffix('.pdf')
doc.storeToURL(uno.systemPathToFileUrl(str(output)),(prop('FilterName','writer_pdf_Export'),))
doc.close(True)
print(output,flush=True)
