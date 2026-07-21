from __future__ import annotations

import pandas as pd

from .data_sources.base import DataSource
from .filters import Filters

# Colonnes brutes (Excel aujourd'hui, champs Kobo mappés demain) -> schéma canonique.
RAW_TO_CANONICAL = {
    "ID": "id",
    "Sexe": "sexe",
    "Province": "province",
    "Pays_d'origine": "pays_origine",
    "Statut_migratoire": "statut_migratoire",
    "Nombre_enfant": "nombre_enfants",
    "Arrivée": "date_arrivee",
    "Date_besoin": "date_besoin",
    "annee_besoin": "annee_besoin",
    "mois_besoins": "mois_besoins",
    "Besoins": "besoin",
    "PEC_besoin": "pec_besoin",
}


class ConseilMigrantDataset:
    """Encapsule le nettoyage, la normalisation et les indicateurs calculés
    d'un jeu de besoins Conseil Migrant, quelle que soit la source
    (Excel aujourd'hui, Kobo demain) — c'est le seul endroit qui connaît le
    mapping brut -> canonique."""

    def __init__(self, source: DataSource):
        self._source = source
        self._df: pd.DataFrame | None = None

    def load(self) -> "ConseilMigrantDataset":
        self._df = self._normalize(self._source.load())
        return self

    @staticmethod
    def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.rename(columns={k: v for k, v in RAW_TO_CANONICAL.items() if k in raw.columns})
        keep = [c for c in RAW_TO_CANONICAL.values() if c in df.columns]
        df = df[keep].copy()

        for col in ("sexe", "statut_migratoire", "pec_besoin", "besoin", "province", "pays_origine"):
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        if "annee_besoin" in df.columns:
            df["annee_besoin"] = pd.to_numeric(df["annee_besoin"], errors="coerce").astype("Int64")
        if "mois_besoins" in df.columns:
            df["mois_besoins"] = pd.to_numeric(df["mois_besoins"], errors="coerce").astype("Int64")
        if "nombre_enfants" in df.columns:
            df["nombre_enfants"] = pd.to_numeric(df["nombre_enfants"], errors="coerce").astype("Int64")
        df["date_besoin"] = pd.to_datetime(df.get("date_besoin"), errors="coerce")
        if "date_arrivee" in df.columns:
            df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], errors="coerce")

        df["genre"] = df["sexe"].map({"M": "Masculin", "F": "Féminin"}).fillna(df["sexe"])
        # PEC_besoin = Prise En Charge du besoin (Oui/Non) : c'est une mesure
        # opérationnelle (le besoin a-t-il été traité), pas une satisfaction
        # subjective — d'où le nom pris_en_charge, pas "satisfait".
        df["pris_en_charge"] = df["pec_besoin"] == "Oui"
        df["periode"] = df["date_besoin"].dt.to_period("M").astype(str)

        # Ancienneté d'installation au moment du besoin (en années). Peut être
        # négative si la date d'arrivée est postérieure au besoin (incohérence
        # de saisie) — laissé tel quel ici, signalé par quality() et exclu des
        # graphiques par tranche.
        if "date_arrivee" in df.columns:
            df["anciennete_ans"] = (df["date_besoin"] - df["date_arrivee"]).dt.days / 365.25

        return df.dropna(subset=["id"]) if "id" in df.columns else df

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            raise RuntimeError("Appeler .load() avant d'accéder aux données.")
        return self._df

    def filtered(self, filters: Filters) -> pd.DataFrame:
        return filters.apply(self.df)

    @staticmethod
    def kpi(df: pd.DataFrame) -> dict:
        total = len(df)
        pris_en_charge = int(df["pris_en_charge"].sum()) if total else 0
        taux = round(pris_en_charge / total * 100, 1) if total else 0.0
        return {
            "total": total,
            "pris_en_charge": pris_en_charge,
            "non_pris_en_charge": total - pris_en_charge,
            "taux": taux,
        }

    @staticmethod
    def quality(df: pd.DataFrame) -> dict:
        """Contrôles de cohérence remontés à l'utilisateur plutôt qu'ignorés
        silencieusement. Chaque entrée : (libellé, nombre de lignes concernées)."""
        checks: dict[str, int] = {}
        if "anciennete_ans" in df.columns:
            checks["arrivée postérieure au besoin"] = int((df["anciennete_ans"] < 0).sum())
            checks["date d'arrivée manquante"] = int(df["date_arrivee"].isna().sum())
        checks["date de besoin manquante"] = int(df["date_besoin"].isna().sum())
        for col in ("statut_migratoire", "province", "pays_origine"):
            if col in df.columns:
                manquants = int((df[col].isna() | (df[col].astype(str).str.strip() == "")).sum())
                if manquants:
                    checks[f"{col.replace('_', ' ')} manquant"] = manquants
        return {k: v for k, v in checks.items() if v > 0}
