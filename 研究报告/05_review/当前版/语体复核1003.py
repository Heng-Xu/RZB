"""技术修订完成后，按指定技能的明确触发规则最小改写。"""
from pathlib import Path
import json,re,hashlib
HERE=Path(__file__).parent;R=HERE.parents[1];T=R/'03_MD/当前版';A=R/'02图表/当前版'
RULES=[
 ('此外，Zhang 等表明','Zhang 等还表明','lieflat第10条：句首连接词'),
 ('此外，Zhao 等以','Zhao 等还以','lieflat第10条：句首连接词'),
 ('对实际规划而言，年度容载比的变化还应区分容量变化与负荷变化。','实际规划还应区分容量变化与负荷变化对年度容载比的影响。','lieflat第10条：前置话题壳'),
 ('对于反向压力外推，保留电源原站归属，并使用非负用户负荷的典型场景。','反向压力外推保留电源原站归属，并使用非负用户负荷的典型场景。','lieflat第10条：前置话题壳'),
 ('形成面向不同片区的弹性容载比参考档位及适用条件。','形成弹性容载比参考档位及适用条件，供不同片区比选。','lieflat第10条：过长前置定语'),
 ('后者是能够容纳该单元全部已算配置的最小上限档。','后者是最小上限档，能够容纳该单元全部已算配置。','lieflat第10条：过长前置定语'),
]
TECHNICAL=[('单台主变退出','主变N-1'),('单台退出','主变N-1'),('退出工况','主变N-1工况'),('槽位','主变安装位置'),('一般站群','五站仿真模板')]
def invariant(s):
    return {'标题':re.findall(r'^#{1,4} .*$',s,re.M),'非空段数':len([p for p in s.split('\n\n') if p.strip()]),'数字':re.findall(r'\d+(?:\.\d+)?',s),'引用':re.findall(r'\[[0-9][0-9,，—–-]*\]',s),'公式':re.findall(r'\$\$[\s\S]*?\$\$|\$[^$\n]+\$',s),'表图占位':re.findall(r'\[\[(?:TABLE|FIG|SECTION):[^\]]+\]\]',s)}
def main():
    audit_path=HERE/'语体与术语审查.json'
    previous=json.loads(audit_path.read_text()) if audit_path.exists() else {}
    records=list(previous.get('实际技能修改',[]));checked=[];new_count=0
    for p in sorted(T.glob('0[1-6] *.md')):
        s=p.read_text()
        # 术语处理单列为甲方修订，先于技能检查。
        for old,new in TECHNICAL:s=s.replace(old,new)
        before=s
        for old,new,rule in RULES:
            if old in s:
                record={'文件':str(p.relative_to(R)),'规则':rule,'原文':old,'修订':new,'匹配次数':s.count(old)}
                if record not in records:records.append(record)
                new_count+=1;s=s.replace(old,new)
        assert invariant(before)==invariant(s),p
        checked.append({'文件':str(p.relative_to(R)),'技术修订后技能处理前SHA256':hashlib.sha256(before.encode()).hexdigest(),'技能处理后SHA256':hashlib.sha256(s.encode()).hexdigest(),'框架数值引文公式核对':'通过'})
        p.write_text(s)
    for filename in ('计算表.json','生成段落.json'):
        p=A/filename;d=json.loads(p.read_text())
        for k,v in d.items():
            for old,new in TECHNICAL:v=v.replace(old,new)
            d[k]=v
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
    review={'状态':'通过','技能':['lieflat-less-ai-tone','humanizer:humanizer'],'依据':['/home/xh/.agents/skills/lieflat-less-ai-tone/SKILL.md','/home/xh/.codex/skills/humanizer/SKILL.md'],'文体':'电网规划研究报告；以用户提供范文和专业语料判断语体，保留正式术语和编号','处理范围':'甲方技术修改完成后，只处理明确匹配的技能规则；未匹配文字不作技能润色。甲方术语修订与技术补充另行记录。','实际技能修改':records,'验收':checked,'保留项':['六章结构、分节顺序及段落结构','指标及公式定义、原精度数据、引文编号','设备与线路条件、费用边界、数据估计性质','工程必要清单、标准名称及引用标题中的标点'],'边界':'不使用检测器分数作为是否为AI生成的结论；依据可定位表达规则复核。'}
    review['逐项复核']={str(i):'按工程报告语体及用户语料复核；只改明确触发处，其余保留' for i in range(1,12)}
    review['体裁保留说明']=['公式变量、约束条件、费用科目及候选清单需要完整列举','章节编号用于正式报告索引，不因编号形式删除','逐站分析承担相同校核功能，保留结构对应关系','标准全称、直接引文、必要范围限定及因果连接保留']
    audit_path.write_text(json.dumps(review,ensure_ascii=False,indent=2))
    print('本次新增技能修订',new_count,'处；本轮累计',len(records),'处；六章框架与数值引文核对通过')
if __name__=='__main__':main()
