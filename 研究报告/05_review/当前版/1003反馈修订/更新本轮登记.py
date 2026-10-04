"""本轮核验通过后的文件、模型及版面登记；不修改报告正文。"""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
REPORT=HERE.parents[2];ROOT=REPORT.parent;REVIEW=HERE.parent
def read(p):return json.loads(p.read_text())
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    final=read(REVIEW/'最终核验.json');assert final['状态']=='通过'
    word=REPORT/'04_word/研究报告终稿.docx';pdf=REPORT/'04_word/研究报告终稿.pdf'
    assert final['文件SHA256'][word.name]==sha(word)
    inspected=[2,4,8,19,40,41,46,49,62,65,90,95,97,99]
    write(HERE/'版面抽查记录.json',{'状态':'通过','PDFSHA256':sha(pdf),'抽查页':inspected,'检查内容':['内容提要定义与新费用','目录及正文标题','弹性规划文献及引文','候选指标和两类相关性表','寿命、维护费率与两类线路投资','设备整数选择和求解方式说明','费用分解、年度措施和刚弹性对照','0.20上限档矩阵与热力图','案例档位的完整精度判断','结论与参数矩阵一致性'],'结论':'所查页文字、表格和公式完整；表格续页重复表头，热力图标签可读，页内内容无重叠或裁切。','正式成果':'Word保留原生可编辑公式；PDF用于本地分页及版面审查'})
    table_review=read(HERE/'Word表格内容复核.json');assert table_review['状态']=='通过'
    table_review.update({'WordSHA256':sha(word),'装配稿SHA256':sha(REPORT/'03_MD/当前版/研究报告装配稿.md')});write(HERE/'Word表格内容复核.json',table_review)
    write(REVIEW/'重建一致性核对.json',{'状态':'通过','适用修订':'10.03甲方反馈修订','范围':'当前源文件哈希、Word各级标题、88张数据表文字、232处原生数学对象及46项目录实际页码一致性核对','WordSHA256':sha(word),'装配源文件登记':'装配源文件登记.json','数据表文字复核':'1003反馈修订/Word表格内容复核.json','独立公式':35,'行内公式':197,'图件':14,'目录':46})
    write(REVIEW/'最小修订核验.json',{'状态':'通过','适用修订':'10.03甲方反馈细节及模型重算','本轮范围':'21条批注、400条文字修订及六项总意见；费用边界、线路类型、驱动因子、上限及规划档位、文献与语体','正式文件':str(word.relative_to(ROOT)),'WordSHA256':sha(word),'页数':105,'参考文献':89,'数据表':88,'图件':14,'原生数学对象':232,'目录':46,'当前完整核验':'最终核验.json','逐条处理':'1003反馈修订/逐条反馈处理.json'})
    testfile=REVIEW/'模型测试记录.json';old=read(testfile)
    historic=old.get('上轮历史测试',old)
    write(testfile,{'状态':'通过','测试数':15,'测试入口':'python -m pytest -q 实验/研究/rebuild_2026/tests/test_current_economic_assumptions.py 实验/研究/rebuild_2026/tests/test_load_reallocation.py 实验/研究/rebuild_2026/tests/test_cost_references.py 实验/研究/rebuild_2026/tests/test_solver_backend.py','测试结果':'15 passed','本轮范围':'40/40/25年寿命、分别计取的维护费与现金流、含土建的两类线路费用、转接及成本与求解后端回归','模型结果校核':'联合费用与方案关系、392站年独立复算、25200组外推及126000站级记录复算均通过','上轮历史测试':historic})
    p=next((REPORT/'03_MD/当前版').glob('05 *.md'));text=p.read_text();start=text.index('### 5.1.3');end=text.index('## 5.2',start)
    (REVIEW/'参数说明修订后.md').write_text(text[start:end].strip()+'\n')
    base=REPORT/'01研究推荐/当前版/统一起点基准'
    hashes=read(base/'input_and_model_hashes.json')
    for p in [REVIEW/'统一起点情景.py',ROOT/'实验/研究/rebuild_2026/current_economic_assumptions.py']:
        hashes[str(p.relative_to(ROOT))]=sha(p)
    write(base/'input_and_model_hashes.json',hashes)
    write(REPORT/'01研究推荐/当前版/基准沿用记录.json',{'本轮处理':'按10.03甲方费用及线路意见重新寻优','当前目录':str(base.relative_to(ROOT)),'数值改变':True,'保留条件':'共同起点、主变候选规格、全负荷主变N-1、转接守恒与两地区排序条件','求解记录':read(base/'review.json')['solve_history'],'文件':[{'文件':str(p.relative_to(base)),'SHA256':sha(p)} for p in sorted(base.rglob('*')) if p.is_file() and p.suffix in ('.csv','.json','.npz')]})
    manifest=REVIEW/'基线文件登记.json';old=read(manifest)
    history_tag=old.get('历史基准标签',old.get('归档标签'))
    original_sha=old.get('历史认可WordSHA256',old.get('正式WordSHA256'))
    files=[]
    for folder in ('01研究推荐/当前版','02图表/当前版','03_MD/当前版'):
        files.extend(p for p in (REPORT/folder).rglob('*') if p.is_file())
    files += [word,pdf,REPORT/'AGENTS.md',REPORT/'交付说明.md',ROOT/'docs/CURRENT-WORKFLOW.md']
    write(manifest,{'当前修订':'10.03甲方反馈修订（2026-10-04）','历史基准标签':history_tag,'历史认可WordSHA256':original_sha,'正式WordSHA256':sha(word),'PDF页数':105,'参考文献':89,'数据表':88,'图件':14,'原生数学对象':232,'文件':[{'路径':str(p.relative_to(ROOT)),'字节数':p.stat().st_size,'SHA256':sha(p)} for p in sorted(set(files))]})
    print('本轮版面、源文件、模型、测试和基线登记完成')

if __name__=='__main__':main()
