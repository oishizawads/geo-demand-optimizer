# Geo Demand Optimizer

需要地点と供給拠点を地図上で可視化し、最近傍貪欲割当と容量不足（Capacity Gap）を示す小型 Streamlit アプリ。シナリオを切り替えて需要増・拠点追加の影響を比較できる。

## 目的

物流・配送・サービス拠点の需要と供給のミスマッチを、地図と数値で直感的に把握する。最適化そのものではなく、**どこが不足し、どこに余剰があるか**を可視化し意思決定を助けることを目的とする。

## 主要機能

- **Map**: 需要地点（青円）と供給拠点（緑=稼働 / 赤=満杯 / 灰=容量0の休止）と割当線を地図表示
- **Demand Settings**: シナリオ選択、需要地点数の調整、需要スケールの適用
- **Assignment Result**: 拠点別サマリ（容量・割当量・余剰・利用率）と需要地点別の割当表
- **Capacity Gap**: 容量不足で割当できなかった需要の一覧と、拠点別余剰
- **Scenario Comparison**: baseline / peak / expansion の3シナリオを横並びで比較

## 使用技術

- Python 3.11+
- Streamlit（UI）
- folium + OpenStreetMapタイル（キー不要の地図描画）
- numpy（haversine 距離行列・ベクトル化計算）
- pandas（表表示）
- pytest（割当ロジックのテスト）

## データの出所

全データは **架空の合成データ** である。`src/data.py` が seed 固定（`seed=42`）で緯度経度・需要量を生成し、地名は `Zone D-01` / `Hub H-01` のように一般化している。実在クライアントの計画や実在地名とは無関係。

## ローカル実行手順

```bash
cd geo-demand-optimizer
python -m venv .venv && source .venv/bin/activate   # 任意
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

テスト:

```bash
pytest
```

## ディレクトリ構成

```
geo-demand-optimizer/
├── app/
│   └── streamlit_app.py      # エントリポイント（画面は薄く）
├── src/
│   ├── models.py             # データモデル（dataclass）
│   ├── data.py               # 仮想データ生成（seed固定）
│   ├── assignment.py         # 割当・距離計算ロジック
│   └── scenarios.py          # シナリオ定義
├── tests/
│   └── test_assignment.py    # 割当関数のテスト
├── assets/                   # スクショ置き場
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## スクリーンショット

画面キャプチャは `assets/` に配置する。

## 制限事項

- **MVP 範囲**: 認証・DB・本番運用・課金・複雑な状態管理は含まない
- **最適化**: 最近傍貪欲法（容量制約付き）であり、厳密最適解ではない。需要が大きい順に優先割当する啓発的手法。将来的に `scipy.optimize.linprog` で厳密な輸送問題に拡張可能
- **分割割当あり**: 1需要地点が複数拠点に分割割当される場合がある。需要が大きい順に優先し、距離が近い拠点から順に残容量を充てる
- **距離**: 直線距離（haversine）であり、道路ネットワーク距離ではない
- **地図タイル**: キー不要の OpenStreetMap を使用。APIキーは不要
- **データ**: 仮想データ。実データでの検証は行っていない

## 設計メモ

- UI と計算ロジックを分離: 割当・最適化は `src/assignment.py`、画面は `app/streamlit_app.py` から呼ぶだけ
- 入力バリデーション: 容量ゼロ拠点・負の容量・需要0の地点いずれでも落ちない
- パスは `pathlib.Path` 基準、絶対パス直書きなし
- APIキーは直書きせず環境変数から（本アプリはキー不要で動作）
