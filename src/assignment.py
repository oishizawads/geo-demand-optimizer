"""割当・最適化ロジック。

需要地点を容量制約付きで最寄りの供給拠点に割当てる貪欲法（簡易最適化）。
計算ロジックはここに集約し、Streamlit 画面からは呼ぶだけにする。
"""

from __future__ import annotations

import numpy as np

from .models import (
    Assignment,
    AssignmentResult,
    DemandPoint,
    SupplyFacility,
    Unassigned,
)

_EARTH_RADIUS_KM = 6371.0088


def haversine_matrix(
    demand_points: list[DemandPoint], facilities: list[SupplyFacility]
) -> np.ndarray:
    """需要地点×拠点の haversine 距離行列(km)を返す。

    numpy ベースのベクトル化実装（scipy の cdist haversine はバージョン依存があるため自前）。

    Args:
        demand_points: 需要地点リスト。
        facilities: 供給拠点リスト。

    Returns:
        shape (n_demand, n_facility) の距離行列(km)。いずれかが空なら zeros。
    """
    n_d = len(demand_points)
    n_f = len(facilities)
    if n_d == 0 or n_f == 0:
        return np.zeros((n_d, n_f))
    d_lat = np.radians(np.array([p.lat for p in demand_points]))[:, None]
    d_lon = np.radians(np.array([p.lon for p in demand_points]))[:, None]
    f_lat = np.radians(np.array([f.lat for f in facilities]))[None, :]
    f_lon = np.radians(np.array([f.lon for f in facilities]))[None, :]
    dlat = f_lat - d_lat
    dlon = f_lon - d_lon
    a = np.sin(dlat / 2.0) ** 2 + np.cos(d_lat) * np.cos(f_lat) * np.sin(dlon / 2.0) ** 2
    a = np.clip(a, 0.0, 1.0)
    return 2.0 * _EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _safe_capacity(f: SupplyFacility) -> float:
    """容量の負値を0にクリップする。"""
    return max(0.0, float(f.capacity))


def _safe_demand(p: DemandPoint) -> float:
    """需要の負値を0にクリップする。"""
    return max(0.0, float(p.demand))


def assign_nearest_with_capacity(
    demand_points: list[DemandPoint],
    facilities: list[SupplyFacility],
) -> AssignmentResult:
    """容量制約付き最近傍貪欲割当を行う。

    各需要地点を最も近い利用可能（残容量>0）拠点に全量割当てる。
    需要量がどの拠点の残容量も超える場合は未割当（容量ギャップ）とする。
    容量ゼロの拠点は利用不可として安全に扱う。

    Args:
        demand_points: 需要地点リスト。
        facilities: 供給拠点リスト。

    Returns:
        割当結果。
    """
    if not facilities:
        # 拠点が無ければ全需要が未割当（最寄り拠点も無し）
        return AssignmentResult(
            unassigned=[
                Unassigned(
                    demand_id=p.id,
                    amount=_safe_demand(p),
                    nearest_facility_id="",
                    nearest_distance_km=0.0,
                )
                for p in demand_points
            ],
            facility_capacities={},
        )
    if not demand_points:
        return AssignmentResult(
            facility_capacities={f.id: _safe_capacity(f) for f in facilities}
        )

    dist = haversine_matrix(demand_points, facilities)
    remaining = {f.id: _safe_capacity(f) for f in facilities}
    capacities = dict(remaining)
    id_to_fac = {f.id: f for f in facilities}

    assignments: list[Assignment] = []
    unassigned: list[Unassigned] = []
    loads: dict[str, float] = {f.id: 0.0 for f in facilities}

    # 需要量が大きい順に割当てる（大きい需要ほど拠点選択肢が限られるため優先）
    order = sorted(
        range(len(demand_points)),
        key=lambda i: _safe_demand(demand_points[i]),
        reverse=True,
    )

    for i in order:
        point = demand_points[i]
        need = _safe_demand(point)
        if need <= 0:
            continue

        row = dist[i]
        # 距離昇順の拠点インデックス
        fac_order = np.argsort(row)
        for fi in fac_order:
            if need <= 0:
                break
            fac = facilities[fi]
            if remaining[fac.id] <= 0:
                continue
            alloc = min(need, remaining[fac.id])
            assignments.append(
                Assignment(
                    demand_id=point.id,
                    facility_id=fac.id,
                    amount=alloc,
                    distance_km=float(row[fi]),
                )
            )
            remaining[fac.id] -= alloc
            loads[fac.id] += alloc
            need -= alloc

        if need > 0:
            # 未割当残: 全拠点中の最寄りを参考情報として記録
            nearest_idx = int(np.argmin(row))
            nearest_fac = facilities[nearest_idx]
            unassigned.append(
                Unassigned(
                    demand_id=point.id,
                    amount=need,
                    nearest_facility_id=nearest_fac.id,
                    nearest_distance_km=float(row[nearest_idx]),
                )
            )

    return AssignmentResult(
        assignments=assignments,
        unassigned=unassigned,
        facility_loads=loads,
        facility_capacities=capacities,
    )


def facility_summary(result: AssignmentResult) -> list[dict]:
    """拠点別の容量・負荷・余剰・利用率を行データとして返す（表表示用）。

    Args:
        result: 割当結果。

    Returns:
        拠点ごとのサマリ辞書のリスト（id, name, capacity, load, surplus, utilization）。
    """
    rows: list[dict] = []
    for fid, cap in result.facility_capacities.items():
        load = result.facility_loads.get(fid, 0.0)
        surplus = max(0.0, cap - load)
        util = (load / cap) if cap > 0 else 0.0
        rows.append(
            {
                "拠点ID": fid,
                "拠点名": fid,
                "容量": round(cap, 1),
                "割当量": round(load, 1),
                "余剰": round(surplus, 1),
                "利用率": round(util, 3),
            }
        )
    return rows
