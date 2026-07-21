from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.charts import ChartBuilder
from src.data_sources.excel_source import ExcelDataSource
from src.dataset import ConseilMigrantDataset
from src.filters import Filters
from src.ui import Theme

st.set_page_config(page_title="Conseil Migrant — Tableau de bord", layout="wide", page_icon="🧭")

theme = Theme()
theme.inject()

DATA_PATH = Path(__file__).parent / "data" / "sample" / "basemigrant_sample.xlsx"

# Version du schéma de données : à incrémenter dès que _normalize / les
# colonnes dérivées / les méthodes du dataset changent. Passée comme argument
# haché à la fonction cachée, elle force Streamlit à reconstruire l'objet au
# lieu de resservir une instance construite par l'ancien code après un
# redéploiement (sinon : AttributeError / KeyError sur les nouveaux champs).
DATA_SCHEMA_VERSION = 2


@st.cache_resource(show_spinner="Chargement des données…")
def load_dataset(path: str, schema_version: int) -> ConseilMigrantDataset:
    return ConseilMigrantDataset(ExcelDataSource(path)).load()


dataset = load_dataset(str(DATA_PATH), DATA_SCHEMA_VERSION)
df = dataset.df

st.sidebar.markdown("## 🧭 Conseil Migrant")
st.sidebar.caption("Tableau de bord opérationnel")
st.sidebar.divider()

min_date, max_date = df["date_besoin"].min(), df["date_besoin"].max()
date_range = st.sidebar.date_input(
    "Période", value=(min_date.date(), max_date.date()),
    min_value=min_date.date(), max_value=max_date.date(),
)
sexes = st.sidebar.multiselect(
    "Genre", options=["M", "F"], default=["M", "F"],
    format_func=lambda x: "Masculin" if x == "M" else "Féminin",
)
provinces = st.sidebar.multiselect("Province", options=sorted(df["province"].unique()))
besoins = st.sidebar.multiselect("Type de besoin", options=sorted(df["besoin"].unique()))
pec = st.sidebar.radio("Prise en charge", options=["Toutes", "Oui", "Non"], horizontal=True)
statuts = st.sidebar.multiselect("Statut migratoire", options=sorted(df["statut_migratoire"].unique()))
pays = st.sidebar.multiselect("Pays d'origine", options=sorted(df["pays_origine"].unique()))
enf_min, enf_max = int(df["nombre_enfants"].min()), int(df["nombre_enfants"].max())
nb_enfants = st.sidebar.slider("Nombre d'enfants", enf_min, enf_max, (enf_min, enf_max))

st.sidebar.divider()
st.sidebar.caption(f"Données : {min_date.date()} – {max_date.date()}")
st.sidebar.caption(f"{len(df)} enregistrements")

filters = Filters(
    date_debut=date_range[0] if len(date_range) == 2 else None,
    date_fin=date_range[1] if len(date_range) == 2 else None,
    sexes=sexes,
    provinces=provinces,
    besoins=besoins,
    statuts=statuts,
    pays_origine=pays,
    pec=pec,
    nb_enfants_min=nb_enfants[0],
    nb_enfants_max=nb_enfants[1],
)
dff = dataset.filtered(filters)
kpi = dataset.kpi(dff)
kpi_all = dataset.kpi(df)
quality = dataset.quality(df)
is_filtered = len(dff) != len(df)
charts = ChartBuilder()

theme.hero("Conseil Migrant — Tableau de bord opérationnel",
           "Suivi des besoins exprimés, taux de prise en charge et couverture par profil, province et statut migratoire.")

# Bandeau qualité de données : signale les incohérences plutôt que de les
# ignorer silencieusement. Replié par défaut pour ne pas surcharger la vue.
if quality:
    with st.expander(f"⚠️ Qualité des données — {len(quality)} contrôle(s) à vérifier", expanded=False):
        st.caption(
            "Ces lignes restent comptées dans les totaux mais peuvent fausser "
            "certaines lectures (notamment l'ancienneté). À corriger à la source."
        )
        for libelle, n in quality.items():
            pct = n / len(df) * 100
            st.markdown(f"- **{n}** ligne(s) — {libelle} *(≈ {pct:.1f} % du total)*")

