from __future__ import annotations

import streamlit as st

from . import palette as pal

ACCENT_HEX = {
    "kpi-accent": pal.CATEGORICAL[0],
    "kpi-good": pal.STATUS["good"],
    "kpi-critical": pal.STATUS["critical"],
}


class Theme:
    """Injecte le CSS responsive (mobile / tablette / desktop) et fournit les
    composants d'habillage (tuiles KPI) alignés sur la palette du skill
    dataviz — un seul endroit à toucher pour changer l'apparence globale."""

    CSS = f"""
    <style>
    html, body, [class*="css"] {{
        font-family: {pal.FONT_FAMILY};
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    /* ---- bande d'accroche en tête de page ---- */
    .hero-band {{
        height: 4px;
        border-radius: 4px;
        margin-bottom: 1.1rem;
        background: linear-gradient(90deg,
            {pal.CATEGORICAL[0]} 0%, {pal.CATEGORICAL[4]} 50%, {pal.CATEGORICAL[6]} 100%);
    }}
    h1 {{
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        color: {pal.INK_PRIMARY} !important;
        letter-spacing: -0.01em;
        margin-bottom: 0.1rem !important;
    }}
    .hero-sub {{
        color: {pal.INK_MUTED};
        font-size: 0.92rem;
        margin-bottom: 1.1rem;
    }}

    /* ---- tuiles KPI : grille adaptative, pas des colonnes Streamlit ---- */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 0.4rem 0 1.6rem 0;
    }}
    .kpi-tile {{
        position: relative;
        background: {pal.SURFACE};
        border: 1px solid {pal.GRID};
        border-radius: 12px;
        padding: 16px 18px 14px 18px;
        box-shadow: 0 1px 2px rgba(11,11,11,0.05);
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
        overflow: hidden;
    }}
    .kpi-tile::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent);
        opacity: 0.85;
    }}
    .kpi-tile:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(11,11,11,0.09);
        border-color: var(--accent);
    }}
    .kpi-top {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }}
    .kpi-label {{
        font-size: 0.78rem;
        color: {pal.INK_MUTED};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .kpi-icon {{
        font-size: 1.05rem;
        opacity: 0.9;
    }}
    .kpi-value {{
        font-size: 1.7rem;
        font-weight: 700;
        color: {pal.INK_PRIMARY};
        line-height: 1.15;
        font-variant-numeric: proportional-nums;
    }}
    .kpi-accent {{ --accent: {pal.CATEGORICAL[0]}; }}
    .kpi-good {{ --accent: {pal.STATUS['good']}; }}
    .kpi-critical {{ --accent: {pal.STATUS['critical']}; }}

    /* ---- cartes graphiques ---- */
    div[data-testid="stPlotlyChart"] {{
        background: {pal.SURFACE};
        border: 1px solid {pal.GRID};
        border-radius: 12px;
        padding: 8px 6px 2px 6px;
        box-shadow: 0 1px 2px rgba(11,11,11,0.05);
        transition: box-shadow 0.18s ease, border-color 0.18s ease;
    }}
    div[data-testid="stPlotlyChart"]:hover {{
        box-shadow: 0 10px 24px rgba(11,11,11,0.10);
        border-color: {pal.BASELINE};
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
        color: {pal.INK_SECONDARY};
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

    /* ---- tablette ---- */
    @media (max-width: 1024px) {{
        .kpi-grid {{ grid-template-columns: repeat(4, 1fr); gap: 10px; }}
        .kpi-value {{ font-size: 1.45rem; }}
    }}

    /* ---- mobile ---- */
    @media (max-width: 640px) {{
        .block-container {{ padding-left: 0.8rem; padding-right: 0.8rem; }}
        h1 {{ font-size: 1.3rem !important; }}
        .hero-sub {{ font-size: 0.82rem; }}
        .kpi-grid {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
        .kpi-tile {{ padding: 12px 14px 10px 14px; }}
        .kpi-value {{ font-size: 1.3rem; }}
        .kpi-label {{ font-size: 0.68rem; }}
    }}
    </style>
    """

    def inject(self) -> None:
        st.markdown(self.CSS, unsafe_allow_html=True)

    @staticmethod
    def hero(title: str, subtitle: str = "") -> None:
        st.markdown('<div class="hero-band"></div>', unsafe_allow_html=True)
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f'<div class="hero-sub">{subtitle}</div>', unsafe_allow_html=True)

    @staticmethod
    def kpi_grid(tiles: list[tuple[str, str, str, str]]) -> None:
        """tiles: liste de (label, valeur formatée, classe de couleur, icône)."""
        cells = "".join(
            f'<div class="kpi-tile {css_class}">'
            f'<div class="kpi-top"><span class="kpi-label">{label}</span>'
            f'<span class="kpi-icon">{icon}</span></div>'
            f'<div class="kpi-value">{value}</div></div>'
            for label, value, css_class, icon in tiles
        )
        st.markdown(f'<div class="kpi-grid">{cells}</div>', unsafe_allow_html=True)
