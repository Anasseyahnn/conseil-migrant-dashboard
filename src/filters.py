from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import pandas as pd

# Colonne calendaire dérivée (voir dataset._normalize) correspondant à chaque
# granularité proposée dans le filtre de période.
GRANULARITE_COLONNES = {
    "Année": "annee_calendaire",
    "Semestre": "semestre_calendaire",
    "Trimestre": "trimestre_calendaire",
    "Mois": "periode",
}


@dataclass
class Filters:
    """État des filtres sélectionnés dans la barre latérale — indépendant
    de Streamlit pour rester testable."""

    date_debut: dt.date | None = None
    date_fin: dt.date | None = None
    periode_granularite: str = "Aucune"                       # "Aucune"|"Année"|"Semestre"|"Trimestre"|"Mois"
    periode_valeurs: list[str] = field(default_factory=list)
    sexes: list[str] = field(default_factory=lambda: ["M", "F"])
    provinces: list[str] = field(default_factory=list)      # vide = toutes
    besoins: list[str] = field(default_factory=list)
    statuts: list[str] = field(default_factory=list)
    pays_origine: list[str] = field(default_factory=list)
    pec: str = "Toutes"                                      # "Toutes" | "Oui" | "Non"
    nb_enfants_min: int | None = None
    nb_enfants_max: int | None = None

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        d = df
        if self.date_debut is not None:
            d = d[d["date_besoin"] >= pd.Timestamp(self.date_debut)]
        if self.date_fin is not None:
            d = d[d["date_besoin"] <= pd.Timestamp(self.date_fin)]
        col = GRANULARITE_COLONNES.get(self.periode_granularite)
        if col and self.periode_valeurs:
            d = d[d[col].isin(self.periode_valeurs)]
        if self.sexes:
            d = d[d["sexe"].isin(self.sexes)]
        if self.provinces:
            d = d[d["province"].isin(self.provinces)]
        if self.besoins:
            d = d[d["besoin"].isin(self.besoins)]
        if self.statuts:
            d = d[d["statut_migratoire"].isin(self.statuts)]
        if self.pays_origine:
            d = d[d["pays_origine"].isin(self.pays_origine)]
        if self.pec in ("Oui", "Non"):
            d = d[d["pec_besoin"] == self.pec]
        if self.nb_enfants_min is not None:
            d = d[d["nombre_enfants"] >= self.nb_enfants_min]
        if self.nb_enfants_max is not None:
            d = d[d["nombre_enfants"] <= self.nb_enfants_max]
        return d
