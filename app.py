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


@st.cache_resource(show_spinner="Chargement des données…")
def load_dataset(path: str) -> ConseilMigrantDataset:
    return ConseilMigrantDataset(ExcelDataSource(path)).load()


dataset = load_dataset(str(DATA_PATH))
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
charts = ChartBuilder()

theme.hero("Conseil Migrant — Tableau de bord opérationnel",
           "Suivi des besoins exprimés, taux de satisfaction et couverture par profil, province et statut migratoire.")

# Tendance mensuelle du volume filtré, pour la sparkline de "Besoins reçus".
spark = dff.groupby("periode").size().sort_index()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Besoins reçus", f"{kpi['total']:,}".replace(",", " "),
    chart_data=spark if len(spark) > 1 else None, chart_type="area", border=True,
)
c2.metric("Besoins satisfaits", f"{kpi['satisfaits']:,}".replace(",", " "), border=True)
c3.metric(
    "Taux de satisfaction", f"{kpi['taux']}%",
    delta=f"{kpi['taux'] - kpi_all['taux']:+.1f} pt", delta_color="normal",
    delta_description="vs global", border=True,
)
c4.metric("Non satisfaits", f"{kpi['non_satisfaits']:,}".replace(",", " "), border=True)

tab1, tab2, tab3, tab4 = st.tabs(["Vue d'ensemble", "Genre & Statut", "Géographie", "Données"])

with tab1:
    col1, col2 = st.columns([3, 2])
    col1.plotly_chart(charts.evolution_annuelle(dff), use_container_width=True, config={"displayModeBar": False})
    col2.plotly_chart(charts.repartition_besoins(dff), use_container_width=True, config={"displayModeBar": False})

with tab2:
    col1, col2 = st.columns([2, 3])
    col1.plotly_chart(charts.par_genre(dff), use_container_width=True, config={"displayModeBar": False})
    col2.plotly_chart(charts.statut_migratoire(dff), use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(charts.taux_genre_besoin(dff), use_container_width=True, config={"displayModeBar": False})
    col3, col4 = st.columns([3, 2])
    col3.plotly_chart(charts.par_pays_origine(dff), use_container_width=True, config={"displayModeBar": False})
    col4.plotly_chart(charts.par_statut_migratoire_donut(dff), use_container_width=True, config={"displayModeBar": False})

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
