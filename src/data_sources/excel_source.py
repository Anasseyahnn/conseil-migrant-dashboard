from pathlib import Path

import pandas as pd

from .base import DataSource


class ExcelDataSource(DataSource):
    """Source actuelle : fichier basemigrant.xlsx, feuille Feuil2."""

    def __init__(self, path: str | Path, sheet_name: str = "Feuil2"):
        self.path = Path(path)
        self.sheet_name = sheet_name

    def load(self) -> pd.DataFrame:
        return pd.read_excel(self.path, sheet_name=self.sheet_name)
