"""Source future : soumissions d'un formulaire KoboToolbox via l'API v2.

Non branchée tant que le formulaire Kobo n'existe pas — prête à l'emploi dès
que KOBO_ASSET_UID et KOBO_API_TOKEN sont disponibles (variables d'env ou
passés au constructeur). field_map traduit les noms de champs Kobo vers le
schéma brut attendu par ConseilMigrantDataset (mêmes noms que les colonnes
Excel actuelles : "Sexe", "Province", "Besoins", "PEC_besoin", ...), pour
que le reste de l'application n'ait aucune adaptation à faire.
"""
from __future__ import annotations

import os

import pandas as pd
import requests

from .base import DataSource


class KoboDataSource(DataSource):
    BASE_URL = "https://kf.kobotoolbox.org/api/v2"

    def __init__(
        self,
        asset_uid: str | None = None,
        api_token: str | None = None,
        field_map: dict[str, str] | None = None,
    ):
        self.asset_uid = asset_uid or os.environ.get("KOBO_ASSET_UID")
        self.api_token = api_token or os.environ.get("KOBO_API_TOKEN")
        self.field_map = field_map or {}

    def load(self) -> pd.DataFrame:
        if not self.asset_uid or not self.api_token:
            raise RuntimeError(
                "KoboDataSource non configuré — définir KOBO_ASSET_UID et "
                "KOBO_API_TOKEN une fois le formulaire Kobo créé et le "
                "field_map renseigné (champs Kobo -> colonnes canoniques)."
            )
        url = f"{self.BASE_URL}/assets/{self.asset_uid}/data.json"
        resp = requests.get(
            url,
            headers={"Authorization": f"Token {self.api_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        df = pd.DataFrame(resp.json().get("results", []))
        if self.field_map:
            df = df.rename(columns=self.field_map)
        return df
