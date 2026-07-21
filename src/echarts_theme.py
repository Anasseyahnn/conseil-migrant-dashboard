"""Rendu ECharts via st.components.v1.html — pas de wrapper tiers
(streamlit-echarts est incompatible avec l'API composants v2 de Streamlit
1.59, testé et abandonné). ECharts est chargé depuis un CDN dans l'iframe
du composant, ce qui est sans risque ici (contrairement à un Artifact
Claude, une app Streamlit déployée n'a pas de CSP bloquant les requêtes
sortantes)."""
from __future__ import annotations

import json

from . import palette as pal

CDN = "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"

_DIV_RED = (220, 112, 112)   # #dc7070
_DIV_MID = (240, 239, 238)   # #f0efec
_DIV_BLUE = (68, 136, 219)   # #4488db


def diverging_color(t: float) -> str:
    """Même interpolation que pal.DIVERGING utilisée côté Plotly : rouge à 0,
    gris à 50, bleu à 100."""
    if t <= 50:
        a, b, f = _DIV_RED, _DIV_MID, t / 50
    else:
        a, b, f = _DIV_MID, _DIV_BLUE, (t - 50) / 50
    c = tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3))
    return f"rgb({c[0]},{c[1]},{c[2]})"


def label_color(t: float) -> str:
    """Encre foncée sur fond pâle (milieu de l'échelle divergente), blanc sur
    fond saturé — même règle que _inside_label_colors côté Plotly."""
    return pal.INK_PRIMARY if 35 <= t <= 65 else "#ffffff"


def base_option(title: str, subtitle: str = "") -> dict:
    """Titre/sous-titre/police/couleurs communs à tous les graphiques —
    équivalent ECharts de ChartBuilder._base_layout côté Plotly."""
    return {
        "title": {
            "text": title,
            "subtext": subtitle,
            "left": 0,
            "top": 0,
            "textStyle": {"fontSize": 15, "fontWeight": 700, "color": pal.INK_PRIMARY,
                          "fontFamily": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
            "subtextStyle": {"fontSize": 12, "color": pal.INK_MUTED,
                              "fontFamily": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
        },
        "backgroundColor": pal.SURFACE,
        "textStyle": {"fontFamily": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
        "tooltip": {
            "trigger": "axis", "axisPointer": {"type": "shadow"},
            "backgroundColor": pal.SURFACE, "borderColor": pal.BASELINE,
            "textStyle": {"color": pal.INK_PRIMARY, "fontSize": 12},
        },
    }


def axis_style() -> dict:
    return {
        "axisLabel": {"color": pal.INK_MUTED, "fontSize": 11},
        "axisLine": {"lineStyle": {"color": pal.BASELINE}},
        "splitLine": {"lineStyle": {"color": pal.GRID}},
    }


def render(option: dict, height: int = 420, dom_id: str = "c") -> str:
    """Emballe un dict d'options ECharts en HTML autonome pour
    st.components.v1.html — un seul point d'assemblage pour tous les
    graphiques, pour garder le même comportement partout (resize, thème)."""
    opt_json = json.dumps(option, ensure_ascii=False)
    return f"""
<div id="{dom_id}" style="width:100%;height:{height}px;"></div>
<script src="{CDN}"></script>
<script>
(function() {{
  var el = document.getElementById("{dom_id}");
  var chart = echarts.init(el);
  chart.setOption({opt_json});
  new ResizeObserver(function() {{ chart.resize(); }}).observe(el);
}})();
</script>
"""
