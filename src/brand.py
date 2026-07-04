"""Portfolio Design System v2 "Ink & Signal" — Streamlit 共通ブランドテーマ。

portfolio-hub と12デモで視覚言語を揃える単一ファイル。外部依存なし。
正典: portfolio-plan/brand/brand.py（各リポの src/brand.py へそのままコピーする）
仕様: portfolio-plan/design-system.md

各アプリの ``streamlit_app.py`` から::

    from src.brand import apply_brand, hero, section, sidebar_header, footer_backlink
    apply_brand(st)                      # set_page_config の後に一度だけ
    hero(st, "KICKER", "タイトル", "サブ説明", chips=["python", "altair"])
    ...
    footer_backlink(st, repo="rag-eval-dashboard")

Altair を使うアプリは import 直後に::

    import altair as alt
    from src.brand import themed_altair
    themed_altair(alt)

Plotly を使うアプリは figure ごとに::

    fig.update_layout(**plotly_template())
"""

from __future__ import annotations

PALETTE = ["#0f766e", "#2563eb", "#d97706", "#be185d", "#7c3aed", "#64748b"]

_FONT_BODY = "'Inter', 'Noto Sans JP', system-ui, sans-serif"
_FONT_DISPLAY = "'Space Grotesk', 'Inter', 'Noto Sans JP', sans-serif"
_FONT_MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace"

_BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
/* stlite は Material Symbols を同梱しないため明示ロード（expander 矢印等の豆腐化防止） */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

:root {
  --bg:#f6f7f9; --fg:#0d1526; --muted:#5b6474;
  --surface:#ffffff;
  --line:rgba(13,21,38,0.10); --line-strong:rgba(13,21,38,0.20);
  --accent:#0f766e; --accent-strong:#115e59; --link:#2563eb; --dark:#0b1220;
  --shadow:0 1px 2px rgba(13,21,38,.05), 0 8px 24px rgba(13,21,38,.06);
  --shadow-hover:0 2px 4px rgba(13,21,38,.06), 0 16px 40px rgba(13,21,38,.10);
}

/* typography（アイコンフォントは触らない） */
html, body, .stApp, .stMarkdown, p, li,
span:not([data-testid="stIconMaterial"]):not([class*="material-symbols"]),
label, button, input, textarea, select,
[data-testid="stWidgetLabel"], [data-testid="stMetricLabel"] {
  font-family: 'Inter', 'Noto Sans JP', system-ui, sans-serif;
}
/* Material Symbols のリガチャを死守（expander 矢印等） */
[data-testid="stIconMaterial"], [class*="material-symbols"] {
  font-family: 'Material Symbols Rounded' !important;
}
h1, h2, h3, h4 {
  font-family: 'Space Grotesk', 'Inter', 'Noto Sans JP', sans-serif;
}
code, pre, kbd,
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
  font-family: 'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace;
  font-variant-numeric: tabular-nums;
}

/* 背景：ほぼ無地＋上部にごく薄い teal の気配 */
.stApp {
  background:
    radial-gradient(1200px 480px at 50% -160px, rgba(15,118,110,0.07), transparent 70%),
    #f6f7f9;
  color: var(--fg);
}

/* Streamlit クロームを控えめに */
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; height: 0; }
[data-testid="stDecoration"] { display: none; }

/* 本文幅と余白 */
.block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3rem;
}

/* 見出し */
h1 { font-weight: 700 !important; letter-spacing: -0.03em; line-height: 1.08; color: var(--fg); }
h2 { font-weight: 700 !important; letter-spacing: -0.02em; color: var(--fg); }
h3 { font-weight: 700 !important; letter-spacing: -0.01em; color: var(--fg); }

/* Hero ブロック */
.brand-hero { margin: 4px 0 34px; }
.brand-kicker {
  color: var(--accent); font-size: .75rem; font-weight: 700;
  letter-spacing: .14em; text-transform: uppercase; margin-bottom: 10px;
}
.brand-title {
  font-family: 'Space Grotesk', 'Inter', 'Noto Sans JP', sans-serif;
  font-size: clamp(2.1rem, 4.5vw, 3.2rem); font-weight: 700;
  line-height: 1.08; letter-spacing: -0.03em; color: var(--fg); margin: 0;
}
.brand-sub {
  color: var(--muted); font-size: 1rem; line-height: 1.8;
  margin-top: 14px; max-width: 760px;
}
.brand-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.brand-chip {
  border: 1px solid var(--line); border-radius: 999px; background: var(--surface);
  padding: 4px 12px; color: var(--muted); font-size: .78rem; font-weight: 600;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
}

