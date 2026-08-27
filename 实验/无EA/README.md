# 实验工程目录

> 创建时间：2026-06-12 | 目的：基于公开数据集进行论文实验（双轨制 — 详 `分析/03_对标期刊分析与论文生成方案.md` §9）

## 目录结构

```
实验/
├── README.md                      ← 本文件（导航）
├── 01_实验方案.md                  ← 实验设计主文档
├── 02_数据采集状态.md              ← 数据采集进度跟踪
├── 03_算法实现规划.md              ← 模型代码实现路线
├── datasets/                      ← 数据集（按类别组织）
│   ├── ieee33/                    ← IEEE 33-bus 配电系统
│   │   ├── ieee33_bus.csv         ← 节点数据
│   │   ├── ieee33_branch.csv      ← 支路数据
│   │   └── README.md              ← 数据说明与引用
│   ├── ieee69/                    ← IEEE 69-bus 配电系统（扩展算例）
│   ├── pv_profiles/               ← PV出力曲线（PVGIS/NREL）
│   ├── load_profiles/             ← 负荷曲线（中国典型曲线）
│   ├── cost_params/               ← 成本参数（Z1-Z5）
│   │   └── baseline_costs.yaml    ← 公开数据标定
│   └── chinese_cases/             ← 中国实际案例摘录
├── scripts/                       ← 数据采集与处理脚本
│   ├── ieee33_loader.py           ← IEEE 33-bus 数据加载
│   ├── fetch_pvgis.py             ← PVGIS API 客户端
│   ├── fetch_load_profile.py      ← 负荷曲线采集
│   └── lcc_simulator.py           ← 双向Z4-LCC 仿真器（骨架）
├── notebooks/                     ← 分析/可视化笔记本
└── results/                       ← 实验结果输出
    ├── figures/                   ← 论文图
    └── tables/                    ← 论文表
```

## 快速启动

```bash
# 1. 验证Python环境
python -c "import numpy, pandas, matplotlib, yaml; print('OK')"

# 2. 加载IEEE 33-bus基线数据
python 实验/scripts/ieee33_loader.py

# 3. 抓取PVGIS光伏出力（徐州坐标 34.27,117.18）
python 实验/scripts/fetch_pvgis.py --lat 34.27 --lon 117.18 --year 2023 \
    --output 实验/datasets/pv_profiles/xuzhou_2023.csv

# 4. 跑LCC基线仿真
python 实验/scripts/lcc_simulator.py --case ieee33 --scenario baseline
```

## 与项目主报告的关系

| 实验产出 | 论文章节 | 项目主报告章节 | 备注 |
|---------|---------|------------|------|
| IEEE 33-bus 算例 | 论文 §4.1 | 主报告 §6.1 | 公开数据，论文重点 |
| 中国典型片区案例 | 论文 §4.2 | 主报告 §6.2 | 半公开数据 |
| 徐州实测案例 | 主报告 §6.3 | 主报告 §6.3 | **甲方数据到位后** |

## 当前状态（2026-06-12）

- ✅ 实验骨架搭建完成
- ✅ IEEE 33-bus 基础数据已编码
- ✅ 基线成本参数YAML已创建
- ✅ PVGIS 抓取脚本已编写
- ⏸ PVGIS 数据采集（待执行）
- ⏸ LCC 仿真器实现（骨架已就位）
- ⏸ 决策矩阵填值（待算例完成）
