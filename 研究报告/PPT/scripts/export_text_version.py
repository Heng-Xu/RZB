from pathlib import Path
import subprocess,sys,os
B=Path(__file__).resolve().parents[1];W=B/'成果汇报_文字增强版_20261021';K=Path('/home/xh/.codex/skills/ppt-master/scripts');PY=sys.executable
env=dict(os.environ,PYTHONPATH='/tmp/pptmaster-deps'+(':'+os.environ['PYTHONPATH']if os.environ.get('PYTHONPATH')else''))
out=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_文字增强版.pptx'
steps=[('authoring',[PY,str(B/'scripts/build_text_version.py')]),('summary',[PY,str(K/'svg_authoring_view.py'),str(W/'authoring-svg-flat'),'--refresh-summary']),('quality',[PY,str(K/'svg_quality_checker.py'),str(W),'--roundtrip','--json']),('export',[PY,str(K/'svg_to_pptx.py'),str(W),'--roundtrip','--native-charts-and-tables','--no-animations','--primary-language','zh-CN','-o',str(out)]),('delivery',[PY,str(K/'pptx_delivery_check.py'),str(out)]),('readback',[PY,str(K/'source_to_md/ppt_to_md.py'),str(out),'-o',str(W/'validation/readback.md')])]
for name,args in steps:
    r=subprocess.run(args,cwd=B,env=env,capture_output=True,text=True);(W/'validation'/f'{name}.log').write_text(r.stdout+'\n'+r.stderr);print(name+': '+str(r.returncode),flush=True)
    if r.returncode:print((r.stdout+'\n'+r.stderr)[-10000:]);sys.exit(r.returncode)
print('Text-enriched version exported')
