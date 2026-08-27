#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PVGIS API 客户端：获取指定地理位置的逐小时光伏出力曲线。

PVGIS（Photovoltaic Geographical Information System）由欧盟JRC维护，
覆盖全球大部分地区（含中国），免费、无需身份验证。

用法：
    python fetch_pvgis.py --lat 34.27 --lon 117.18 --output xuzhou.csv
    python fetch_pvgis.py --lat 34.27 --lon 117.18 --kwp 1000 --tilt 30

参考：https://re.jrc.ec.europa.eu/api/v5_2/seriescalc
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from urllib import error, parse, request


PVGIS_BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
DEFAULT_TIMEOUT = 60


def fetch(
    lat: float,
    lon: float,
    *,
    kwp: float = 1.0,
    loss: float = 14.0,
    tilt: float = 30.0,
    aspect: float = 0.0,
    pvtechchoice: str = "crystSi",
    mounting: str = "free",
    startyear: int | None = None,
    endyear: int | None = None,
) -> dict:
    """Fetch raw PVGIS time series in JSON format."""
    params = {
        "lat": f"{lat:.4f}",
        "lon": f"{lon:.4f}",
        "outputformat": "json",
        "pvcalculation": 1,
        "peakpower": kwp,
        "loss": loss,
        "angle": tilt,
        "aspect": aspect,
        "pvtechchoice": pvtechchoice,
        "mountingplace": mounting,
        "browser": 0,
    }
    if startyear is not None:
        params["startyear"] = startyear
    if endyear is not None:
        params["endyear"] = endyear

    url = f"{PVGIS_BASE_URL}?{parse.urlencode(params)}"
    print(f"[INFO] fetching: {url}", file=sys.stderr)

    for attempt in range(3):
        try:
            req = request.Request(url, headers={"User-Agent": "research-pvgis-client/1.0"})
            with request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                return json.loads(resp.read())
        except (error.URLError, error.HTTPError, TimeoutError) as e:
            wait = 2 ** attempt
            print(f"[WARN] attempt {attempt+1} failed: {e}; retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"PVGIS unreachable after 3 attempts: {url}")


def to_csv(data: dict, output: Path) -> int:
    """Convert PVGIS hourly output to wide-format CSV."""
    outputs = data.get("outputs", {}).get("hourly", [])
    if not outputs:
        raise RuntimeError("PVGIS response missing hourly outputs")

    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["time", "P", "G_i", "T2m", "WS10m"]  # P=kW power, G_i=irradiance, T=temp, WS=wind
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in outputs:
            writer.writerow({k: row.get(k) for k in fields})
    print(f"[OK] saved {len(outputs)} hourly samples -> {output}")
    return len(outputs)


def summarize(data: dict, peakpower_kwp: float = 1.0) -> dict:
    """PVGIS 'P' field is in Watts. Convert to kWh for energy totals."""
    outputs = data.get("outputs", {}).get("hourly", [])
    if not outputs:
        return {}
    p_vals_w = [row.get("P", 0) or 0 for row in outputs]
    total_kwh = sum(p_vals_w) / 1000.0
    peak_w = max(p_vals_w) if p_vals_w else 0
    peak_kw = peak_w / 1000.0
    pv_hours = sum(1 for p in p_vals_w if p > 0)
    # Capacity factor = total_kwh / (capacity_kw * n_hours)
    cap_factor = total_kwh / (peakpower_kwp * len(outputs)) if outputs else 0
    return {
        "n_hours": len(outputs),
        "total_yield_kwh": round(total_kwh, 2),
        "peak_kw": round(peak_kw, 4),
        "operating_hours": pv_hours,
        "capacity_factor_pct": round(cap_factor * 100, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="PVGIS hourly PV time series fetcher")
    ap.add_argument("--lat", type=float, required=True, help="纬度 例 34.27 徐州")
    ap.add_argument("--lon", type=float, required=True, help="经度 例 117.18 徐州")
    ap.add_argument("--kwp", type=float, default=1.0, help="额定容量 kWp（默认1）")
    ap.add_argument("--loss", type=float, default=14.0, help="系统损耗 %% 默认14")
    ap.add_argument("--tilt", type=float, default=30.0, help="倾角 度 默认30")
    ap.add_argument("--aspect", type=float, default=0.0, help="方位角 度 默认0（朝南）")
    ap.add_argument("--startyear", type=int, default=None)
    ap.add_argument("--endyear", type=int, default=None)
    ap.add_argument("--output", type=Path, required=True, help="输出CSV路径")
    ap.add_argument("--dry-run", action="store_true", help="只构造URL不发起请求")
    args = ap.parse_args()

    if args.dry_run:
        params = parse.urlencode({
            "lat": args.lat, "lon": args.lon, "outputformat": "json",
            "pvcalculation": 1, "peakpower": args.kwp, "loss": args.loss,
            "angle": args.tilt, "aspect": args.aspect,
        })
        print(f"[DRY] {PVGIS_BASE_URL}?{params}")
        return 0

    data = fetch(
        args.lat, args.lon,
        kwp=args.kwp, loss=args.loss, tilt=args.tilt, aspect=args.aspect,
        startyear=args.startyear, endyear=args.endyear,
    )
    n = to_csv(data, args.output)
    s = summarize(data, peakpower_kwp=args.kwp)
    print(f"[SUMMARY]")
    for k, v in s.items():
        print(f"  {k:25s} = {v}")
    return 0 if n > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
