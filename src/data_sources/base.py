"""Interface commune à toutes les sources de données du tableau de bord.

Toute nouvelle source (Excel aujourd'hui, KoboToolbox demain) implémente
DataSource et renvoie un DataFrame au même schéma brut — le reste de
l'application (dataset, filtres, graphiques) n'a jamais besoin de savoir
d'où viennent les données.
"""
from abc import ABC, abstractmethod

import pandas as pd


class DataSource(ABC):
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Retourne un DataFrame brut, une ligne par besoin exprimé."""
        raise NotImplementedError
