"""portfolio-hub と視覚言語を揃える共通ブランドテーマ（Streamlit 用）。

- near-white グラデ背景 / slate 文字 / teal・blue アクセント
- 半透明の白カード + blur / 8px 角丸 / uppercase キッカー + 大きな見出し

外部依存なし。各アプリの ``streamlit_app.py`` から::

    from src.brand import apply_brand, hero
    apply_brand(st)          # set_page_config の後に一度だけ
    hero(st, "Kicker", "タイトル", "サブ説明")
"""

from __future__ import annotations

_BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg:#f8fafc; --fg:#0f172a; --muted:rgba(15,23,42,0.66);
  --surface:rgba(255,255,255,0.82); --line:rgba(15,23,42,0.12);
  --accent:#0f766e; --accent2:#2563eb;
  --shadow:0 18px 50px rgba(15,23,42,0.08);
}

/* typography（アイコンフォントは触らない） */
html, body, .stApp, .stMarkdown, p, li, span, label,
h1, h2, h3, h4, button, input, textarea, select,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] {
  font-family: 'Inter', system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* 背景グラデ（portfolio-hub .portfolio-shell 相当） */
.stApp {
  background:
    linear-gradient(180deg, rgba(248,250,252,0.92), rgba(241,245,249,0.96) 42%, rgba(15,23,42,0.05)),
    radial-gradient(circle at 50% 0%, rgba(255,255,255,0.95), rgba(219,234,254,0.55) 42%, rgba(15,23,42,0.06));
  color: var(--fg);
}

/* Streamlit クロームを控えめに */
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; height: 0; }
[data-testid="stDecoration"] { display: none; }

/* 本文幅と余白 */
.block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem;
}

/* 見出し */
h1 { font-weight: 800 !important; letter-spacing: -0.02em; line-height: 1.05; color: var(--fg); }
h2 { font-weight: 700 !important; letter-spacing: -0.01em; color: var(--fg); }
h3 { font-weight: 700 !important; color: var(--fg); }

/* Hero ブロック */
.brand-hero { margin: 6px 0 30px; }
.brand-kicker {
  color: var(--accent); font-size: .78rem; font-weight: 700;
  letter-spacing: .15em; text-transform: uppercase; margin-bottom: 10px;
}
.brand-title {
  font-size: clamp(2.1rem, 5vw, 3.5rem); font-weight: 800;
  line-height: 1.03; letter-spacing: -0.025em; color: var(--fg); margin: 0;
}
.brand-sub {
  color: var(--muted); font-size: 1.02rem; line-height: 1.8;
  margin-top: 14px; max-width: 760px;
}

/* サイドバー = 半透明サーフェス */
[data-testid="stSidebar"] {
  background: rgba(255,255,255,0.72); backdrop-filter: blur(16px);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .brand-kicker { margin-top: 4px; }

/* metric をカード化 */
[data-testid="stMetric"] {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 12px; padding: 16px 18px; box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
}
[data-testid="stMetricValue"] { color: var(--fg); font-weight: 800; }
[data-testid="stMetricLabel"] { color: var(--muted); }

/* ボタン = ダークプライマリ */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 8px; border: 1px solid #0f172a; background: #0f172a;
  color: #fff; font-weight: 700; padding: 8px 16px;
  transition: transform .15s ease, background .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: #020617; transform: translateY(-1px); border-color: #0f172a; color: #fff;
}

/* タブ */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-weight: 700; color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--fg); }

/* 表・expander をカード化 */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
  box-shadow: var(--shadow);
}
[data-testid="stExpander"] {
  border: 1px solid var(--line); border-radius: 12px;
  background: var(--surface); box-shadow: var(--shadow);
}

/* 入力の角丸 */
[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea,
.stNumberInput input { border-radius: 8px !important; }

/* 通知・区切り */
[data-testid="stNotification"], .stAlert { border-radius: 10px; }
hr { border-color: var(--line); }
</style>
"""


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


def hero(st, kicker: str, title: str, subtitle: str | None = None) -> None:
    """portfolio-hub 風のヒーロー見出し（キッカー + 大見出し + サブ説明）。"""
    html = (
        '<div class="brand-hero">'
        f'<div class="brand-kicker">{_esc(kicker)}</div>'
        f'<div class="brand-title">{_esc(title)}</div>'
    )
    if subtitle:
        html += f'<div class="brand-sub">{_esc(subtitle)}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