/* セクション見出し */
.brand-section { margin: 34px 0 6px; }
.brand-section .brand-kicker { margin-bottom: 6px; }
.brand-section-title {
  font-family: 'Space Grotesk', 'Inter', 'Noto Sans JP', sans-serif;
  font-size: 1.45rem; font-weight: 700; letter-spacing: -0.02em;
  color: var(--fg); margin: 0;
}

/* サイドバー：不透明サーフェス */
[data-testid="stSidebar"] {
  background: #fbfcfd;
  border-right: 1px solid var(--line);
}
.brand-side-title {
  font-family: 'Space Grotesk', 'Inter', 'Noto Sans JP', sans-serif;
  font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em;
  color: var(--fg); margin: 2px 0 2px;
}

/* metric をカード化（左に accent の芯） */
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line); border-left: 3px solid var(--accent);
  border-radius: 12px; padding: 14px 16px; box-shadow: var(--shadow);
}
[data-testid="stMetricValue"] { color: var(--fg); font-weight: 600; }
[data-testid="stMetricLabel"] {
  color: var(--muted); font-size: .74rem; font-weight: 600;
  letter-spacing: .08em; text-transform: uppercase;
}

/* ボタン */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 10px; border: 1px solid var(--fg); background: var(--fg);
  color: #fff; font-weight: 600; padding: 8px 18px;
  transition: transform .15s ease, background .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: var(--dark); border-color: var(--dark); color: #fff;
  transform: translateY(-1px); box-shadow: var(--shadow);
}

/* タブ */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-weight: 600; color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--accent-strong); }

/* 表・expander をカード化 */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
  box-shadow: var(--shadow); background: var(--surface);
}
[data-testid="stExpander"] {
  border: 1px solid var(--line); border-radius: 12px;
  background: var(--surface); box-shadow: var(--shadow);
}

