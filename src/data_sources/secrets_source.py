"""Source de données réelles via les secrets Streamlit Cloud.

Le fichier basemigrant.xlsx réel (PII d'une population vulnérable) n'est
JAMAIS committé sur GitHub (.gitignore). Pour l'app hébergée sur Streamlit
Community Cloud, il est stocké encodé en base64 dans les secrets de l'app
(configuration privée côté Streamlit Cloud, jamais dans le repo) — voir
`data_sources/base.py` pour l'interface commune.
"""
from __future__ import annotations

import base64
import io

import pandas as pd

from .base import DataSource


class SecretsExcelDataSource(DataSource):
    """Charge le classeur réel depuis une chaîne base64 (secret Streamlit)."""

    def __init__(self, b64_content: str, sheet_name: str = "Feuil2"):
        self.b64_content = b64_content
        self.sheet_name = sheet_name

    def load(self) -> pd.DataFrame:
        raw = base64.b64decode(self.b64_content)
        return pd.read_excel(io.BytesIO(raw), sheet_name=self.sheet_name)
