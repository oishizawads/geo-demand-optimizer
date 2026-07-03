"""仮想データの生成。

全データは seed 固定で合成した架空の地点。実在クライアントの計画とは無関係。
地名は一般化し、座標は中立的な範囲に配置する。
"""

from __future__ import annotations

import numpy as np

from .models import DemandPoint, SupplyFacility

_LAT_RANGE = (35.05, 35.95)
_LON_RANGE = (139.55, 140.45)
_DEMAND_RANGE = (60, 520)
_BASE_SEED = 42


def generate_demand_points(n: int, seed: int = _BASE_SEED) -> list[DemandPoint]:
    """需要地点を seed 固定で合成する。

    Args:
        n: 生成する地点数。
        seed: 乱数シード。

    Returns:
        合成された需要地点のリスト。
    """
    if n < 0:
        raise ValueError("地点数は0以上である必要があります")
    rng = np.random.default_rng(seed)
    lats = rng.uniform(_LAT_RANGE[0], _LAT_RANGE[1], n)
    lons = rng.uniform(_LON_RANGE[0], _LON_RANGE[1], n)
    demands = rng.integers(_DEMAND_RANGE[0], _DEMAND_RANGE[1] + 1, n)
    points: list[DemandPoint] = []
    for i in range(n):
        points.append(
            DemandPoint(
                id=f"D-{i + 1:02d}",
                name=f"Zone D-{i + 1:02d}",
                lat=float(lats[i]),
                lon=float(lons[i]),
                demand=int(demands[i]),
            )
        )
    return points


def scale_demand(points: list[DemandPoint], scale: float) -> list[DemandPoint]:
    """需要量を一括スケールする（シナリオ peak 等で使用）。

    Args:
        points: 元の需要地点リスト。
        scale: スケール係数（>0）。

    Returns:
        需要量をスケールした新しい需要地点リスト。
    """
    if scale <= 0:
        raise ValueError("スケールは正の値である必要があります")
    return [
        DemandPoint(
            id=p.id,
            name=p.name,
            lat=p.lat,
            lon=p.lon,
            demand=round(p.demand * scale, 1),
        )
        for p in points
    ]


# ベース供給拠点（seed固定ではなく固定配置。容量ゼロ拠点を1つ含めて堅牢性確認用にする）
BASE_FACILITIES: list[SupplyFacility] = [
    SupplyFacility(id="H-01", name="Hub H-01", lat=35.45, lon=139.75, capacity=1800),
    SupplyFacility(id="H-02", name="Hub H-02", lat=35.70, lon=140.05, capacity=1500),
    SupplyFacility(id="H-03", name="Hub H-03", lat=35.20, lon=140.20, capacity=1200),
    SupplyFacility(id="H-04", name="Hub H-04", lat=35.85, lon=139.65, capacity=0),
    SupplyFacility(id="H-05", name="Hub H-05", lat=35.35, lon=140.35, capacity=900),
]

# expansion シナリオで追加する拠点
EXTRA_FACILITIES: list[SupplyFacility] = [
    SupplyFacility(id="H-06", name="Hub H-06 (new)", lat=35.60, lon=139.90, capacity=1400),
    SupplyFacility(id="H-07", name="Hub H-07 (new)", lat=35.15, lon=139.85, capacity=1000),
]


def get_base_facilities() -> list[SupplyFacility]:
    """ベース供給拠点のコピーを返す。"""
    return list(BASE_FACILITIES)


def get_expansion_facilities() -> list[SupplyFacility]:
    """ベース + 追加の供給拠点を返す。"""
    return list(BASE_FACILITIES) + list(EXTRA_FACILITIES)
