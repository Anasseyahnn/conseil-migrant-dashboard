from __future__ import annotations

import pandas as pd
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode, JsCode

from . import palette as pal

COLUMN_LABELS = {
    "id": "ID",
    "genre": "Genre",
    "province": "Province",
    "pays_origine": "Pays d'origine",
    "statut_migratoire": "Statut migratoire",
    "nombre_enfants": "Enfants",
    "besoin": "Besoin",
    "pec_besoin": "Prise en charge",
    "date_besoin": "Date du besoin",
}

_PEC_CELL_STYLE = JsCode(
    f"""
    function(params) {{
        if (params.value === 'Oui') {{
            return {{'backgroundColor': '#e6f7e6', 'color': '{pal.STATUS["good"]}', 'fontWeight': '600'}};
        }}
        if (params.value === 'Non') {{
            return {{'backgroundColor': '#fbe9e9', 'color': '{pal.STATUS["critical"]}', 'fontWeight': '600'}};
        }}
        return {{}};
    }}
    """
)


class DataGrid:
    """Grille interactive (streamlit-aggrid) pour l'onglet Données — tri,
    filtre par colonne, recherche, redimensionnement, export ; bien plus
    riche qu'un st.dataframe brut pour retrouver un cas précis."""

    @staticmethod
    def render(df: pd.DataFrame, height: int = 460):
        d = df.rename(columns=COLUMN_LABELS)
        if "Date du besoin" in d.columns:
            d["Date du besoin"] = pd.to_datetime(d["Date du besoin"]).dt.strftime("%Y-%m-%d")

        gb = GridOptionsBuilder.from_dataframe(d)
        gb.configure_default_column(filterable=True, sortable=True, resizable=True, floatingFilter=True)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        if "Prise en charge" in d.columns:
            gb.configure_column("Prise en charge", cellStyle=_PEC_CELL_STYLE)
        if "ID" in d.columns:
            gb.configure_column("ID", pinned="left", width=90)
        grid_options = gb.build()

        return AgGrid(
            d,
            gridOptions=grid_options,
            height=height,
            theme="alpine",
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=True,
        )
