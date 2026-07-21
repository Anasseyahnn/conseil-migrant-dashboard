from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import palette as pal

STATUT_LABEL = {True: "Pris en charge", False: "Non pris en charge"}
STATUT_COLOR = {"Pris en charge": pal.STATUS["good"], "Non pris en charge": pal.STATUS["critical"]}
PEC_COLOR = {"Oui": pal.STATUS["good"], "Non": pal.STATUS["critical"]}
# Rouge/vert sont réservés au statut de prise en charge — le genre ne doit
# jamais emprunter ces teintes, pour ne pas laisser croire à un signal de
# prise en charge là où il n'y en a pas.
# Adouci (21/07), revalidé : ΔE 17.6 protan (largement > cible 8) — PASS.
GENRE_COLOR = {"Masculin": "#4a86d1", "Féminin": "#e08268"}  # bleu / tomate adoucis

# Tranches d'ancienneté d'installation (années depuis l'arrivée). Bornes
# choisies sur des paliers d'intégration usuels : première année (accès aux
# droits en cours), 1-3 ans, 3-5 ans, 5 ans et plus (installation durable).
ANCIENNETE_BINS = [0, 1, 3, 5, float("inf")]
ANCIENNETE_LABELS = ["Moins d'1 an", "1 à 3 ans", "3 à 5 ans", "5 ans et +"]


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
        return self._base_layout(fig, "Besoins reçus vs pris en charge", "part par année")

    def repartition_besoins(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["besoin", "pris_en_charge"]).size().reset_index(name="n")
        d["statut"] = d["pris_en_charge"].map(STATUT_LABEL)
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
        return self._base_layout(fig, "Types de besoins exprimés", "part prise en charge / non prise en charge")

    # ---- Genre & statut ----------------------------------------------------

    def par_genre(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["genre", "pris_en_charge"]).size().reset_index(name="n")
        d["statut"] = d["pris_en_charge"].map(STATUT_LABEL)
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
        return self._base_layout(fig, "Besoins par genre", "part prise en charge / non prise en charge")

    def statut_migratoire(self, df: pd.DataFrame) -> go.Figure:
        # "Profil des demandeurs" parle de PERSONNES, pas de besoins — une
        # personne peut exprimer plusieurs besoins (plusieurs lignes, même
        # id). Dédupliquer par id ici, sinon un statut avec des demandeurs
        # qui reviennent souvent apparaîtrait gonflé sans raison.
        total_demandeurs = df["id"].nunique()
        n_demandeurs = df.groupby("statut_migratoire")["id"].nunique()
        taux = df.groupby("statut_migratoire")["pris_en_charge"].mean()
        d = pd.DataFrame({"statut_migratoire": n_demandeurs.index, "n": n_demandeurs.values})
        d["taux"] = (d["statut_migratoire"].map(taux) * 100).round(1)
        d["part"] = (d["n"] / total_demandeurs * 100).round(1)
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
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[2]}% des demandeurs (personnes uniques) — taux de prise en charge de leurs besoins %{customdata[1]}%<extra></extra>",
        )
        # Échelle 0-20% commune à ce graphique ET à "Volume de besoins par
        # province" (même famille de mesure : part du total entre N
        # catégories) — jamais 0-100% (les rendrait illisibles, tassés sous
        # 20%) ni deux échelles différentes entre les deux (trompeur : une
        # même longueur de barre représenterait des valeurs différentes).
        fig.update_xaxes(range=[0, 20], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.3)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Profil des demandeurs par statut migratoire",
                                  "longueur = part du total, couleur = taux de prise en charge", show_legend=False)

    def taux_genre_besoin(self, df: pd.DataFrame) -> go.Figure:
        d = (
            df.groupby(["besoin", "genre"])
            .agg(taux=("pris_en_charge", "mean"), n=("id", "count"))
            .reset_index()
        )
        d["taux"] = (d["taux"] * 100).round(1)
        fig = px.bar(
            d, x="besoin", y="taux", color="genre", barmode="group",
            color_discrete_map=GENRE_COLOR,
            labels={"besoin": "", "taux": "Taux de prise en charge (%)"},
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
        return self._base_layout(fig, "Taux de prise en charge croisé", "par type de besoin et par genre")

    def par_pays_origine(self, df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        # Seul graphique en valeur absolue : les parts (%) sur un top 10 avec
        # des effectifs proches (6-8% chacun) sont trop peu différenciantes.
        # "Bénéficiaires" = personnes, pas besoins — dédupliquer par id.
        d = (
            df.groupby("pays_origine")["id"].nunique().reset_index(name="n")
            .sort_values("n", ascending=False).head(top_n).sort_values("n")
        )
        fig = px.bar(d, x="n", y="pays_origine", orientation="h",
                      labels={"n": "Nombre de bénéficiaires", "pays_origine": ""},
                      text="n", custom_data=["pays_origine"])
        fig.update_traces(
            marker_color=pal.CATEGORICAL[0],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{x} bénéficiaires<extra></extra>",
        )
        fig = self._round_bars(fig, bargap=0.3)
        return self._base_layout(fig, f"Top {top_n} pays d'origine", "", show_legend=False)

    # ---- Géographie ---------------------------------------------------------

    def par_province(self, df: pd.DataFrame) -> go.Figure:
        total = len(df)
        d = df.groupby("province").agg(n=("id", "count"), taux=("pris_en_charge", "mean")).reset_index()
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
        # Même échelle 0-20% que "Profil des demandeurs par statut
        # migratoire" — même famille de mesure (part du total), comparables
        # entre eux visuellement, jamais deux échelles différentes.
        fig.update_xaxes(range=[0, 20], ticksuffix="%")
        fig = self._round_bars(fig, bargap=0.25)
        fig.update_coloraxes(colorbar=dict(title="Taux %", tickfont=dict(color=pal.INK_MUTED)))
        return self._base_layout(fig, "Volume de besoins par province", "longueur = part du total, couleur = taux de prise en charge", show_legend=False)

    def taux_province(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("province").agg(total=("id", "count"), pris=("pris_en_charge", "sum")).reset_index()
        d["taux"] = (d["pris"] / d["total"] * 100).round(1)
        d = d.sort_values("taux")
        fig = px.bar(
            d, x="taux", y="province", orientation="h", color="taux",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"taux": "Taux de prise en charge (%)", "province": ""},
            text="taux", custom_data=["province", "pris", "total"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_inside_label_colors(d["taux"]), size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} / %{customdata[2]}<extra></extra>",
        )
        fig.add_vline(x=50, line_dash="dot", line_width=1, line_color=pal.BASELINE)
        fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=20)
        fig = self._round_bars(fig, bargap=0.25)
        # Pas de colorbar ici : contrairement à "Volume de besoins par
        # province" (où la couleur est la SEULE vue du taux), le taux est
        # déjà l'axe X et déjà étiqueté sur chaque barre — une échelle de
        # couleur redondante ne ferait que voler la place des barres.
        fig.update_coloraxes(showscale=False)
        return self._base_layout(fig, "Taux de prise en charge", "par province", show_legend=False)

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
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
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

    # ---- Ancienneté & famille ---------------------------------------------

    def prise_en_charge_anciennete(self, df: pd.DataFrame) -> go.Figure:
        """Taux de prise en charge par ancienneté d'installation — répond à
        « les personnes récemment arrivées sont-elles moins bien couvertes ? ».
        Les lignes à ancienneté négative (arrivée saisie après le besoin) ou
        manquante sont exclues ici et signalées par le bandeau qualité."""
        if "anciennete_ans" not in df.columns:
            return self._empty("Ancienneté d'installation", "donnée d'arrivée absente")
        d = df[df["anciennete_ans"] >= 0].copy()
        d["tranche"] = pd.cut(d["anciennete_ans"], bins=ANCIENNETE_BINS,
                               labels=ANCIENNETE_LABELS, right=False, include_lowest=True)
        g = (d.groupby("tranche", observed=True)
             .agg(taux=("pris_en_charge", "mean"), n=("id", "count"))
             .reindex(ANCIENNETE_LABELS).dropna(subset=["n"]).reset_index())
        if g.empty:
            return self._empty("Prise en charge par ancienneté", "aucune ancienneté exploitable")
        g["taux"] = (g["taux"] * 100).round(1)
        g["n"] = g["n"].astype(int)
        fig = px.bar(
            g, x="tranche", y="taux", color="taux",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"tranche": "", "taux": "Taux de prise en charge (%)"},
            text="taux", custom_data=["tranche", "n"],
            category_orders={"tranche": ANCIENNETE_LABELS},
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="outside",
            textfont=dict(color=pal.INK_SECONDARY, size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>Taux de prise en charge %{y}% (n=%{customdata[1]})<extra></extra>",
        )
        fig.add_hline(y=50, line_dash="dot", line_width=1, line_color=pal.BASELINE)
        fig.update_yaxes(range=[0, 100], ticksuffix="%", dtick=20)
        fig = self._round_bars(fig, bargap=0.4)
        fig.update_coloraxes(showscale=False)
        return self._base_layout(fig, "Prise en charge par ancienneté d'installation",
                                  "années écoulées depuis l'arrivée, au moment du besoin", show_legend=False)

    def par_nombre_enfants(self, df: pd.DataFrame) -> go.Figure:
        """Volume et prise en charge par nombre d'enfants — indicateur de
        vulnérabilité familiale (une famille nombreuse cumule plus de besoins
        et est plus exposée)."""
        d = df.dropna(subset=["nombre_enfants"]).copy()
        if d.empty:
            return self._empty("Prise en charge par charge familiale", "donnée enfants absente")
        g = (d.groupby("nombre_enfants")
             .agg(taux=("pris_en_charge", "mean"), n=("id", "count"))
             .reset_index())
        g["taux"] = (g["taux"] * 100).round(1)
        g["label"] = g["nombre_enfants"].astype(int).map(
            lambda k: "Sans enfant" if k == 0 else ("1 enfant" if k == 1 else f"{k} enfants"))
        fig = px.bar(
            g, x="label", y="taux", color="taux",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"label": "", "taux": "Taux de prise en charge (%)"},
            text="taux", custom_data=["label", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="outside",
            textfont=dict(color=pal.INK_SECONDARY, size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>Taux de prise en charge %{y}% (n=%{customdata[1]})<extra></extra>",
        )
        fig.add_hline(y=50, line_dash="dot", line_width=1, line_color=pal.BASELINE)
        fig.update_yaxes(range=[0, 100], ticksuffix="%", dtick=20)
        fig = self._round_bars(fig, bargap=0.4)
        fig.update_coloraxes(showscale=False)
        return self._base_layout(fig, "Prise en charge par charge familiale",
                                  "nombre d'enfants à charge", show_legend=False)

    # ---- Synthèse pilotage -------------------------------------------------

    def sous_couverture(self, df: pd.DataFrame, global_taux: float, min_n: int = 15,
                        bottom: int = 8) -> go.Figure:
        """« Où la prise en charge décroche » : classe les segments (toutes
        dimensions confondues) par taux de prise en charge croissant, et
        montre les plus bas. Garde-fou min_n : un segment à faible effectif
        donnerait un taux instable (100 % sur 2 lignes ne veut rien dire) —
        on ne remonte que les segments d'au moins `min_n` personnes."""
        dims = {
            "Besoin": "besoin",
            "Statut": "statut_migratoire",
            "Province": "province",
            "Genre": "genre",
        }
        rows = []
        for prefix, col in dims.items():
            if col not in df.columns:
                continue
            g = df.groupby(col).agg(taux=("pris_en_charge", "mean"), n=("id", "count")).reset_index()
            g = g[g["n"] >= min_n]
            for _, r in g.iterrows():
                rows.append({"segment": f"{prefix} · {r[col]}", "taux": round(r["taux"] * 100, 1),
                             "n": int(r["n"])})
        if not rows:
            return self._empty("Où la prise en charge décroche",
                                f"aucun segment d'au moins {min_n} personnes")
        d = pd.DataFrame(rows).sort_values("taux").head(bottom).sort_values("taux", ascending=False)
        fig = px.bar(
            d, x="taux", y="segment", orientation="h", color="taux",
            color_continuous_scale=pal.DIVERGING, range_color=[0, 100],
            labels={"taux": "Taux de prise en charge (%)", "segment": ""},
            text="taux", custom_data=["segment", "n"],
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_inside_label_colors(d["taux"]), size=11, family=pal.FONT_FAMILY),
            hovertemplate="<b>%{customdata[0]}</b><br>Taux %{x}% (n=%{customdata[1]})<extra></extra>",
        )
        # Référence = taux global, pour lire chaque segment comme un écart.
        fig.add_vline(x=global_taux, line_dash="dot", line_width=1.5, line_color=pal.INK_MUTED,
                       annotation_text=f"Global {global_taux:.0f}%",
                       annotation_font=dict(color=pal.INK_MUTED, size=10))
        fig.update_xaxes(range=[0, 100], ticksuffix="%", dtick=20)
        fig = self._round_bars(fig, bargap=0.3)
        fig.update_coloraxes(showscale=False)
        return self._base_layout(fig, "Où la prise en charge décroche",
                                  f"segments les moins couverts (≥ {min_n} personnes)", show_legend=False)

    # ---- Utilitaire --------------------------------------------------------

    def _empty(self, title: str, reason: str) -> go.Figure:
        """Figure de repli lisible quand une dimension n'est pas exploitable
        (donnée absente, filtre trop restrictif) — jamais un graphique vide
        sans explication."""
        fig = go.Figure()
        fig.add_annotation(text=f"Indisponible — {reason}", showarrow=False,
                            font=dict(color=pal.INK_MUTED, size=13, family=pal.FONT_FAMILY),
                            x=0.5, y=0.5, xref="paper", yref="paper")
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return self._base_layout(fig, title, "", show_legend=False)
