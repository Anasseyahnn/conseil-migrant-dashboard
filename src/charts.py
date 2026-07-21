from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import palette as pal

STATUT_LABEL = {True: "Satisfait", False: "Non satisfait"}
STATUT_COLOR = {"Satisfait": pal.STATUS["good"], "Non satisfait": pal.STATUS["critical"]}
PEC_COLOR = {"Oui": pal.STATUS["good"], "Non": pal.STATUS["critical"]}
# Rouge/vert sont réservés au statut de satisfaction (NPS) — le genre ne
# doit jamais emprunter ces teintes, pour ne pas laisser croire à un signal
# de satisfaction là où il n'y en a pas.
GENRE_COLOR = {"Masculin": "#2a78d6", "Féminin": "#FF6347"}  # bleu / tomate


def _inside_label_colors(taux_values) -> list[str]:
    """Couleur de texte par barre selon la teinte du remplissage à ce taux :
    le milieu de l'échelle divergente est un gris pâle (encre foncée lisible),
    les extrêmes sont un rouge/bleu saturé (texte blanc nécessaire)."""
    return [pal.INK_PRIMARY if 35 <= t <= 65 else "#ffffff" for t in taux_values]


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
        d["pct"] = d.groupby("annee_besoin")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        fig = px.bar(
            d, x="annee_besoin", y="pct", color="pec_besoin", barmode="relative",
            color_discrete_map=PEC_COLOR,
            labels={"annee_besoin": "Année", "pct": "Part des besoins (%)", "pec_besoin": "Statut"},
            text="pct", custom_data=["pec_besoin", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{y}% des besoins de %{x} (n=%{customdata[1]})<extra></extra>",
        )
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig = self._round_bars(fig)
        return self._base_layout(fig, "Besoins reçus vs satisfaits", "part par année")

    def repartition_besoins(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["besoin", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map(STATUT_LABEL)
        order = d.groupby("besoin")["n"].sum().sort_values().index.tolist()
        d["pct"] = d.groupby("besoin")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        fig = px.bar(
            d, x="pct", y="besoin", color="statut", orientation="h",
            color_discrete_map=STATUT_COLOR, category_orders={"besoin": order},
            labels={"pct": "Part (%)", "besoin": ""},
            text="pct", custom_data=["besoin", "statut", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} : %{x}% (n=%{customdata[2]})<extra></extra>",
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.3)
        return self._base_layout(fig, "Types de besoins exprimés", "part satisfaite / non satisfaite")

    # ---- Genre & statut ----------------------------------------------------

    def par_genre(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["genre", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map(STATUT_LABEL)
        d["pct"] = d.groupby("genre")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        fig = px.bar(
            d, x="genre", y="pct", color="statut", barmode="relative",
            color_discrete_map=STATUT_COLOR,
            labels={"genre": "", "pct": "Part (%)"},
            text="pct", custom_data=["genre", "statut", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b> — %{customdata[1]}<br>%{y}% (n=%{customdata[2]})<extra></extra>",
        )
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.45)
        return self._base_layout(fig, "Besoins par genre", "part satisfaite / non satisfaite")

    def statut_migratoire(self, df: pd.DataFrame) -> go.Figure:
        total = len(df)
        d = df.groupby("statut_migratoire").agg(n=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d["part"] = (d["n"] / total * 100).round(1)
        d = d.sort_values("part")
        fig = px.bar(
            d, x="part", y="statut_migratoire", color="taux", orientation="h",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"part": "Part des demandeurs (%)", "statut_migratoire": "", "taux": "Taux %"},
            text="taux", custom_data=["statut_migratoire", "taux", "part"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_inside_label_colors(d["taux"]), size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[2]}% des demandeurs — taux %{customdata[1]}%<extra></extra>",
        )
        fig.update_xaxes(ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.3)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Profil des demandeurs par statut migratoire",
                                  "longueur = part du total, couleur = taux de satisfaction", show_legend=False)

    def taux_genre_besoin(self, df: pd.DataFrame) -> go.Figure:
        d = (
            df.groupby(["besoin", "genre"])
            .agg(taux=("satisfait", "mean"), n=("id", "count"))
            .reset_index()
        )
        d["taux"] = (d["taux"] * 100).round(1)
        fig = px.bar(
            d, x="besoin", y="taux", color="genre", barmode="group",
            color_discrete_map=GENRE_COLOR,
            labels={"besoin": "", "taux": "Taux de satisfaction (%)"},
            text="taux", custom_data=["besoin", "genre", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            hovertemplate="<b>%{customdata[0]}</b> — %{customdata[1]}<br>%{y}% (n=%{customdata[2]})<extra></extra>",
        )
        # Contraste : blanc lisible sur le bleu, mais pas sur le tomate (trop
        # clair) — encre foncée pour Féminin.
        for trace in fig.data:
            text_color = pal.INK_PRIMARY if trace.name == "Féminin" else "#ffffff"
            trace.update(textfont=dict(color=text_color, size=11, family=pal.FONT_FAMILY))
        fig.add_hline(y=50, line_dash="dot", line_width=1, line_color=pal.BASELINE,
                       annotation_text="Seuil 50%", annotation_font=dict(color=pal.INK_MUTED, size=10))
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.35)
        return self._base_layout(fig, "Taux de satisfaction croisé", "par type de besoin et par genre")

    def par_pays_origine(self, df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        total = len(df)
        d = df.groupby("pays_origine").size().reset_index(name="n")
        d["pct"] = (d["n"] / total * 100).round(1)
        d = d.sort_values("pct", ascending=False).head(top_n).sort_values("pct")
        fig = px.bar(d, x="pct", y="pays_origine", orientation="h",
                      labels={"pct": "Part des bénéficiaires (%)", "pays_origine": ""},
                      text="pct", custom_data=["pays_origine", "n"])
        fig.update_traces(
            marker_color=pal.CATEGORICAL[0],
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x}% des bénéficiaires (n=%{customdata[1]})<extra></extra>",
        )
        fig.update_xaxes(ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.3)
        return self._base_layout(fig, f"Top {top_n} pays d'origine", "", show_legend=False)

    # ---- Géographie ---------------------------------------------------------

    def par_province(self, df: pd.DataFrame) -> go.Figure:
        total = len(df)
        d = df.groupby("province").agg(n=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d["part"] = (d["n"] / total * 100).round(1)
        d = d.sort_values("part")
        fig = px.bar(
            d, x="part", y="province", color="taux", orientation="h",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"part": "Part des besoins (%)", "province": "", "taux": "Taux %"},
            text="taux", custom_data=["province", "taux", "part"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_inside_label_colors(d["taux"]), size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[2]}% des besoins — taux %{customdata[1]}%<extra></extra>",
        )
        fig.update_xaxes(ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.25)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Volume de besoins par province", "longueur = part du total, couleur = taux de satisfaction", show_legend=False)

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
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_inside_label_colors(d["taux"]), size=11, family=pal.FONT_FAMILY),
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
        d["pct"] = d.groupby("periode")["n"].transform(lambda s: (s / s.sum() * 100).round(1))

        provinces = [p for p in d["province"].unique() if p != "Autres"]
        color_map = {p: pal.CATEGORICAL[i] for i, p in enumerate(provinces)}
        color_map["Autres"] = pal.MUTED

        fig = px.line(
            d, x="periode", y="pct", color="province", markers=True,
            color_discrete_map=color_map,
            labels={"periode": "", "pct": "Part des besoins du mois (%)", "province": ""},
            custom_data=["province", "n"],
        )
        fig.update_traces(
            line=dict(width=2),
            marker=dict(size=8, line=dict(width=2, color=pal.SURFACE)),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x} : %{y}% (n=%{customdata[1]})<extra></extra>",
        )
        fig.update_yaxes(ticksuffix="%")
        # Une seule étiquette par ligne — la dernière valeur — jamais un
        # nombre sur chaque point (illisible avec autant de mois × séries).
        for trace in fig.data:
            values = list(trace.y)
            labels = [""] * (len(values) - 1) + [f"{values[-1]:.0f}%"] if values else []
            trace.update(mode="lines+markers+text", text=labels,
                          textposition="top center",
                          textfont=dict(color=trace.line.color, size=11, family=pal.FONT_FAMILY))
        return self._base_layout(fig, "Évolution mensuelle des besoins",
                                  "part par province, par mois — top 6, reste replié en «Autres»")

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
