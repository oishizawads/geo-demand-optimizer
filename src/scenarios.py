"""シナリオ定義。

需要スケールと拠点構成の組み合わせで複数シナリオを提供し、
画面で切り替えて結果を比較できるようにする。
"""

from __future__ import annotations

from dataclasses import dataclass

from .data import (
    generate_demand_points,
    get_base_facilities,
    get_expansion_facilities,
    scale_demand,
)
from .models import DemandPoint, SupplyFacility

_DEFAULT_N_DEMAND = 24
_PEAK_SCALE = 1.6


@dataclass(frozen=True)
class Scenario:
    """1シナリオの定義。

    Attributes:
        key: シナリオ識別子。
        name: 表示名。
        description: シナリオの説明。
        demand_points: 需要地点リスト。
        facilities: 供給拠点リスト。
    """

    key: str
    name: str
    description: str
    demand_points: list[DemandPoint]
    facilities: list[SupplyFacility]


def build_scenarios(n_demand: int = _DEFAULT_N_DEMAND) -> dict[str, Scenario]:
    """全シナリオを構築して返す。

    Args:
        n_demand: 需要地点数（地点数を増やしても UI が崩れないか確認用）。

    Returns:
        シナリオキー -> Scenario の辞書。
    """
    if n_demand < 0:
        raise ValueError("需要地点数は0以上である必要があります")

    base_demand = generate_demand_points(n_demand)
    base_fac = get_base_facilities()
    exp_fac = get_expansion_facilities()

    return {
        "baseline": Scenario(
            key="baseline",
            name="Baseline",
            description="標準需要と既存拠点構成（現状）。",
            demand_points=list(base_demand),
            facilities=list(base_fac),
        ),
        "peak": Scenario(
            key="peak",
            name="Peak Demand",
            description=f"需要を {_PEAK_SCALE}x に増加。既存拠点でどこまで耐えるか。",
            demand_points=scale_demand(base_demand, _PEAK_SCALE),
            facilities=list(base_fac),
        ),
        "expansion": Scenario(
            key="expansion",
            name="Expansion",
            description="需要は標準のまま拠点を2件追加。余剰とカバレッジの変化を比較。",
            demand_points=list(base_demand),
            facilities=list(exp_fac),
        ),
    }


def scenario_order() -> list[str]:
    """表示順に並べたシナリオキー。"""
    return ["baseline", "peak", "expansion"]
