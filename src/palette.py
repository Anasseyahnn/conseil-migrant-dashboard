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
# Version adoucie (21/07) : intensité réduite pour le confort visuel, mais
# revalidée par scripts/validate_palette.js (skill dataviz) avant adoption —
# ALL CHECKS PASS (bande de clarté, plancher de chroma, séparation daltonisme
# ΔE 8.7 deutan, contraste — 4 slots en WARN contraste, légal car chaque
# graphique utilisant ces teintes porte déjà un encodage secondaire : label
# de valeur direct sur chaque marque + légende).
CATEGORICAL = [
    "#4488db",  # 1 blue
    "#1f921f",  # 2 green
    "#eb8baf",  # 3 magenta
    "#eda100",  # 4 yellow (non modifié — déjà en haut de bande, adoucir le sortait de la plage)
    "#36b98a",  # 5 aqua
    "#ed7a4c",  # 6 orange
    "#6052b2",  # 7 violet
    "#e65f5e",  # 8 red
]
MUTED = "#898781"  # "Autres" / agrégat — jamais un slot numéroté

# Statut — état (satisfait / non satisfait), jamais recyclé pour une série.
# Adouci (21/07), revalidé : vert/rouge ΔE 8.7 deutan (>= cible 8), contraste
# >= 3:1 pour les deux — PASS sans réserve.
STATUS = {
    "good": "#219b21",
    "critical": "#dc7070",
}

# Diverging — polarité (taux de satisfaction), pôles + neutre gris médian.
DIVERGING = ["#dc7070", "#f0efec", "#4488db"]  # rouge -> gris -> bleu (adoucis)

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
