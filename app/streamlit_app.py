"""Geo Demand Optimizer — Streamlit エントリポイント。

画面は薄く保ち、計算ロジックは src/ に委譲する。
実行: streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.assignment import assign_nearest_with_capacity, facility_summary
from src.data import scale_demand
from src.models import AssignmentResult, DemandPoint, SupplyFacility
from src.scenarios import build_scenarios, scenario_order


_MAP_HEIGHT = 560
_N_DEMAND_MIN = 6
_N_DEMAND_MAX = 60
_N_DEMAND_DEFAULT = 24


# --- キャッシュ付き計算 -----------------------------------------------------


@st.cache_data
def _load_scenarios(n_demand: int) -> dict:
    """シナリオ群を構築してキャッシュする。"""
    return build_scenarios(n_demand)


@st.cache_data
def _compute(
    n_demand: int, scenario_key: str, demand_scale: float
) -> tuple[AssignmentResult, list[DemandPoint], list[SupplyFacility]]:
    """指定条件で割当を計算し、結果と入力データを返す。"""
    scenarios = build_scenarios(n_demand)
    sc = scenarios[scenario_key]
    points = (
        scale_demand(sc.demand_points, demand_scale)
        if demand_scale != 1.0
        else list(sc.demand_points)
    )
    result = assign_nearest_with_capacity(points, sc.facilities)
    return result, points, list(sc.facilities)


# --- 地図構築 ---------------------------------------------------------------


def _build_map(
    points: list[DemandPoint],
    facilities: list[SupplyFacility],
    result: AssignmentResult,
) -> folium.Map:
    """需要地点・拠点・割当線を描いた folium 地図を返す。"""
    all_lats = [p.lat for p in points] + [f.lat for f in facilities]
    all_lons = [p.lon for p in points] + [f.lon for f in facilities]
    if not all_lats:
        center = [35.5, 140.0]
    else:
        center = [sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)]

    fmap = folium.Map(location=center, zoom_start=10, tiles="OpenStreetMap")

    fac_by_id = {f.id: f for f in facilities}
    pt_by_id = {p.id: p for p in points}

    # 割当線（需要→拠点）
    for a in result.assignments:
        p = pt_by_id.get(a.demand_id)
        f = fac_by_id.get(a.facility_id)
        if p is None or f is None:
            continue
        folium.PolyLine(
            [(p.lat, p.lon), (f.lat, f.lon)],
            color="#7a7a7a",
            weight=1,
            opacity=0.45,
        ).add_to(fmap)

    # 需要地点（青い円、サイズは需要量におおむね比例）
    for p in points:
        radius = max(3.0, min(13.0, p.demand / 55.0))
        folium.CircleMarker(
            location=[p.lat, p.lon],
            radius=radius,
            color="#2b7fd4",
            fill=True,
            fill_color="#2b7fd4",
            fill_opacity=0.55,
            popup=folium.Popup(
                f"<b>{p.name}</b><br>需要: {p.demand:.0f}", max_width=180
            ),
            tooltip=f"{p.name} / 需要 {p.demand:.0f}",
        ).add_to(fmap)

    # 供給拠点（マーカー、容量ゼロは灰・満杯は赤・それ以外は緑）
    for f in facilities:
        cap = max(0.0, f.capacity)
        load = result.facility_loads.get(f.id, 0.0)
        if cap == 0:
            color = "lightgray"
            status = "休止(容量0)"
        elif load >= cap:
            color = "red"
            status = "満杯"
        else:
            color = "green"
            status = "稼働"
        folium.Marker(
            location=[f.lat, f.lon],
            popup=folium.Popup(
                f"<b>{f.name}</b><br>容量: {cap:.0f}<br>割当: {load:.0f}<br>状態: {status}",
                max_width=200,
            ),
            tooltip=f"{f.name} / {status}",
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(fmap)

    return fmap


# --- 指標カード -------------------------------------------------------------


def _kpi_row(result: AssignmentResult) -> None:
    """主要指標をカードで並べる（モバイルでは縦に並ぶ）。"""
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("総需要", f"{result.total_demand:,.0f}")
    c2.metric("総容量", f"{result.total_capacity:,.0f}")
    c3.metric("割当済", f"{result.total_assigned:,.0f}")
    c4.metric("未割当(不足)", f"{result.total_unassigned:,.0f}")
    c5.metric("利用率", f"{result.utilization_rate:.1%}")


# --- 画面本体 ---------------------------------------------------------------


def main() -> None:
    st.set_page_config(
        page_title="Geo Demand Optimizer",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    from src.brand import apply_brand, hero
    apply_brand(st)
    hero(st, "Geospatial Optimization", "Geo Demand Optimizer", "需要地点と供給拠点を地図上で見せ、割当と容量不足を可視化します。")
    st.caption(
        "需要地点と供給拠点を地図上で可視化し、最近傍貪易割当と容量不足を示すMVP。"
        "データは全て架空（seed固定の合成データ）。"
    )

    # サイドバー: シナリオと地点数
    st.sidebar.header("設定")
    n_demand = st.sidebar.slider(
        "需要地点数", _N_DEMAND_MIN, _N_DEMAND_MAX, _N_DEMAND_DEFAULT, step=2
    )
    scenarios = _load_scenarios(n_demand)
    keys = scenario_order()
    scenario_key = st.sidebar.radio(
        "シナリオ",
        keys,
        format_func=lambda k: f"{scenarios[k].name} — {scenarios[k].description}",
    )
    st.sidebar.divider()
    st.sidebar.markdown(
        "**データについて**: 全地点は seed 固定の仮想データです。"
        "実在クライアントの計画とは無関係です。"
    )

    sc = scenarios[scenario_key]

    # 現在のスケール（ボタンで更新）
    if "demand_scale" not in st.session_state:
        st.session_state["demand_scale"] = 1.0

    # タブ
    tab_map, tab_settings, tab_assign, tab_gap, tab_cmp = st.tabs(
        ["Map", "Demand Settings", "Assignment Result", "Capacity Gap", "Scenario Comparison"]
    )

    # Demand Settings タブでスケールを調整 + 再計算ボタン
    with tab_settings:
        st.subheader("需要設定")
        st.markdown(f"**シナリオ**: {sc.name} — {sc.description}")
        st.markdown(f"**需要地点数**: {len(sc.demand_points)}  / **供給拠点数**: {len(sc.facilities)}")
        new_scale = st.slider(
            "需要スケール",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state["demand_scale"],
            step=0.1,
            help="シナリオの需要量にこの倍率を掛けます。適用ボタンで再割当します。",
        )
        if st.button("割当を再計算", type="primary"):
            st.session_state["demand_scale"] = new_scale
            st.success("需要スケールを適用し、割当を再計算しました。")
        st.caption(
            "ボタンは何度押しても同じ入力なら同じ結果になります（状態は壊れません）。"
        )

    demand_scale = st.session_state["demand_scale"]
    result, points, facilities = _compute(n_demand, scenario_key, demand_scale)

    # Map タブ
    with tab_map:
        _kpi_row(result)
        fmap = _build_map(points, facilities, result)
        components.html(fmap._repr_html_(), height=_MAP_HEIGHT)
        st.caption(
            "青円=需要地点（大きさは需要量）/ 緑マーカー=稼働拠点 / 赤=満杯 / 灰=容量0の休止拠点 / 線=割当"
        )

    # Assignment Result タブ
    with tab_assign:
        _kpi_row(result)
        st.subheader("拠点別サマリ")
        fac_rows = facility_summary(result)
        st.dataframe(pd.DataFrame(fac_rows), use_container_width=True, hide_index=True)

        st.subheader("需要地点別の割当")
        pt_by_id = {p.id: p for p in points}
        rows = []
        for a in result.assignments:
            p = pt_by_id.get(a.demand_id)
            rows.append(
                {
                    "需要地点": p.name if p else a.demand_id,
                    "割当先拠点": a.facility_id,
                    "割当量": round(a.amount, 1),
                    "距離(km)": round(a.distance_km, 2),
                }
            )
        for u in result.unassigned:
            p = pt_by_id.get(u.demand_id)
            rows.append(
                {
                    "需要地点": p.name if p else u.demand_id,
                    "割当先拠点": "（未割当）",
                    "割当量": 0.0,
                    "距離(km)": round(u.nearest_distance_km, 2),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Capacity Gap タブ
    with tab_gap:
        _kpi_row(result)
        st.subheader("容量不足（未割当需要）")
        if not result.unassigned:
            st.success("全ての需要を割当てました。容量不足はありません。")
        else:
            gap_total = result.total_unassigned
            st.error(f"未割当需要 合計: {gap_total:,.0f}")
            gap_rows = []
            pt_by_id = {p.id: p for p in points}
            for u in result.unassigned:
                p = pt_by_id.get(u.demand_id)
                gap_rows.append(
                    {
                        "需要地点": p.name if p else u.demand_id,
                        "未割当量": round(u.amount, 1),
                        "最寄り拠点": u.nearest_facility_id,
                        "最寄り拠点まで(km)": round(u.nearest_distance_km, 2),
                    }
                )
            st.dataframe(pd.DataFrame(gap_rows), use_container_width=True, hide_index=True)

        st.subheader("拠点別 余剰容量")
        surplus_rows = [r for r in facility_summary(result) if r["余剰"] > 0]
        if surplus_rows:
            st.dataframe(pd.DataFrame(surplus_rows), use_container_width=True, hide_index=True)
        else:
            st.info("余剰容量のある拠点はありません（全拠点が満杯または容量0）。")

    # Scenario Comparison タブ
    with tab_cmp:
        st.subheader("全シナリオ比較")
        cmp_rows = []
        for k in keys:
            s = scenarios[k]
            r, _, _ = _compute(n_demand, k, 1.0)
            cmp_rows.append(
                {
                    "シナリオ": s.name,
                    "需要地点": len(s.demand_points),
                    "拠点数": len(s.facilities),
                    "総需要": round(r.total_demand, 0),
                    "総容量": round(r.total_capacity, 0),
                    "割当済": round(r.total_assigned, 0),
                    "未割当": round(r.total_unassigned, 0),
                    "利用率": f"{r.utilization_rate:.1%}",
                    "平均距離(km)": round(r.avg_distance_km, 2),
                }
            )
        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)
        st.caption(
            "シナリオを切り替えると、未割当・利用率・平均距離が変化します。"
            "ピーク需要では不足が拡大し、拠点追加では不足が解消されることを確認できます。"
        )


if __name__ == "__main__":
    main()
