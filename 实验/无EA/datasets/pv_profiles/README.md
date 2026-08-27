# PV出力曲线数据集

> 来源：PVGIS API v5.2（欧盟JRC Photovoltaic Geographical Information System，全球覆盖，免费、无认证）  
> 文档：https://re.jrc.ec.europa.eu/api/v5_2/

## 已采集数据

| 文件 | 地点 | 经纬度 | 数据时间范围 | 采样间隔 |
|------|------|--------|------------|---------|
| `xuzhou_tmy.csv` | 徐州 | 34.27°N, 117.18°E | PVGIS默认多年序列（约16年） | 1小时 |
| `jiaxing_tmy.csv` | 嘉兴 | 30.77°N, 120.75°E | 同上 | 1小时 |
| `laiwu_tmy.csv` | 莱芜 | 36.20°N, 117.68°E | 同上 | 1小时 |

## 字段说明

| 字段 | 含义 | **单位** |
|------|------|------|
| time | 时间戳 | YYYYMMDD:HH 格式（UTC） |
| **P** | PV系统出力 | **W**（瓦特）注意：不是 kW |
| G_i | 倾斜面辐照度 | W/m² |
| T2m | 2米气温 | °C |
| WS10m | 10米风速 | m/s |

> ⚠️ **关键说明**：PVGIS 在 `pvcalculation=1` 模式下返回的 `P` 字段是**瓦特**（W），来自单位 kWp 容量装机（额定1 kWp）。  
> 若需 kW：`P_kw = P / 1000`；若需归一化到任意装机容量：`P(kW) = (P / 1000) × installed_kWp`。

## 系统参数（采集时设定）

| 参数 | 值 |
|------|---|
| 额定容量 (peakpower) | 1.0 kWp |
| 系统损耗 (loss) | 14% |
| 倾角 (angle) | 30° |
| 方位角 (aspect) | 0°（朝南） |
| PV技术 (pvtechchoice) | crystSi（晶硅） |
| 安装方式 (mountingplace) | free（自由立柱） |

## 数据规模

每个文件约 **140256 小时 = 16 年** 的连续记录（PVGIS默认时间范围 2005-2020）。

## 期望物理量

对于晶硅+30°倾角+14%损耗的1 kWp装机：

| 指标 | 长三角/华北预期 | 字段对应 |
|------|----------|--------|
| 年发电量 | 1100-1400 kWh/kWp | `total_yield_kwh` ÷ 年数 |
| 峰值出力 | 0.85-0.95 kW（来自1kWp） | `peak_kw` |
| 年运行小时 | 4300-4500 h/年 | `operating_hours` ÷ 年数 |
| 容量因子 | 12-16% | `capacity_factor_pct` |

## 在 LCC 仿真器中的使用

```python
import pandas as pd

# 加载小时曲线
pv = pd.read_csv("datasets/pv_profiles/xuzhou_tmy.csv")
pv["P_kw"] = pv["P"] / 1000  # W → kW

# 归一化到任意装机
installed_kwp = 2500  # 例: 2.5 MWp片区PV
pv["P_kw_actual"] = pv["P_kw"] * installed_kwp

# 用于反送场景生成
# 反送时刻 = (PV出力 - 负荷) > 0 的小时
load = pd.read_csv("datasets/load_profiles/typical_load.csv")  # 待补
net = pv["P_kw_actual"] - load["P_kw"]
reverse_hours = (net > 0).sum()
print(f"年反送小时数：{reverse_hours} h")
```

## 重新采集命令

```bash
# 徐州（默认地点）
python scripts/fetch_pvgis.py --lat 34.27 --lon 117.18 \
    --kwp 1.0 --tilt 30 \
    --output datasets/pv_profiles/xuzhou_tmy.csv

# 自定义倾角扫描
for tilt in 25 30 35; do
    python scripts/fetch_pvgis.py --lat 34.27 --lon 117.18 \
        --kwp 1.0 --tilt $tilt \
        --output datasets/pv_profiles/xuzhou_tilt${tilt}.csv
done
```

## 数据已验证

| 文件 | 文件大小 | 状态 |
|------|--------|------|
| xuzhou_tmy.csv | 4.4 MB | ✅ |
| jiaxing_tmy.csv | 4.4 MB | ✅ |
| laiwu_tmy.csv | 4.4 MB | ✅ |
