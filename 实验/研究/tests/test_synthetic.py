import pandas as pd, pathlib

from src.clr import compute_all
from src.io_loader import load_scenario

ROOT = pathlib.Path(__file__).parents[1]
D = ROOT / "data/synthetic"
def test_structure():
    st = pd.read_csv(D / "stations.csv")
    assert set(st.county) == {"XY", "PZ"}
    assert st.zone_id.nunique() == 5            # 2县共5个高压分区(XY:3, PZ:2)
    assert len(st) == 12                        # 共12座110kV站
def test_curves_shape():
    s0 = pd.read_csv(D / "load_curves" / "S01.csv")
    assert len(s0) == 8760 and {"timestamp","p_net_mw"} <= set(s0.columns)
def test_has_reverse_zone():
    # 设计保证:至少1个乡镇高PV分区存在负净负荷时段(反向),1个城区分区全年正向
    import glob
    mins = {p: pd.read_csv(p).p_net_mw.min() for p in glob.glob(str(D/"load_curves/*.csv"))}
    assert min(mins.values()) < -5  and max(mins.values()) > 0


def test_reverse_binding_zone():
    """分区反向卡边验收(跨任务修复,见 gen_synthetic.py 文件头调参记录):
    1. >=1 个乡镇(rural)分区聚合净负荷 P->P+(反向卡边,binding=='reverse');
    2. 该分区内 >=1 站站级 P->0.8x站容量(2x50MVA 站即 P->80MW,反向不加
       措施不可行);
    3. 城区(urban)分区全年保持正向(P_rev==0),不受调参影响。
    分区聚合口径与 src.clr.compute_all 一致:逐时刻先加总同分区各站,再取峰
    (同时率内生),不得用各站峰值直接相加。
    """
    data = load_scenario(ROOT)
    df = compute_all(data)

    rural = df[df.area_type == "rural"]
    reverse_zones = rural[rural.binding == "reverse"]
    assert len(reverse_zones) >= 1, f"无乡镇分区反向卡边:\n{rural}"

    station_cap_mva = {
        sid: sum(t.capacity_mva for t in st.transformers)
        for sid, st in data.stations.items()
    }
    hit = False
    for zone_id in reverse_zones.index:
        zone = data.zones[zone_id]
        for st in zone.stations:
            s = data.pnet[st.station_id]
            p_rev = max(float(-s.min()), 0.0)
            cap = station_cap_mva[st.station_id]
            if p_rev > 0.8 * cap:
                hit = True
    assert hit, "反向卡边分区内无站级 P->0.8xcap(未达'不加措施不可行'门槛)"

    urban = df[df.area_type == "urban"]
    assert (urban.p_rev == 0.0).all(), f"城区分区出现反向:\n{urban}"


def test_baseline_r_below_cap():
    """旧合成演示用双向压力诊断比不超过 1.95。

    该断言只服务旧 M1 优化器的 ``max(P⁺,P⁻)`` 演示口径；合同 2.0.0 下
    ``compute_all().r`` 已改为正式正向容载比 ``ΣS/P⁺``，不能再拿正式列
    检查旧双向阈值。

    根因:原合成数据 Z5 诊断比=2.10>2.0(容量富余),旧红线约束
    无法自然满足,逼优化器用"储能午间放电人为抬高反送峰"这种非物理方式压 R。
    修复口径:抬高 Z5 负荷幅值/下调 PV 使基线峰值上升、R 落回 <=1.95,使红线在
    基态即成立,演示机制回归"反向压力→柔性措施"的设计本意(见 gen_synthetic.py
    文件头调参记录第2条)。口径与 src.clr.compute_all 完全一致(逐时刻分区聚合
    后取峰,同时率内生)。
    """
    data = load_scenario(ROOT)
    df = compute_all(data)
    legacy_bidirectional_diagnostic = df["cap_mva"] / df[["p_fwd", "p_rev"]].max(axis=1)
    over = df[legacy_bidirectional_diagnostic > 1.95]
    assert over.empty, (
        "以下分区旧双向诊断比>1.95(容量富余,会诱发旧红线抬峰):\n"
        f"{over[['cap_mva', 'p_fwd', 'p_rev', 'r']]}"
    )
    pd.testing.assert_series_equal(
        df["r"],
        df["cap_mva"] / df["p_fwd"],
        check_names=False,
        rtol=1e-12,
    )
