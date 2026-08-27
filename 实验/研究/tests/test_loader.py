"""Task 2 对象层测试:io_loader + net_model。

覆盖简报 Step 1 五类断言:
1. 对象数量(zones/stations/ties)
2. S01.cap_mva == 100
3. 3台并列站(S05/S11) beta_eff ≈ 0.5333
4. forbidden 联络(T09) usable == False
5. 删列触发 SchemaError(用 tmp_path 复制数据,不动原数据)
"""
import shutil
from pathlib import Path

import pytest

from src.io_loader import SchemaError, load_params, load_scenario

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def scenario():
    return load_scenario(ROOT)


def test_object_counts(scenario):
    assert len(scenario.zones) == 5
    assert len(scenario.stations) == 12
    assert len(scenario.ties) == 9


def test_station_cap_mva(scenario):
    assert scenario.stations["S01"].cap_mva == pytest.approx(100.0)


def test_beta_eff_parallel(scenario):
    beta_cfg = scenario.params["beta"]
    for sid in ("S05", "S11"):
        st = scenario.stations[sid]
        assert len(st.transformers) == 3
        assert st.beta_eff(beta_cfg) == pytest.approx((3 - 1) / 3, rel=1e-6)


def test_beta_eff_split(scenario):
    beta_cfg = scenario.params["beta"]
    st = scenario.stations["S01"]
    assert st.beta_eff(beta_cfg) == pytest.approx(0.80)


def test_tie_forbidden_not_usable(scenario):
    tie = next(t for t in scenario.ties if t.tie_id == "T09")
    assert tie.switch_mode == "forbidden"
    assert tie.usable is False


def test_tie_sensitive_not_usable(scenario):
    for tid in ("T01", "T08"):
        tie = next(t for t in scenario.ties if t.tie_id == tid)
        assert tie.sensitive is True
        assert tie.usable is False


def test_pnet_shape_and_index(scenario):
    assert scenario.pnet.shape == (8760, 12)
    assert list(scenario.pnet.columns) == sorted(scenario.pnet.columns)
    assert scenario.pnet.index.inferred_type == "datetime64"


def test_pv_capacity_series(scenario):
    assert scenario.pv_capacity["S01"] == pytest.approx(20.387)
    assert set(scenario.pv_capacity.index) == set(scenario.stations)


def test_load_params():
    p = load_params(ROOT)
    assert p["beta"]["split_mode"] == pytest.approx(0.80)


def test_schema_error_on_missing_column(tmp_path):
    # 复制整个 data/ 目录到 tmp_path,删掉 stations.csv 的 zone_id 列,触发 SchemaError
    data_src = ROOT / "data"
    data_dst = tmp_path / "data"
    shutil.copytree(data_src, data_dst)

    stations_path = data_dst / "synthetic" / "stations.csv"
    lines = stations_path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(",")
    zone_idx = header.index("zone_id")
    new_lines = []
    for line in lines:
        cols = line.split(",")
        del cols[zone_idx]
        new_lines.append(",".join(cols))
    stations_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    shutil.copy(ROOT / "params.yaml", tmp_path / "params.yaml")

    with pytest.raises(SchemaError) as exc_info:
        load_scenario(tmp_path)

    msg = str(exc_info.value)
    assert "stations.csv" in msg
    assert "zone_id" in msg
