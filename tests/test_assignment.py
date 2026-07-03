"""割当・データ・シナリオの最低限のテスト。

実行: pytest
"""

from __future__ import annotations

import pytest

from src.assignment import (
    assign_nearest_with_capacity,
    facility_summary,
    haversine_matrix,
)
from src.data import (
    generate_demand_points,
    get_base_facilities,
    get_expansion_facilities,
    scale_demand,
)
from src.models import DemandPoint, SupplyFacility
from src.scenarios import build_scenarios, scenario_order


# --- 割当ロジック -----------------------------------------------------------


def test_assign_basic_nearest():
    """需要は最寄りの容量十分な拠点に割当てられる。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    f = [
        SupplyFacility(id="F1", name="F1", lat=35.51, lon=140.01, capacity=1000),
        SupplyFacility(id="F2", name="F2", lat=36.0, lon=141.0, capacity=1000),
    ]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_assigned == 100
    assert r.assignments[0].facility_id == "F1"
    assert r.total_unassigned == 0


def test_capacity_zero_facility_safe():
    """容量ゼロの拠点だけの場合、未割当になるが落ちない。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    f = [SupplyFacility(id="F1", name="F1", lat=35.51, lon=140.01, capacity=0)]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_assigned == 0
    assert r.total_unassigned == 100
    assert r.unassigned[0].nearest_facility_id == "F1"


def test_capacity_shortage_unassigned():
    """容量不足分は未割当として記録される。"""
    p = [
        DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=600),
        DemandPoint(id="D2", name="D2", lat=35.51, lon=140.01, demand=600),
    ]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=1000)]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_assigned == 1000
    assert r.total_unassigned == 200
    assert len(r.unassigned) == 1


def test_demand_priority_large_first():
    """需要量が大きい地点が優先して割当てられる（分割割当で残を小需要に回す）。"""
    p = [
        DemandPoint(id="small", name="small", lat=35.5, lon=140.0, demand=100),
        DemandPoint(id="large", name="large", lat=35.5, lon=140.0, demand=800),
    ]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=850)]
    r = assign_nearest_with_capacity(p, f)
    # large(800)が先に全額割当 → small(100)は残50のみ割当、50が未割当
    assert r.total_assigned == 850
    assert r.total_unassigned == 50


def test_no_facility_all_unassigned():
    """拠点が無ければ全需要が未割当になる（落ちない）。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    r = assign_nearest_with_capacity(p, [])
    assert r.total_assigned == 0
    assert r.total_unassigned == 100


def test_no_demand_safe():
    """需要地点が無ければ結果は空（落ちない）。"""
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=500)]
    r = assign_nearest_with_capacity([], f)
    assert r.total_assigned == 0
    assert r.total_unassigned == 0
    assert r.total_capacity == 500


def test_negative_capacity_clipped():
    """負の容量は0として扱い、落ちない。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=-100)]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_assigned == 0
    assert r.total_unassigned == 100


def test_zero_demand_skipped():
    """需要0の地点は割当対象にならない。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=0)]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=500)]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_assigned == 0
    assert r.total_unassigned == 0


# --- 距離とサマリ -----------------------------------------------------------


def test_haversine_matrix_shape_and_nonneg():
    """距離行列の形状と非負を確認。"""
    p = generate_demand_points(5)
    f = get_base_facilities()
    m = haversine_matrix(p, f)
    assert m.shape == (5, len(f))
    assert (m >= 0).all()


def test_haversine_matrix_empty():
    """空入力の距離行列は zeros。"""
    assert haversine_matrix([], get_base_facilities()).shape == (0, 5)
    assert haversine_matrix(generate_demand_points(3), []).shape == (3, 0)


def test_facility_summary_rows():
    """拠点サマリが全拠点分出力される。"""
    p = generate_demand_points(6)
    f = get_base_facilities()
    r = assign_nearest_with_capacity(p, f)
    rows = facility_summary(r)
    assert len(rows) == len(f)
    for row in rows:
        assert 0.0 <= row["利用率"] <= 1.0
        assert row["余剰"] >= 0.0


def test_result_properties():
    """集計プロパティの整合性。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=500)]
    r = assign_nearest_with_capacity(p, f)
    assert r.total_demand == 100
    assert r.total_capacity == 500
    assert r.total_surplus == 400
    assert r.utilization_rate == pytest.approx(0.2)
    assert r.avg_distance_km >= 0.0


def test_utilization_rate_zero_capacity():
    """容量0の時は利用率0。"""
    p = [DemandPoint(id="D1", name="D1", lat=35.5, lon=140.0, demand=100)]
    f = [SupplyFacility(id="F1", name="F1", lat=35.5, lon=140.0, capacity=0)]
    r = assign_nearest_with_capacity(p, f)
    assert r.utilization_rate == 0.0


# --- データとシナリオ -------------------------------------------------------


def test_seed_reproducible():
    """同 seed で同じデータが生成される。"""
    a = generate_demand_points(10, seed=42)
    b = generate_demand_points(10, seed=42)
    assert [p.demand for p in a] == [p.demand for p in b]
    assert [p.lat for p in a] == [p.lat for p in b]


def test_seed_different():
    """異 seed で異なるデータ。"""
    a = generate_demand_points(10, seed=42)
    b = generate_demand_points(10, seed=7)
    assert [p.lat for p in a] != [p.lat for p in b]


def test_scale_demand():
    """需要スケールが正しく掛かる。"""
    p = generate_demand_points(3)
    scaled = scale_demand(p, 2.0)
    for a, b in zip(p, scaled):
        assert abs(b.demand - a.demand * 2.0) < 0.01


def test_scale_demand_invalid():
    """0/負のスケールは ValueError。"""
    p = generate_demand_points(2)
    with pytest.raises(ValueError):
        scale_demand(p, 0.0)
    with pytest.raises(ValueError):
        scale_demand(p, -1.0)


def test_generate_demand_invalid():
    """負の地点数は ValueError。"""
    with pytest.raises(ValueError):
        generate_demand_points(-1)


def test_base_facilities_include_zero_capacity():
    """ベース拠点に容量0の休止拠点が含まれる（堅牢性確認用）。"""
    f = get_base_facilities()
    assert any(x.capacity == 0 for x in f)


def test_expansion_has_more_facilities():
    """expansion は baseline より拠点が多い。"""
    assert len(get_expansion_facilities()) > len(get_base_facilities())


def test_scenarios_consistent():
    """全シナリオが整合して構築される。"""
    sc = build_scenarios(12)
    for k in scenario_order():
        assert k in sc
        assert len(sc[k].demand_points) == 12
        assert len(sc[k].facilities) > 0
    assert len(sc["expansion"].facilities) > len(sc["baseline"].facilities)
    # peak は baseline より総需要が大きい
    assert sc["peak"].demand_points[0].demand > sc["baseline"].demand_points[0].demand


def test_scenario_key_order():
    """シナリオ順序は baseline -> peak -> expansion。"""
    assert scenario_order() == ["baseline", "peak", "expansion"]
