# Conseil Migrant — Tableau de bord

Tableau de bord opérationnel de suivi des besoins exprimés par les bénéficiaires de Conseil Migrant : volume, taux de satisfaction, répartition par genre/province/statut migratoire, évolution temporelle.

Implémentation **Streamlit** (Python), pensée pour un hébergement simple et gratuit sur Streamlit Community Cloud. La logique reprend et fusionne le meilleur de deux versions R/flexdashboard existantes (historique interne, non versionnées ici), avec des filtres avancés et une nouvelle donnée source.

## Données et confidentialité

Les données réelles (`ID`, `Sexe`, `Province`, `Statut_migratoire`, `Besoins`, `PEC_besoin`, dates) concernent une population vulnérable. **Aucune donnée nominative (`Nom`, `Date_de_naissance`) n'est versionnée dans ce repo ni chargée dans les applications hébergées.**

- `data/sample/` contient un jeu de données **synthétique** (mêmes colonnes, valeurs fictives) pour le développement et la démo.
- Le fichier réel reste local, hors git (voir `.gitignore`).
- Pour retrouver l'identité d'un bénéficiaire à partir d'un `ID` filtré dans le tableau de bord (ex. cas non traités), l'équipe Conseil Migrant utilise son propre fichier `ID → Nom → Date_de_naissance`, conservé séparément et jamais partagé avec ce repo ou les apps hébergées.

## Statut

Repo privé — travail en cours.


Pour la generation de graphique toujour se referer au lien : https://echarts.apache.org/examples/en/index.html#chart-type-matrix
