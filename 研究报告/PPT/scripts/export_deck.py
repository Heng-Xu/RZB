from pathlib import Path
import subprocess,os,sys,json
BASE=Path(__file__).resolve().parents[1];W=BASE/'成果汇报_20261019';K=Path('/home/xh/.codex/skills/ppt-master/scripts');PY=sys.executable
env=dict(os.environ,PYTHONPATH='/tmp/pptmaster-deps'+(':'+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else ''))
steps=[
 ('authoring',[PY,str(BASE/'scripts/build_deck.py')]),
 ('stamp',[PY,str(K/'stamp_native_fallbacks.py'),str(W/'authoring-svg-flat'),'--write']),
 ('summary',[PY,str(K/'svg_authoring_view.py'),str(W/'authoring-svg-flat'),'--refresh-summary']),
 ('quality',[PY,str(K/'svg_quality_checker.py'),str(W),'--roundtrip','--json']),
 ('export',[PY,str(K/'svg_to_pptx.py'),str(W),'--roundtrip','--native-charts-and-tables','--no-animations','--primary-language','zh-CN','-o',str(W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx')]),
 ('manual_advance',[PY,str(BASE/'scripts/set_manual_advance.py')]),
 ('delivery',[PY,str(K/'pptx_delivery_check.py'),str(W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx')]),
 ('readback',[PY,str(K/'source_to_md/ppt_to_md.py'),str(W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx'),'-o',str(W/'validation/readback.md')]),
]
for name,args in steps:
    p=subprocess.run(args,cwd=BASE,env=env,capture_output=True,text=True)
    (W/'validation'/f'{name}.log').write_text(p.stdout+'\n'+p.stderr)
    print(name+': '+str(p.returncode),flush=True)
    if p.returncode:
        print((p.stdout+'\n'+p.stderr)[-14000:]);sys.exit(p.returncode)
print('Export and native validation completed')