# Tendance mensuelle du volume filtré, pour la sparkline de "Besoins reçus".
spark = dff.groupby("periode").size().sort_index()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Besoins reçus", f"{kpi['total']:,}".replace(",", " "),
    chart_data=spark if len(spark) > 1 else None, chart_type="area", border=True,
)
c2.metric("Besoins pris en charge", f"{kpi['pris_en_charge']:,}".replace(",", " "), border=True)
c3.metric(
    "Taux de prise en charge", f"{kpi['taux']}%",
    # Le delta n'a de sens que comparé à une référence : on ne l'affiche que
    # quand un filtre est actif (écart du segment filtré vs l'ensemble).
    delta=f"{kpi['taux'] - kpi_all['taux']:+.1f} pt" if is_filtered else None,
    delta_color="normal",
    delta_description="vs ensemble" if is_filtered else None, border=True,
)
c4.metric("Non pris en charge", f"{kpi['non_pris_en_charge']:,}".replace(",", " "), border=True)

tab1, tab2, tab3, tab4 = st.tabs(["Vue d'ensemble", "Profils", "Géographie", "Données"])

with tab1:
    # La synthèse pilotage en tête : la première chose à voir est où la prise
    # en charge décroche, pas la répartition brute.
    st.plotly_chart(charts.sous_couverture(dff, kpi["taux"]), use_container_width=True,
                    config={"displayModeBar": False})
    col1, col2 = st.columns([3, 2])
    col1.plotly_chart(charts.evolution_annuelle(dff), use_container_width=True, config={"displayModeBar": False})
    col2.plotly_chart(charts.repartition_besoins(dff), use_container_width=True, config={"displayModeBar": False})

with tab2:
    col1, col2 = st.columns([2, 3])
    col1.plotly_chart(charts.par_genre(dff), use_container_width=True, config={"displayModeBar": False})
    col2.plotly_chart(charts.statut_migratoire(dff), use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(charts.taux_genre_besoin(dff), use_container_width=True, config={"displayModeBar": False})
    col3, col4 = st.columns([1, 1])
    col3.plotly_chart(charts.prise_en_charge_anciennete(dff), use_container_width=True, config={"displayModeBar": False})
    col4.plotly_chart(charts.par_nombre_enfants(dff), use_container_width=True, config={"displayModeBar": False})
    col5, col6 = st.columns([3, 2])
    col5.plotly_chart(charts.par_pays_origine(dff), use_container_width=True, config={"displayModeBar": False})
    col6.plotly_chart(charts.par_statut_migratoire_donut(dff), use_container_width=True, config={"displayModeBar": False})

with tab3:
    col1, col2 = st.columns([1, 1])
    col1.plotly_chart(charts.par_province(dff), use_container_width=True, config={"displayModeBar": False})
    col2.plotly_chart(charts.taux_province(dff), use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(charts.evolution_mensuelle(dff), use_container_width=True, config={"displayModeBar": False})

with tab4:
    st.subheader("Cas non traités — suivi individuel")
    st.caption(
        "Filtrez sur « Prise en charge = Non » (colonne, ou filtre en tête de "
        "colonne) pour lister les ID à retrouver dans le fichier d'identité local "
        "de l'équipe (Nom, Date de naissance) — ce tableau de bord ne contient "
        "jamais d'information nominative."
    )
    show_cols = [
        "id", "genre", "province", "pays_origine", "statut_migratoire",
        "nombre_enfants", "besoin", "pec_besoin", "date_besoin",
    ]
    table = dff[[c for c in show_cols if c in dff.columns]].sort_values("date_besoin", ascending=False)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇ Exporter en CSV", table.to_csv(index=False).encode("utf-8"),
        file_name="conseil_migrant_filtre.csv", mime="text/csv",
    )