/* 入力の角丸 */
[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea,
.stNumberInput input { border-radius: 10px !important; }

/* 通知・区切り・リンク */
[data-testid="stNotification"], .stAlert { border-radius: 10px; }
hr { border-color: var(--line); }
a { color: var(--link); }

/* 静的テーブル（st.dataframe の stlite 代替） */
.brand-table-wrap {
  overflow-x: auto; border: 1px solid var(--line); border-radius: 12px;
  background: var(--surface); box-shadow: var(--shadow);
}
.brand-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.brand-table th {
  text-align: left; color: var(--muted); font-size: .72rem; font-weight: 600;
  letter-spacing: .06em; text-transform: uppercase;
  padding: 10px 14px; border-bottom: 1px solid var(--line-strong); background: #fbfcfd;
}
.brand-table td {
  padding: 9px 14px; border-bottom: 1px solid var(--line);
  color: var(--fg); font-variant-numeric: tabular-nums;
}
.brand-table tr:last-child td { border-bottom: none; }

/* フッター */
.brand-footer {
  margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--line);
  display: flex; flex-wrap: wrap; gap: 8px 20px;
  align-items: center; justify-content: space-between;
  color: var(--muted); font-size: .82rem; line-height: 1.7;
}
.brand-footer a { color: var(--accent-strong); font-weight: 600; text-decoration: none; }
.brand-footer a:hover { text-decoration: underline; }
</style>
"""

HUB_URL = "https://oishizawads.github.io/portfolio-hub/"
GITHUB_OWNER = "oishizawads"


def apply_brand(st) -> None:
    """ブランド CSS を注入する。``st.set_page_config`` の後に一度だけ呼ぶ。"""
    st.markdown(_BRAND_CSS, unsafe_allow_html=True)


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def hero(
    st,
    kicker: str,
    title: str,
    subtitle: str | None = None,
    chips: list[str] | None = None,
) -> None:
    """ヒーロー見出し（キッカー + 大見出し + サブ説明 + 技術チップ）。"""
    html = (
        '<div class="brand-hero">'
        f'<div class="brand-kicker">{_esc(kicker)}</div>'
        f'<div class="brand-title">{_esc(title)}</div>'
    )
    if subtitle:
        html += f'<div class="brand-sub">{_esc(subtitle)}</div>'
    if chips:
        html += '<div class="brand-chips">'
        html += "".join(f'<span class="brand-chip">{_esc(c)}</span>' for c in chips)
        html += "</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section(st, kicker: str, title: str) -> None:
    """本文セクション見出し（kicker + タイトル）。``st.header`` の代替。"""
    st.markdown(
        '<div class="brand-section">'
        f'<div class="brand-kicker">{_esc(kicker)}</div>'
        f'<div class="brand-section-title">{_esc(title)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def sidebar_header(st, title: str, caption: str | None = None) -> None:
    """サイドバー先頭の見出し。"""
    html = (
        '<div class="brand-kicker" style="margin-top:4px">Controls</div>'
        f'<div class="brand-side-title">{_esc(title)}</div>'
    )
    st.sidebar.markdown(html, unsafe_allow_html=True)
    if caption:
        st.sidebar.caption(caption)


def footer_backlink(st, repo: str | None = None) -> None:
    """合成データ注記と Portfolio Hub への戻りリンクを持つ共通フッター。"""
    links = f'<a href="{HUB_URL}">← Portfolio Hub</a>'
    if repo:
        links += (
            f' &nbsp; <a href="https://github.com/{GITHUB_OWNER}/{_esc(repo)}">'
            "GitHub ↗</a>"
        )
    st.markdown(
        '<div class="brand-footer">'
        "<span>Synthetic data demo — 数値はすべて合成データで、実在の精度・効果を示しません。</span>"
        f"<span>{links}</span>"
        "</div>",
        unsafe_allow_html=True,
    )


def show_table(st, df, hide_index: bool = True, float_fmt: str | None = None) -> None:
    """静的 HTML テーブルとして描画する。

    stlite 1.8 系では st.dataframe（glide-data-grid）が空描画になるため、
    デモの一覧表示はこのヘルパーで代替する。
    """
    data = df.copy()
    if float_fmt:
        for col in data.columns:
            if getattr(data[col].dtype, "kind", "") == "f":
                data[col] = data[col].map(lambda v: float_fmt.format(v))
    html = data.to_html(index=not hide_index, classes="brand-table", border=0)
    st.markdown(f'<div class="brand-table-wrap">{html}</div>', unsafe_allow_html=True)


def altair_config() -> dict:
    """ブランド仕様の Altair テーマ設定を返す。"""
    return {
        "config": {
            "background": "transparent",
            "font": _FONT_BODY,
            "range": {"category": PALETTE},
            "axis": {
                "labelFont": _FONT_BODY,
                "titleFont": _FONT_BODY,
                "labelColor": "#5b6474",
                "titleColor": "#0d1526",
                "titleFontWeight": 600,
                "labelFontSize": 12,
                "titleFontSize": 12,
                "gridColor": "rgba(13,21,38,0.08)",
                "domainColor": "rgba(13,21,38,0.20)",
                "tickColor": "rgba(13,21,38,0.20)",
            },
            "legend": {
                "labelFont": _FONT_BODY,
                "titleFont": _FONT_BODY,
                "labelColor": "#5b6474",
                "titleColor": "#0d1526",
            },
            "title": {
                "font": _FONT_DISPLAY,
                "color": "#0d1526",
                "fontSize": 15,
                "fontWeight": 700,
                "anchor": "start",
            },
            "view": {"stroke": "transparent"},
            "bar": {"color": PALETTE[0]},
            "line": {"color": PALETTE[0], "strokeWidth": 2.5},
            "point": {"color": PALETTE[0], "filled": True, "size": 70},
            "area": {"color": PALETTE[0], "opacity": 0.16, "line": True},
            "rule": {"color": "#5b6474"},
        }
    }


def themed_altair(alt) -> None:
    """Altair にブランドテーマを登録して有効化する（バージョン差異を吸収）。"""
    theme = altair_config

    try:  # altair >= 5.5
        alt.theme.register("brand", enable=True)(theme)
        return
    except Exception:
        pass
    try:  # altair < 5.5
        alt.themes.register("brand", theme)
        alt.themes.enable("brand")
    except Exception:
        pass


def set_plotly_theme() -> None:
    """plotly express が色を焼き込む前にブランドテンプレートを既定化する。

    figure 生成より前（import 直後）に一度だけ呼ぶ。
    """
    import plotly.graph_objects as go
    import plotly.io as pio

    pio.templates["brand"] = go.layout.Template(layout=plotly_template())
    pio.templates.default = "plotly_white+brand"


def plotly_template() -> dict:
    """``fig.update_layout(**plotly_template())`` で適用する共通レイアウト。"""
    grid = "rgba(13,21,38,0.08)"
    zero = "rgba(13,21,38,0.20)"
    return {
        "font": {"family": "Inter, Noto Sans JP, sans-serif", "color": "#0d1526", "size": 13},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "colorway": PALETTE,
        "xaxis": {"gridcolor": grid, "zerolinecolor": zero, "linecolor": zero},
        "yaxis": {"gridcolor": grid, "zerolinecolor": zero, "linecolor": zero},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
        "margin": {"t": 48, "r": 16, "b": 48, "l": 56},
        "hoverlabel": {"font": {"family": "Inter, Noto Sans JP, sans-serif"}},
    }
