from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import palette as pal

STATUT_LABEL = {True: "Satisfait", False: "Non satisfait"}
STATUT_COLOR = {"Satisfait": pal.STATUS["good"], "Non satisfait": pal.STATUS["critical"]}
PEC_COLOR = {"Oui": pal.STATUS["good"], "Non": pal.STATUS["critical"]}


class ChartBuilder:
    """Un thème visuel cohérent (skill dataviz) appliqué à tous les
    graphiques : couleur assignée par rôle (catégoriel / statut / diverging),
    traits fins, légende conditionnelle, hover soigné, grilles récessives."""

    def _base_layout(self, fig: go.Figure, title: str, subtitle: str = "", show_legend: bool | None = None) -> go.Figure:
        full_title = f"<b>{title}</b>"
        if subtitle:
            full_title += f"<br><span style='font-size:12px;color:{pal.INK_MUTED}'>{subtitle}</span>"
        fig.update_layout(
            title=dict(text=full_title, x=0, xanchor="left", y=0.97, yanchor="top", pad=dict(b=8)),
            paper_bgcolor=pal.SURFACE,
            plot_bgcolor=pal.SURFACE,
            font=dict(family=pal.FONT_FAMILY, color=pal.INK_SECONDARY, size=12),
            legend=dict(
                orientation="h", y=1.24, yanchor="bottom", x=1, xanchor="right",
                font=dict(size=11, color=pal.INK_SECONDARY),
                title=None,
            ) if show_legend is not False else dict(visible=False),
            showlegend=show_legend if show_legend is not None else True,
            margin=dict(t=84, b=36, l=8, r=8),
            hoverlabel=dict(
                bgcolor=pal.SURFACE, bordercolor=pal.BASELINE,
                font=dict(family=pal.FONT_FAMILY, color=pal.INK_PRIMARY, size=12),
            ),
            hovermode="closest",
        )
        fig.update_xaxes(
            gridcolor=pal.GRID, gridwidth=1, griddash="solid",
            linecolor=pal.BASELINE, zeroline=False,
            tickfont=dict(color=pal.INK_MUTED, size=11),
            title_font=dict(color=pal.INK_MUTED, size=11),
        )
        fig.update_yaxes(
            gridcolor=pal.GRID, gridwidth=1, griddash="solid",
            linecolor=pal.BASELINE, zeroline=False,
            tickfont=dict(color=pal.INK_MUTED, size=11),
            title_font=dict(color=pal.INK_MUTED, size=11),
        )
        return fig

    @staticmethod
    def _round_bars(fig: go.Figure, bargap: float = 0.4, bargroupgap: float = 0.08) -> go.Figure:
        fig.update_traces(marker_cornerradius=4, selector=dict(type="bar"))
        fig.update_layout(bargap=bargap, bargroupgap=bargroupgap)
        return fig

    @staticmethod
    def _fold_to_other(df: pd.DataFrame, key: str, metric: str, top_n: int = 6, other_label: str = "Autres") -> pd.DataFrame:
        """Repli 'Autres' : au-delà de top_n séries, agrège le reste — jamais
        plus de couleurs catégorielles que de slots sûrs sur un graphique.
        other_label est personnalisable pour éviter une collision avec une
        vraie valeur de la donnée (ex. la catégorie "Autre" de statut_migratoire)."""
        totals = df.groupby(key)[metric].sum().sort_values(ascending=False)
        keep = set(totals.head(top_n).index)
        d = df.copy()
        d[key] = d[key].where(d[key].isin(keep), other_label)
        return d

    # ---- Vue d'ensemble --------------------------------------------------

    def evolution_annuelle(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["annee_besoin", "pec_besoin"]).size().reset_index(name="n")
        fig = px.bar(
            d, x="annee_besoin", y="n", color="pec_besoin", barmode="group",
            color_discrete_map=PEC_COLOR,
            labels={"annee_besoin": "Année", "n": "Nombre de besoins", "pec_besoin": "Statut"},
            custom_data=["pec_besoin"],
        )
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{y} besoins — %{x}<extra></extra>")
        fig = self._round_bars(fig)
        return self._base_layout(fig, "Besoins reçus vs satisfaits", "par année")

    def repartition_besoins(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["besoin", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map(STATUT_LABEL)
        d = d.sort_values("n")
        fig = px.bar(
            d, x="n", y="besoin", color="statut", orientation="h",
            color_discrete_map=STATUT_COLOR,
            labels={"n": "Nombre", "besoin": ""},
            custom_data=["besoin", "statut"],
        )
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} : %{x}<extra></extra>")
        fig = self._round_bars(fig, bargap=0.3)
        return self._base_layout(fig, "Types de besoins exprimés", "volume et statut")

    # ---- Genre & statut ----------------------------------------------------

    def par_genre(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["genre", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map(STATUT_LABEL)
        fig = px.bar(
            d, x="genre", y="n", color="statut", barmode="group",
            color_discrete_map=STATUT_COLOR,
            labels={"genre": "", "n": "Nombre"},
            custom_data=["genre", "statut"],
        )
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b> — %{customdata[1]}<br>%{y} besoins<extra></extra>")
        fig = self._round_bars(fig, bargap=0.45)
        return self._base_layout(fig, "Besoins par genre", "satisfaits vs non satisfaits")

    def statut_migratoire(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("statut_migratoire").agg(total=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d = d.sort_values("total")
        fig = px.bar(
            d, x="total", y="statut_migratoire", color="taux", orientation="h",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"total": "Nombre de demandeurs", "statut_migratoire": "", "taux": "Taux %"},
            text="taux", custom_data=["statut_migratoire", "taux"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="outside",
            textfont=dict(color=pal.INK_SECONDARY, size=11),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x} demandeurs — taux %{customdata[1]}%<extra></extra>",
        )
        fig = self._round_bars(fig, bargap=0.3)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Profil des demandeurs par statut migratoire",
                                  "longueur = volume, couleur = taux de satisfaction", show_legend=False)

    def taux_genre_besoin(self, df: pd.DataFrame) -> go.Figure:
        d = (
            df.groupby(["besoin", "genre"])
            .agg(taux=("satisfait", "mean"), n=("id", "count"))
            .reset_index()
        )
        d["taux"] = (d["taux"] * 100).round(1)
        genres = sorted(d["genre"].unique())
        color_map = {g: pal.CATEGORICAL[i] for i, g in enumerate(genres)}
        fig = px.bar(
            d, x="besoin", y="taux", color="genre", barmode="group",
            color_discrete_map=color_map,
            labels={"besoin": "", "taux": "Taux de satisfaction (%)"},
            custom_data=["besoin", "genre", "n"],
        )
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b> — %{customdata[1]}<br>%{y}% (n=%{customdata[2]})<extra></extra>")
        fig.add_hline(y=50, line_dash="dot", line_width=1, line_color=pal.BASELINE,
                       annotation_text="Seuil 50%", annotation_font=dict(color=pal.INK_MUTED, size=10))
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.35)
        return self._base_layout(fig, "Taux de satisfaction croisé", "par type de besoin et par genre")

    def par_pays_origine(self, df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        d = (
            df.groupby("pays_origine").size().reset_index(name="n")
            .sort_values("n", ascending=False).head(top_n).sort_values("n")
        )
        fig = px.bar(d, x="n", y="pays_origine", orientation="h",
                      labels={"n": "Nombre de bénéficiaires", "pays_origine": ""},
                      custom_data=["pays_origine"])
        fig.update_traces(
            marker_color=pal.CATEGORICAL[0],
            hovertemplate="<b>%{customdata[0]}</b><br>%{x} bénéficiaires<extra></extra>",
        )
        fig = self._round_bars(fig, bargap=0.3)
        return self._base_layout(fig, f"Top {top_n} pays d'origine", "", show_legend=False)

    # ---- Géographie ---------------------------------------------------------

    def par_province(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("province").agg(total=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d = d.sort_values("total")
        fig = px.bar(
            d, x="total", y="province", color="taux", orientation="h",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"total": "Nombre de besoins", "province": "", "taux": "Taux %"},
            custom_data=["province", "taux"],
        )
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{x} besoins — taux %{customdata[1]}%<extra></extra>")
        fig = self._round_bars(fig, bargap=0.25)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Volume de besoins par province", "couleur = taux de satisfaction", show_legend=False)

    def taux_province(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("province").agg(total=("id", "count"), satisfaits=("satisfait", "sum")).reset_index()
        d["taux"] = (d["satisfaits"] / d["total"] * 100).round(1)
        d = d.sort_values("taux")
        fig = px.bar(
            d, x="taux", y="province", orientation="h", color="taux",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"taux": "Taux de satisfaction (%)", "province": ""},
            text="taux", custom_data=["province", "satisfaits", "total"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="outside",
            textfont=dict(color=pal.INK_SECONDARY, size=11),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} / %{customdata[2]}<extra></extra>",
        )
        fig.add_vline(x=50, line_dash="dot", line_width=1, line_color=pal.BASELINE)
        fig.update_xaxes(range=[0, 108], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.25)
        return self._base_layout(fig, "Taux de satisfaction", "par province", show_legend=False)

    def evolution_mensuelle(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["periode", "province"]).size().reset_index(name="n")
        d = self._fold_to_other(d, "province", "n", top_n=6)
        d = d.groupby(["periode", "province"], as_index=False)["n"].sum().sort_values("periode")

        provinces = [p for p in d["province"].unique() if p != "Autres"]
        color_map = {p: pal.CATEGORICAL[i] for i, p in enumerate(provinces)}
        color_map["Autres"] = pal.MUTED

        fig = px.line(
            d, x="periode", y="n", color="province", markers=True,
            color_discrete_map=color_map,
            labels={"periode": "", "n": "Besoins exprimés", "province": ""},
            custom_data=["province"],
        )
        fig.update_traces(
            line=dict(width=2),
            marker=dict(size=8, line=dict(width=2, color=pal.SURFACE)),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x} : %{y} besoins<extra></extra>",
        )
        return self._base_layout(fig, "Évolution mensuelle des besoins",
                                  "par province — top 6, reste replié en «Autres»")

    def par_statut_migratoire_donut(self, df: pd.DataFrame) -> go.Figure:
        """Vue complémentaire compacte pour petits écrans : part de chaque
        statut migratoire, repliée à 6 tranches + Autres."""
        other_label = "Autres statuts"
        d = df.groupby("statut_migratoire").size().reset_index(name="n")
        d = self._fold_to_other(d, "statut_migratoire", "n", top_n=6, other_label=other_label)
        d = d.groupby("statut_migratoire", as_index=False)["n"].sum().sort_values("n", ascending=False)
        labels = [s for s in d["statut_migratoire"] if s != other_label]
        colors = [pal.CATEGORICAL[i] for i in range(len(labels))]
        color_map = dict(zip(labels, colors))
        color_map[other_label] = pal.MUTED
        fig = go.Figure(
            go.Pie(
                labels=d["statut_migratoire"], values=d["n"], hole=0.58,
                marker=dict(colors=[color_map[s] for s in d["statut_migratoire"]],
                             line=dict(color=pal.SURFACE, width=2)),
                textinfo="percent", textposition="inside", insidetextorientation="horizontal",
                textfont=dict(color=pal.INK_PRIMARY, size=12, family=pal.FONT_FAMILY),
                hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
            )
        )
        fig = self._base_layout(fig, "Répartition par statut migratoire", "")
        # Trop d'entrées pour une légende horizontale en tête (chevauche le titre) :
        # légende verticale à droite du donut à la place.
        fig.update_layout(
            legend=dict(
                orientation="v", x=1.02, xanchor="left", y=0.5, yanchor="middle",
                font=dict(size=11, color=pal.INK_SECONDARY), title=None,
            ),
            margin=dict(t=56, b=24, l=8, r=140),
        )
        return fig
