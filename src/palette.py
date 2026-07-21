"""Palette validée (skill dataviz interne) — chaque couleur a un rôle fixe,
jamais choisie à l'œil. Voir `references/palette.md` du skill pour la
méthode complète ; ces valeurs sont l'instance de référence (mode clair).

Streamlit ne permet pas un thème clair/sombre entièrement custom au même
niveau qu'une page HTML — seul le thème clair est câblé ici en dur (via
.streamlit/config.toml) ; le mode sombre du sélecteur Streamlit reste géré
par son moteur de thème natif.
"""
from __future__ import annotations

# Catégoriel — 8 teintes, ORDRE FIXE, jamais recyclé/réordonné par rang.
CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#008300",  # 2 green
    "#e87ba4",  # 3 magenta
    "#eda100",  # 4 yellow
    "#1baf7a",  # 5 aqua
    "#eb6834",  # 6 orange
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]
MUTED = "#898781"  # "Autres" / agrégat — jamais un slot numéroté

# Statut — état (satisfait / non satisfait), jamais recyclé pour une série.
STATUS = {
    "good": "#0ca30c",
    "critical": "#d03b3b",
}

# Diverging — polarité (taux de satisfaction), pôles + neutre gris médian.
DIVERGING = ["#e34948", "#f0efec", "#2a78d6"]  # rouge -> gris -> bleu

# Séquentiel — magnitude, une seule teinte bleu, clair -> foncé.
SEQUENTIAL = ["#cde2fb", "#86b6ef", "#3987e5", "#2a78d6", "#1c5cab", "#0d366b"]

# Chrome & encre (mode clair).
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', sans-serif"
