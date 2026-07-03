"""データモデル定義。

需要地点・供給拠点・割当結果を表す dataclass を提供する。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DemandPoint:
    """需要地点。

    Attributes:
        id: 一意識別子。
        name: 表示用名称（一般化した仮想地名）。
        lat: 緯度。
        lon: 経度。
        demand: 需要量（>=0）。
    """

    id: str
    name: str
    lat: float
    lon: float
    demand: float


@dataclass(frozen=True)
class SupplyFacility:
    """供給拠点。

    容量ゼロの拠点も許容する（休止拠点として扱い、落ちないようにする）。

    Attributes:
        id: 一意識別子。
        name: 表示用名称。
        lat: 緯度。
        lon: 経度。
        capacity: 容量上限（>=0）。
    """

    id: str
    name: str
    lat: float
    lon: float
    capacity: float


@dataclass(frozen=True)
class Assignment:
    """1件の割当。

    Attributes:
        demand_id: 需要地点ID。
        facility_id: 割当先拠点ID。
        amount: 割当量。
        distance_km: 地点と拠点間の直線距離(km)。
    """

    demand_id: str
    facility_id: str
    amount: float
    distance_km: float


@dataclass(frozen=True)
class Unassigned:
    """割当できなかった需要。

    Attributes:
        demand_id: 需要地点ID。
        amount: 未割当量。
        nearest_facility_id: 最も近い拠点ID（参考）。
        nearest_distance_km: 最寄り拠点までの距離(km)。
    """

    demand_id: str
    amount: float
    nearest_facility_id: str
    nearest_distance_km: float


@dataclass
class AssignmentResult:
    """割当計算の全体結果。

    Attributes:
        assignments: 成立した割当のリスト。
        unassigned: 容量不足で割当できなかった需要。
        facility_loads: 拠点ID -> 割当済合計量。
        facility_capacities: 拠点ID -> 容量。
    """

    assignments: list[Assignment] = field(default_factory=list)
    unassigned: list[Unassigned] = field(default_factory=list)
    facility_loads: dict[str, float] = field(default_factory=dict)
    facility_capacities: dict[str, float] = field(default_factory=dict)

    @property
    def total_demand(self) -> float:
        """総需要（割当済 + 未割当）。"""
        return sum(a.amount for a in self.assignments) + sum(
            u.amount for u in self.unassigned
        )

    @property
    def total_assigned(self) -> float:
        """割当済需要合計。"""
        return sum(a.amount for a in self.assignments)

    @property
    def total_capacity(self) -> float:
        """総容量。"""
        return sum(self.facility_capacities.values())

    @property
    def total_unassigned(self) -> float:
        """未割当（容量不足）需要合計。"""
        return sum(u.amount for u in self.unassigned)

    @property
    def total_surplus(self) -> float:
        """総余剰容量。"""
        return sum(
            max(0.0, self.facility_capacities.get(fid, 0.0) - load)
            for fid, load in self.facility_loads.items()
        )

    @property
    def avg_distance_km(self) -> float:
        """割当済の需要重み付き平均距離(km)。割当が無ければ0。"""
        total = self.total_assigned
        if total <= 0:
            return 0.0
        return sum(a.amount * a.distance_km for a in self.assignments) / total

    @property
    def utilization_rate(self) -> float:
        """総容量に対する割当済の割合(0-1)。容量0の時は0。"""
        cap = self.total_capacity
        if cap <= 0:
            return 0.0
        return min(1.0, self.total_assigned / cap)
