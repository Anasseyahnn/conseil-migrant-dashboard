from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartBuilder:
    """Regroupe la palette et les graphiques du tableau de bord — une
    instance = un thème visuel cohérent appliqué à tous les graphiques."""

    COL_OUI = "#1B6CA8"
    COL_NON = "#E05C5C"
    COL_MASC = "#1B6CA8"
    COL_FEM = "#F4A261"
    SCALE_TAUX = ["#E05C5C", "#E8A838", "#1B6CA8"]
    BG = "white"

    def _layout(self, fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
        fig.update_layout(
            title=dict(
                text=f"<b>{title}</b>"
                + (f"<br><span style='font-size:12px;color:#8A95A3'>{subtitle}</span>" if subtitle else "")
            ),
            paper_bgcolor=self.BG,
            plot_bgcolor=self.BG,
            legend=dict(orientation="h", y=1.18, font=dict(size=11), title=None),
            margin=dict(t=75, b=40, l=40, r=20),
            font=dict(color="#1E293B"),
        )
        fig.update_xaxes(gridcolor="#F0F2F5")
        fig.update_yaxes(gridcolor="#F0F2F5")
        return fig

    def evolution_annuelle(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["annee_besoin", "pec_besoin"]).size().reset_index(name="n")
        fig = px.bar(
            d, x="annee_besoin", y="n", color="pec_besoin", barmode="group",
            color_discrete_map={"Oui": self.COL_OUI, "Non": self.COL_NON},
            labels={"annee_besoin": "Année", "n": "Nombre de besoins", "pec_besoin": "Statut"},
        )
        return self._layout(fig, "Besoins reçus vs satisfaits", "par année")

    def repartition_besoins(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["besoin", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map({True: "Satisfait", False: "Non satisfait"})
        fig = px.bar(
            d, x="n", y="besoin", color="statut", orientation="h",
            color_discrete_map={"Satisfait": self.COL_OUI, "Non satisfait": self.COL_NON},
            labels={"n": "Nombre", "besoin": ""},
        )
        return self._layout(fig, "Types de besoins exprimés", "volume et statut")

    def par_genre(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["genre", "satisfait"]).size().reset_index(name="n")
        d["statut"] = d["satisfait"].map({True: "Satisfait", False: "Non satisfait"})
        fig = px.bar(
            d, x="genre", y="n", color="statut", barmode="group",
            color_discrete_map={"Satisfait": self.COL_OUI, "Non satisfait": self.COL_NON},
            labels={"genre": "", "n": "Nombre"},
        )
        return self._layout(fig, "Besoins par genre", "satisfaits vs non satisfaits")

    def statut_migratoire(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("statut_migratoire").agg(total=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d = d.sort_values("total")
        fig = px.bar(
            d, x="total", y="statut_migratoire", color="taux", orientation="h",
            color_continuous_scale=self.SCALE_TAUX,
            labels={"total": "Nombre de demandeurs", "statut_migratoire": "", "taux": "Taux %"},
        )
        return self._layout(fig, "Profil des demandeurs par statut migratoire", "couleur = taux de satisfaction")

    def taux_genre_besoin(self, df: pd.DataFrame) -> go.Figure:
        d = (
            df.groupby(["besoin", "genre"])
            .agg(taux=("satisfait", "mean"), n=("id", "count"))
            .reset_index()
        )
        d["taux"] = (d["taux"] * 100).round(1)
        fig = px.bar(
            d, x="besoin", y="taux", color="genre", barmode="group",
            color_discrete_map={"Masculin": self.COL_MASC, "Féminin": self.COL_FEM},
            labels={"besoin": "", "taux": "Taux de satisfaction (%)"},
        )
        fig.add_hline(y=50, line_dash="dash", line_color="#CBD5E1")
        return self._layout(fig, "Taux de satisfaction croisé", "par type de besoin et par genre")

    def par_province(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("province").agg(total=("id", "count"), taux=("satisfait", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d = d.sort_values("total")
        fig = px.bar(
            d, x="total", y="province", color="taux", orientation="h",
            color_continuous_scale=self.SCALE_TAUX,
            labels={"total": "Nombre de besoins", "province": "", "taux": "Taux %"},
        )
        return self._layout(fig, "Volume de besoins par province", "couleur = taux de satisfaction")

    def taux_province(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby("province").agg(total=("id", "count"), satisfaits=("satisfait", "sum")).reset_index()
        d["taux"] = (d["satisfaits"] / d["total"] * 100).round(1)
        d = d.sort_values("taux")
        fig = px.bar(
            d, x="taux", y="province", orientation="h", color="taux",
            color_continuous_scale=self.SCALE_TAUX,
            labels={"taux": "Taux de satisfaction (%)", "province": ""},
        )
        fig.add_vline(x=50, line_dash="dash", line_color="#CBD5E1")
        return self._layout(fig, "Taux de satisfaction", "par province")

    def evolution_mensuelle(self, df: pd.DataFrame) -> go.Figure:
        d = df.groupby(["periode", "province"]).size().reset_index(name="n").sort_values("periode")
        fig = px.line(
            d, x="periode", y="n", color="province", markers=True,
            labels={"periode": "", "n": "Besoins exprimés", "province": ""},
        )
        return self._layout(fig, "Évolution mensuelle des besoins", "par province")

    def par_pays_origine(self, df: pd.DataFrame, top_n: int = 12) -> go.Figure:
        d = (
            df.groupby("pays_origine").size().reset_index(name="n")
            .sort_values("n", ascending=False).head(top_n).sort_values("n")
        )
        fig = px.bar(d, x="n", y="pays_origine", orientation="h",
                      labels={"n": "Nombre de bénéficiaires", "pays_origine": ""})
        fig.update_traces(marker_color=self.COL_OUI)
        return self._layout(fig, f"Top {top_n} pays d'origine", "")
