from __future__ import annotations

import streamlit as st

from . import palette as pal


class Theme:
    """Injecte le CSS responsive (mobile / tablette / desktop) et le
    composant d'habillage (bande d'accroche) alignés sur la palette du
    skill dataviz — un seul endroit à toucher pour changer l'apparence
    globale. Les cartes KPI utilisent st.metric natif (voir app.py)."""

    CSS = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: {pal.FONT_FAMILY};
    }}
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    /* ---- atmosphère de fond : wash très discret, jamais dans les cartes ---- */
    .stApp {{
        background:
            radial-gradient(ellipse 900px 480px at 6% -8%, {pal.CATEGORICAL[0]}14, transparent 60%),
            radial-gradient(ellipse 700px 420px at 100% 8%, {pal.CATEGORICAL[5]}12, transparent 55%),
            {pal.PAGE};
    }}

    @keyframes rise {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ---- panneau d'accroche ---- */
    .hero-panel {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 24px;
        margin-bottom: 1.4rem;
        border-radius: 16px;
        border: 1px solid {pal.GRID};
        background:
            linear-gradient(135deg, {pal.CATEGORICAL[0]}10 0%, transparent 45%),
            {pal.SURFACE};
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 12px 28px -18px rgba(11,11,11,0.18);
        animation: rise 0.5s ease both;
    }}
    .hero-badge {{
        flex: none;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        border-radius: 14px;
        background: linear-gradient(160deg, {pal.CATEGORICAL[0]}, {pal.CATEGORICAL[6]});
        box-shadow: 0 6px 16px -6px {pal.CATEGORICAL[0]}80;
    }}
    .hero-title {{
        font-family: {pal.DISPLAY_FONT};
        font-size: 1.95rem;
        font-weight: 600;
        color: {pal.INK_PRIMARY};
        letter-spacing: -0.01em;
        line-height: 1.15;
        margin: 0;
    }}
    .hero-sub {{
        color: {pal.INK_MUTED};
        font-size: 0.92rem;
        margin-top: 0.15rem;
    }}

    /* ---- cartes KPI (st.metric natif, border=True) ---- */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"] div[data-testid="stMetric"])
      > div[data-testid="column"] {{
        animation: rise 0.45s ease both;
    }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"] div[data-testid="stMetric"])
      > div[data-testid="column"]:nth-of-type(1) {{ animation-delay: 0.03s; }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"] div[data-testid="stMetric"])
      > div[data-testid="column"]:nth-of-type(2) {{ animation-delay: 0.10s; }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"] div[data-testid="stMetric"])
      > div[data-testid="column"]:nth-of-type(3) {{ animation-delay: 0.17s; }}
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"] div[data-testid="stMetric"])
      > div[data-testid="column"]:nth-of-type(4) {{ animation-delay: 0.24s; }}

    div[data-testid="stMetric"] {{
        background: {pal.SURFACE};
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 10px 22px -18px rgba(11,11,11,0.22);
        padding: 15px 18px 13px 18px;
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 16px 30px -14px rgba(11,11,11,0.16);
        border-color: {pal.CATEGORICAL[0]} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: {pal.MONO_FONT};
        font-variant-numeric: proportional-nums;
        letter-spacing: -0.01em;
    }}

    /* ---- cartes graphiques ---- */
    div[data-testid="stPlotlyChart"] {{
        background: {pal.SURFACE};
        border: 1px solid {pal.GRID};
        border-radius: 14px;
        padding: 8px 6px 2px 6px;
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 10px 22px -18px rgba(11,11,11,0.2);
        transition: box-shadow 0.18s ease, border-color 0.18s ease;
    }}
    div[data-testid="stPlotlyChart"]:hover {{
        box-shadow: 0 1px 2px rgba(11,11,11,0.04), 0 18px 32px -14px rgba(11,11,11,0.14);
        border-color: {pal.BASELINE};
    }}

    /* ---- expander (bandeau qualité) ---- */
    div[data-testid="stExpander"] {{
        border-radius: 12px !important;
        border-color: {pal.GRID} !important;
        background: {pal.SURFACE};
        margin-bottom: 1.2rem;
    }}

    /* ---- onglets ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        overflow-x: auto;
        flex-wrap: nowrap;
        border-bottom: 1px solid {pal.GRID};
    }}
    .stTabs [data-baseweb="tab"] {{
        white-space: nowrap;
        font-weight: 600;
        color: {pal.INK_MUTED};
        transition: color 0.15s ease;
    }}
    .stTabs [aria-selected="true"] {{
        color: {pal.CATEGORICAL[0]} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {pal.CATEGORICAL[0]} !important;
        height: 3px;
        border-radius: 3px;
    }}

    /* ---- barre latérale ---- */
    section[data-testid="stSidebar"] {{
        background: {pal.SURFACE};
        border-right: 1px solid {pal.GRID};
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label {{
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.01em;
        color: {pal.INK_SECONDARY};
    }}
    .sidebar-eyebrow {{
        font-family: {pal.FONT_FAMILY};
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {pal.CATEGORICAL[0]};
        margin: 1.1rem 0 0.3rem 0;
    }}
    .sidebar-eyebrow:first-of-type {{ margin-top: 0.2rem; }}

    /* ---- widgets de filtre : dropdowns, tags, radio, slider, date ---- */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        border-radius: 10px !important;
        border-color: {pal.GRID} !important;
        background: {pal.PAGE} !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div {{
        border-color: {pal.CATEGORICAL[0]} !important;
        box-shadow: 0 0 0 3px {pal.CATEGORICAL[0]}22 !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        border-radius: 7px !important;
        box-shadow: 0 1px 2px rgba(11,11,11,0.08);
    }}
    div[data-testid="stDateInputField"] {{
        border-radius: 10px !important;
        border-color: {pal.GRID} !important;
        background: {pal.PAGE} !important;
    }}
    div[data-testid="stSliderTickBar"] {{
        color: {pal.INK_MUTED};
        font-size: 0.72rem;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        box-shadow: 0 2px 6px {pal.CATEGORICAL[0]}55 !important;
    }}
    div[data-testid="stRadioOption"] label {{
        font-weight: 500 !important;
    }}
    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2px;
    }}
    .sidebar-brand-icon {{
        flex: none;
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        border-radius: 10px;
        background: linear-gradient(160deg, {pal.CATEGORICAL[0]}, {pal.CATEGORICAL[6]});
    }}
    .sidebar-brand-name {{
        font-family: {pal.DISPLAY_FONT};
        font-size: 1.15rem;
        font-weight: 600;
        color: {pal.INK_PRIMARY};
    }}

    /* ---- boutons & inputs ---- */
    .stDownloadButton button {{
        border-radius: 8px !important;
        border-color: {pal.CATEGORICAL[0]} !important;
        color: {pal.CATEGORICAL[0]} !important;
        font-weight: 600 !important;
        transition: background 0.15s ease, color 0.15s ease;
    }}
    .stDownloadButton button:hover {{
        background: {pal.CATEGORICAL[0]} !important;
        color: white !important;
    }}

    /* ---- scrollbar ---- */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {pal.PAGE}; }}
    ::-webkit-scrollbar-thumb {{ background: {pal.BASELINE}; border-radius: 6px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {pal.INK_MUTED}; }}

    /* ---- mobile ---- */
    @media (max-width: 640px) {{
        .block-container {{ padding-left: 0.8rem; padding-right: 0.8rem; }}
        .hero-panel {{ padding: 16px; gap: 12px; }}
        .hero-badge {{ width: 42px; height: 42px; font-size: 1.2rem; border-radius: 12px; }}
        .hero-title {{ font-size: 1.35rem; }}
        .hero-sub {{ font-size: 0.82rem; }}
    }}
    </style>
    """

    def inject(self) -> None:
        st.markdown(self.CSS, unsafe_allow_html=True)

    @staticmethod
    def hero(title: str, subtitle: str = "") -> None:
        sub_html = f'<div class="hero-sub">{subtitle}</div>' if subtitle else ""
        st.markdown(
            f'<div class="hero-panel">'
            f'<div class="hero-badge">🧭</div>'
            f'<div><div class="hero-title">{title}</div>{sub_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    @staticmethod
    def sidebar_brand(name: str, caption: str = "") -> None:
        st.sidebar.markdown(
            f'<div class="sidebar-brand">'
            f'<div class="sidebar-brand-icon">🧭</div>'
            f'<div class="sidebar-brand-name">{name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if caption:
            st.sidebar.caption(caption)

    @staticmethod
    def sidebar_section(label: str) -> None:
        """Éveille une hiérarchie dans la pile de filtres — sans ça, la
        sidebar est une liste plate de champs sans structure de lecture."""
        st.sidebar.markdown(f'<div class="sidebar-eyebrow">{label}</div>', unsafe_allow_html=True)
