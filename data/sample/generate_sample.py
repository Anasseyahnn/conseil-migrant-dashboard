"""Génère un jeu de données synthétique (data/sample/basemigrant_sample.xlsx)
avec les mêmes colonnes et distributions plausibles que les données réelles,
mais sans aucune information nominative — sûr à versionner.

Usage : python data/sample/generate_sample.py
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

N = 420

PROVINCES = [
    "Alberta", "Colombie-Britannique", "Manitoba", "Nouveau-Brunswick",
    "Nouvelle-Écosse", "Ontario", "Île-du-Prince-Édouard", "Québec",
    "Saskatchewan", "Terre-Neuve-et-Labrador",
]
PAYS_ORIGINE = [
    "Belgique", "Burkina_Faso", "Cambodge", "Chili", "Ethiopie", "France",
    "Guatemala", "Haiti", "Nicaragua", "Nigeria", "Mozambique", "Soudan",
    "Suisse", "Togo", "Venezuela",
]
STATUTS = [
    "Travailleur temporaire", "Demandeur d'asile", "Visiteur", "Touriste",
    "Étudiant(e)", "Résident(e)", "Autre",
]
BESOINS = ["Aide financière", "Aide alimentaire", "Assistance juridique", "Santé", "Aide au logement"]

PRENOMS = [f"Bénéficiaire_{i:04d}" for i in range(1, N + 1)]  # placeholder, pas un vrai prénom


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def main() -> None:
    rows = []
    for i in range(1, N + 1):
        date_besoin = random_date(date(2024, 1, 1), date(2026, 8, 28))
        rows.append(
            {
                "ID": i,
                "Sexe": random.choice(["M", "F"]),
                "Province": random.choice(PROVINCES),
                "Pays_d'origine": random.choice(PAYS_ORIGINE),
                "Statut_migratoire": random.choice(STATUTS),
                "Nombre_enfant": random.choices([0, 1, 2, 3], weights=[155, 104, 97, 66])[0],
                "Arrivée": random_date(date(2015, 1, 1), date(2026, 3, 24)),
                "Date_besoin": date_besoin,
                "annee_besoin": date_besoin.year,
                "mois_besoins": date_besoin.month,
                "Besoins": random.choice(BESOINS),
                "PEC_besoin": random.choices(["Oui", "Non"], weights=[267, 155])[0],
            }
        )

    df = pd.DataFrame(rows)
    out = Path(__file__).parent / "basemigrant_sample.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Feuil2", index=False)
    print(f"Écrit : {out} ({len(df)} lignes)")


if __name__ == "__main__":
    main()
