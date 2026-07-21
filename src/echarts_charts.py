from __future__ import annotations

import pandas as pd

from . import palette as pal
from .echarts_theme import axis_style, base_option, diverging_color, label_color, render

STATUT_LABEL = {True: "Pris en charge", False: "Non pris en charge"}
STATUT_COLOR = {"Pris en charge": pal.STATUS["good"], "Non pris en charge": pal.STATUS["critical"]}
PEC_COLOR = {"Oui": pal.STATUS["good"], "Non": pal.STATUS["critical"]}
GENRE_COLOR = {"Masculin": "#4a86d1", "Féminin": "#e08268"}

ANCIENNETE_BINS = [0, 1, 3, 5, float("inf")]
ANCIENNETE_LABELS = ["Moins d'1 an", "1 à 3 ans", "3 à 5 ans", "5 ans et +"]


class EChartsBuilder:
    """Même contrat que ChartBuilder (Plotly) — mêmes noms de méthodes, même
    logique de données — mais retourne du HTML prêt pour
    st.components.v1.html au lieu d'une figure Plotly."""

    @staticmethod
    def _fold_to_other(df: pd.DataFrame, key: str, metric: str, top_n: int = 6,
                        other_label: str = "Autres") -> pd.DataFrame:
        totals = df.groupby(key)[metric].sum().sort_values(ascending=False)
        keep = set(totals.head(top_n).index)
        d = df.copy()
        d[key] = d[key].where(d[key].isin(keep), other_label)
        return d

    def _empty(self, title: str, reason: str, height: int = 420) -> str:
        opt = base_option(title, "")
        opt["graphic"] = {
            "type": "text", "left": "center", "top": "middle",
            "style": {"text": f"Indisponible — {reason}", "fill": pal.INK_MUTED, "fontSize": 13},
        }
        return render(opt, height=height)

    # ---- Vue d'ensemble --------------------------------------------------

    def evolution_annuelle(self, df: pd.DataFrame) -> str:
        d = df.groupby(["annee_besoin", "pec_besoin"]).size().reset_index(name="n")
        d["pct"] = d.groupby("annee_besoin")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        annees = sorted(d["annee_besoin"].dropna().unique().tolist())
        non_vals = [float(d[(d.annee_besoin == a) & (d.pec_besoin == "Non")]["pct"].sum()) for a in annees]
        oui_vals = [float(d[(d.annee_besoin == a) & (d.pec_besoin == "Oui")]["pct"].sum()) for a in annees]

        opt = base_option("Besoins reçus vs pris en charge", "part par année")
        opt.update({
            "legend": {"top": 28, "right": 0, "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "grid": {"left": 45, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "category", "data": [str(int(a)) for a in annees], **axis_style()},
            "yAxis": {"type": "value", "max": 100, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": [
                {"name": "Non pris en charge", "type": "bar", "stack": "t", "data": non_vals,
                 "itemStyle": {"color": pal.STATUS["critical"], "borderRadius": [0, 0, 4, 4]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
                {"name": "Pris en charge", "type": "bar", "stack": "t", "data": oui_vals,
                 "itemStyle": {"color": pal.STATUS["good"], "borderRadius": [4, 4, 0, 0]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
            ],
        })
        return render(opt, height=420, dom_id="evolution_annuelle")

    def repartition_besoins(self, df: pd.DataFrame) -> str:
        d = df.groupby(["besoin", "pris_en_charge"]).size().reset_index(name="n")
        d["statut"] = d["pris_en_charge"].map(STATUT_LABEL)
        order = d.groupby("besoin")["n"].sum().sort_values().index.tolist()
        d["pct"] = d.groupby("besoin")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        non_vals = [float(d[(d.besoin == b) & (~d.pris_en_charge)]["pct"].sum()) for b in order]
        oui_vals = [float(d[(d.besoin == b) & (d.pris_en_charge)]["pct"].sum()) for b in order]

        opt = base_option("Types de besoins exprimés", "part prise en charge / non prise en charge")
        opt.update({
            "legend": {"top": 28, "right": 0, "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "grid": {"left": 130, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "value", "max": 100, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": order, **axis_style()},
            "series": [
                {"name": "Non pris en charge", "type": "bar", "stack": "t", "data": non_vals,
                 "itemStyle": {"color": pal.STATUS["critical"], "borderRadius": [4, 0, 0, 4]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
                {"name": "Pris en charge", "type": "bar", "stack": "t", "data": oui_vals,
                 "itemStyle": {"color": pal.STATUS["good"], "borderRadius": [0, 4, 4, 0]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
            ],
        })
        return render(opt, height=420, dom_id="repartition_besoins")

    # ---- Genre & statut ----------------------------------------------------

    def par_genre(self, df: pd.DataFrame) -> str:
        d = df.groupby(["genre", "pris_en_charge"]).size().reset_index(name="n")
        d["statut"] = d["pris_en_charge"].map(STATUT_LABEL)
        genres = sorted(d["genre"].unique().tolist())
        d["pct"] = d.groupby("genre")["n"].transform(lambda s: (s / s.sum() * 100).round(1))
        non_vals = [float(d[(d.genre == g) & (~d.pris_en_charge)]["pct"].sum()) for g in genres]
        oui_vals = [float(d[(d.genre == g) & (d.pris_en_charge)]["pct"].sum()) for g in genres]

        opt = base_option("Besoins par genre", "part prise en charge / non prise en charge")
        opt.update({
            "legend": {"top": 28, "right": 0, "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "grid": {"left": 45, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "category", "data": genres, **axis_style()},
            "yAxis": {"type": "value", "max": 100, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": [
                {"name": "Non pris en charge", "type": "bar", "stack": "t", "data": non_vals, "barWidth": "45%",
                 "itemStyle": {"color": pal.STATUS["critical"], "borderRadius": [0, 0, 4, 4]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
                {"name": "Pris en charge", "type": "bar", "stack": "t", "data": oui_vals, "barWidth": "45%",
                 "itemStyle": {"color": pal.STATUS["good"], "borderRadius": [4, 4, 0, 0]},
                 "label": {"show": True, "formatter": "{c}%", "color": "#fff"}},
            ],
        })
        return render(opt, height=420, dom_id="par_genre")

    def statut_migratoire(self, df: pd.DataFrame) -> str:
        total_demandeurs = df["id"].nunique()
        n_demandeurs = df.groupby("statut_migratoire")["id"].nunique()
        taux = df.groupby("statut_migratoire")["pris_en_charge"].mean()
        d = pd.DataFrame({"statut_migratoire": n_demandeurs.index, "n": n_demandeurs.values})
        d["taux"] = (d["statut_migratoire"].map(taux) * 100).round(1)
        d["part"] = (d["n"] / total_demandeurs * 100).round(1)
        d = d.sort_values("part")

        opt = base_option("Profil des demandeurs par statut migratoire",
                           "longueur = part du total, couleur = taux de prise en charge")
        opt.update({
            "grid": {"left": 160, "right": 20, "top": 60, "bottom": 30},
            "xAxis": {"type": "value", "min": 0, "max": 20, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": d["statut_migratoire"].tolist(), **axis_style()},
            "series": [{
                "type": "bar", "barCategoryGap": "30%",
                "data": [
                    {"value": row.part,
                     "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4},
                     "label": {"formatter": f"{row.taux:.0f}%", "color": label_color(row.taux)}}
                    for row in d.itertuples()
                ],
                "label": {"show": True, "position": "inside", "fontSize": 11},
            }],
        })
        return render(opt, height=420, dom_id="statut_migratoire")

    def taux_genre_besoin(self, df: pd.DataFrame) -> str:
        g = (df.groupby(["besoin", "genre"]).agg(taux=("pris_en_charge", "mean"), n=("id", "count")).reset_index())
        g["taux"] = (g["taux"] * 100).round(1)
        besoins = sorted(g["besoin"].unique().tolist())
        genres = sorted(g["genre"].unique().tolist())

        series = []
        for genre in genres:
            vals = [float(g[(g.besoin == b) & (g.genre == genre)]["taux"].sum()) for b in besoins]
            color = GENRE_COLOR.get(genre, pal.CATEGORICAL[0])
            text_color = pal.INK_PRIMARY if genre == "Féminin" else "#ffffff"
            series.append({
                "name": genre, "type": "bar", "data": vals,
                "itemStyle": {"color": color, "borderRadius": 4},
                "label": {"show": True, "formatter": "{c}%", "color": text_color, "position": "inside"},
            })

        opt = base_option("Taux de prise en charge croisé", "par type de besoin et par genre")
        opt.update({
            "legend": {"top": 28, "right": 0, "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "grid": {"left": 45, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "category", "data": besoins, **axis_style()},
            "yAxis": {"type": "value", "max": 100, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": series,
        })
        return render(opt, height=420, dom_id="taux_genre_besoin")

    def par_pays_origine(self, df: pd.DataFrame, top_n: int = 10) -> str:
        d = (df.groupby("pays_origine")["id"].nunique().reset_index(name="n")
             .sort_values("n", ascending=False).head(top_n).sort_values("n"))
        opt = base_option(f"Top {top_n} pays d'origine", "")
        opt.update({
            "grid": {"left": 150, "right": 30, "top": 40, "bottom": 30},
            "xAxis": {"type": "value", "axisLabel": {"color": pal.INK_MUTED}, "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": d["pays_origine"].tolist(), **axis_style()},
            "series": [{
                "type": "bar", "barCategoryGap": "30%", "data": d["n"].tolist(),
                "itemStyle": {"color": pal.CATEGORICAL[0], "borderRadius": 4},
                "label": {"show": True, "position": "inside", "color": "#fff"},
            }],
        })
        return render(opt, height=460, dom_id="par_pays_origine")

    # ---- Géographie ---------------------------------------------------------

    def par_province(self, df: pd.DataFrame) -> str:
        total = len(df)
        d = df.groupby("province").agg(n=("id", "count"), taux=("pris_en_charge", "mean")).reset_index()
        d["taux"] = (d["taux"] * 100).round(1)
        d["part"] = (d["n"] / total * 100).round(1)
        d = d.sort_values("part")

        opt = base_option("Volume de besoins par province",
                           "longueur = part du total, couleur = taux de prise en charge")
        opt.update({
            "grid": {"left": 160, "right": 20, "top": 60, "bottom": 30},
            "xAxis": {"type": "value", "min": 0, "max": 20, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": d["province"].tolist(), **axis_style()},
            "series": [{
                "type": "bar", "barCategoryGap": "25%",
                "data": [
                    {"value": row.part,
                     "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4},
                     "label": {"formatter": f"{row.taux:.0f}%", "color": label_color(row.taux)}}
                    for row in d.itertuples()
                ],
                "label": {"show": True, "position": "inside", "fontSize": 11},
            }],
        })
        return render(opt, height=420, dom_id="par_province")

    def taux_province(self, df: pd.DataFrame) -> str:
        d = df.groupby("province").agg(total=("id", "count"), pris=("pris_en_charge", "sum")).reset_index()
        d["taux"] = (d["pris"] / d["total"] * 100).round(1)
        d = d.sort_values("taux")

        opt = base_option("Taux de prise en charge", "par province")
        opt.update({
            "grid": {"left": 160, "right": 20, "top": 40, "bottom": 30},
            "xAxis": {"type": "value", "min": 0, "max": 100, "interval": 20,
                      "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": d["province"].tolist(), **axis_style()},
            "series": [{
                "type": "bar", "barCategoryGap": "25%",
                "data": [
                    {"value": row.taux,
                     "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4},
                     "label": {"formatter": f"{row.taux:.0f}%", "color": label_color(row.taux)}}
                    for row in d.itertuples()
                ],
                "label": {"show": True, "position": "inside", "fontSize": 11},
                "markLine": {
                    "silent": True, "symbol": "none",
                    "lineStyle": {"color": pal.BASELINE, "type": "dashed"},
                    "data": [{"xAxis": 50}],
                },
            }],
        })
        return render(opt, height=420, dom_id="taux_province")

    def evolution_mensuelle(self, df: pd.DataFrame) -> str:
        d = df.groupby(["periode", "province"]).size().reset_index(name="n")
        d = self._fold_to_other(d, "province", "n", top_n=6)
        d = d.groupby(["periode", "province"], as_index=False)["n"].sum().sort_values("periode")
        d["pct"] = d.groupby("periode")["n"].transform(lambda s: (s / s.sum() * 100).round(1))

        periodes = sorted(d["periode"].unique().tolist())
        provinces = [p for p in d["province"].unique().tolist() if p != "Autres"]
        color_map = {p: pal.CATEGORICAL[i] for i, p in enumerate(provinces)}
        color_map["Autres"] = pal.MUTED
        all_series_names = provinces + (["Autres"] if "Autres" in d["province"].unique() else [])

        series = []
        for name in all_series_names:
            vals = []
            for p in periodes:
                row = d[(d.periode == p) & (d.province == name)]
                vals.append(float(row["pct"].sum()) if len(row) else None)
            # étiquette uniquement sur le dernier point réel de la série
            last_idx = max((i for i, v in enumerate(vals) if v is not None), default=None)
            data_points = []
            for i, v in enumerate(vals):
                if v is None:
                    data_points.append(None)
                elif i == last_idx:
                    data_points.append({"value": v, "label": {"show": True, "formatter": f"{v:.0f}%"}})
                else:
                    data_points.append({"value": v, "label": {"show": False}})
            series.append({
                "name": name, "type": "line", "data": data_points, "symbolSize": 8,
                "lineStyle": {"width": 2, "color": color_map[name]},
                "itemStyle": {"color": color_map[name], "borderColor": pal.SURFACE, "borderWidth": 2},
                "label": {"color": color_map[name], "fontSize": 11, "position": "top"},
            })

        opt = base_option("Évolution mensuelle des besoins",
                           "part par province, par mois — top 6, reste replié en «Autres»")
        opt.update({
            "legend": {"top": 28, "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "grid": {"left": 45, "right": 20, "top": 78, "bottom": 50},
            "xAxis": {"type": "category", "data": periodes, "axisLabel": {"rotate": 45, "color": pal.INK_MUTED, "fontSize": 10},
                      "axisLine": axis_style()["axisLine"]},
            "yAxis": {"type": "value", "min": 0, "max": 100, "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": series,
        })
        return render(opt, height=440, dom_id="evolution_mensuelle")

    def par_statut_migratoire_donut(self, df: pd.DataFrame) -> str:
        other_label = "Autres statuts"
        d = df.groupby("statut_migratoire").size().reset_index(name="n")
        d = self._fold_to_other(d, "statut_migratoire", "n", top_n=4, other_label=other_label)
        d = d.groupby("statut_migratoire", as_index=False)["n"].sum().sort_values("n", ascending=False)
        labels = [s for s in d["statut_migratoire"] if s != other_label]
        color_map = {s: pal.CATEGORICAL[i] for i, s in enumerate(labels)}
        color_map[other_label] = pal.MUTED

        opt = base_option("Répartition par statut migratoire", "")
        opt.update({
            "legend": {"orient": "vertical", "right": 10, "top": "middle",
                       "textStyle": {"color": pal.INK_SECONDARY, "fontSize": 11}},
            "series": [{
                "type": "pie", "radius": ["48%", "72%"], "center": ["38%", "55%"],
                "data": [{"name": s, "value": int(n), "itemStyle": {"color": color_map[s]}}
                         for s, n in zip(d["statut_migratoire"], d["n"])],
                "label": {"formatter": "{d}%", "color": pal.INK_PRIMARY, "fontSize": 12},
                "itemStyle": {"borderColor": pal.SURFACE, "borderWidth": 2},
            }],
        })
        return render(opt, height=420, dom_id="par_statut_migratoire_donut")

    # ---- Ancienneté & famille ------------------------------------------

    def prise_en_charge_anciennete(self, df: pd.DataFrame) -> str:
        if "anciennete_ans" not in df.columns:
            return self._empty("Ancienneté d'installation", "donnée d'arrivée absente")
        d = df[df["anciennete_ans"] >= 0].copy()
        d["tranche"] = pd.cut(d["anciennete_ans"], bins=ANCIENNETE_BINS,
                               labels=ANCIENNETE_LABELS, right=False, include_lowest=True)
        g = (d.groupby("tranche", observed=True).agg(taux=("pris_en_charge", "mean"), n=("id", "count"))
             .reindex(ANCIENNETE_LABELS).dropna(subset=["n"]).reset_index())
        if g.empty:
            return self._empty("Prise en charge par ancienneté", "aucune ancienneté exploitable")
        g["taux"] = (g["taux"] * 100).round(1)

        opt = base_option("Prise en charge par ancienneté d'installation",
                           "années écoulées depuis l'arrivée, au moment du besoin")
        opt.update({
            "grid": {"left": 45, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "category", "data": g["tranche"].astype(str).tolist(), **axis_style()},
            "yAxis": {"type": "value", "min": 0, "max": 100, "interval": 20,
                      "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": [{
                "type": "bar", "barCategoryGap": "40%",
                "data": [{"value": row.taux, "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4}}
                         for row in g.itertuples()],
                "label": {"show": True, "position": "top", "formatter": "{c}%", "color": pal.INK_SECONDARY},
                "markLine": {"silent": True, "symbol": "none",
                             "lineStyle": {"color": pal.BASELINE, "type": "dashed"}, "data": [{"yAxis": 50}]},
            }],
        })
        return render(opt, height=420, dom_id="prise_en_charge_anciennete")

    def par_nombre_enfants(self, df: pd.DataFrame) -> str:
        d = df.dropna(subset=["nombre_enfants"]).copy()
        if d.empty:
            return self._empty("Prise en charge par charge familiale", "donnée enfants absente")
        g = d.groupby("nombre_enfants").agg(taux=("pris_en_charge", "mean"), n=("id", "count")).reset_index()
        g["taux"] = (g["taux"] * 100).round(1)
        g["label"] = g["nombre_enfants"].astype(int).map(
            lambda k: "Sans enfant" if k == 0 else ("1 enfant" if k == 1 else f"{k} enfants"))

        opt = base_option("Prise en charge par charge familiale", "nombre d'enfants à charge")
        opt.update({
            "grid": {"left": 45, "right": 20, "top": 68, "bottom": 30},
            "xAxis": {"type": "category", "data": g["label"].tolist(), **axis_style()},
            "yAxis": {"type": "value", "min": 0, "max": 100, "interval": 20,
                      "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "series": [{
                "type": "bar", "barCategoryGap": "40%",
                "data": [{"value": row.taux, "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4}}
                         for row in g.itertuples()],
                "label": {"show": True, "position": "top", "formatter": "{c}%", "color": pal.INK_SECONDARY},
                "markLine": {"silent": True, "symbol": "none",
                             "lineStyle": {"color": pal.BASELINE, "type": "dashed"}, "data": [{"yAxis": 50}]},
            }],
        })
        return render(opt, height=420, dom_id="par_nombre_enfants")

    # ---- Synthèse pilotage -------------------------------------------------

    def sous_couverture(self, df: pd.DataFrame, global_taux: float, min_n: int = 15,
                         bottom: int = 8, view: str = "faibles") -> str:
        """view="faibles" : seulement les segments les plus sous-couverts
        (vue d'alerte). view="tous" : tous les segments, triés — pour voir
        où se situe chaque segment par rapport au global, pas seulement
        les pires (demandé après confusion sur le sous-titre : sans cette
        bascule, l'utilisateur ne voit jamais qu'il existe des segments
        au-dessus de la moyenne)."""
        dims = {"Besoin": "besoin", "Statut": "statut_migratoire", "Province": "province", "Genre": "genre"}
        rows = []
        for prefix, col in dims.items():
            if col not in df.columns:
                continue
            g = df.groupby(col).agg(taux=("pris_en_charge", "mean"), n=("id", "count")).reset_index()
            g = g[g["n"] >= min_n]
            for _, r in g.iterrows():
                rows.append({"segment": f"{prefix} · {r[col]}", "taux": round(r["taux"] * 100, 1), "n": int(r["n"])})
        if not rows:
            return self._empty("Où la prise en charge décroche", f"aucun segment d'au moins {min_n} personnes")

        d_all = pd.DataFrame(rows).sort_values("taux", ascending=False)
        if view == "tous":
            d = d_all
            title = "Tous les segments vs le global"
            subtitle = f"{len(d)} segments (≥ {min_n} personnes), triés par taux de prise en charge"
            height = max(420, 34 * len(d) + 120)
        else:
            d = d_all.sort_values("taux").head(bottom).sort_values("taux", ascending=False)
            title = "Où la prise en charge décroche"
            subtitle = (f"les {bottom} segments les PLUS FAIBLES uniquement (≥ {min_n} personnes) — "
                        "bascule «Tous les segments» pour voir l'ensemble")
            height = 420

        opt = base_option(title, subtitle)
        opt.update({
            "grid": {"left": 190, "right": 40, "top": 40, "bottom": 30},
            "xAxis": {"type": "value", "min": 0, "max": 100, "interval": 20,
                      "axisLabel": {"formatter": "{value}%", "color": pal.INK_MUTED},
                      "splitLine": axis_style()["splitLine"]},
            "yAxis": {"type": "category", "data": d["segment"].tolist()[::-1], **axis_style()},
            "series": [{
                "type": "bar", "barCategoryGap": "30%",
                "data": [
                    {"value": row.taux,
                     "itemStyle": {"color": diverging_color(row.taux), "borderRadius": 4},
                     "label": {"formatter": f"{row.taux:.0f}%", "color": label_color(row.taux)}}
                    for row in d.sort_values("taux").itertuples()
                ],
                "label": {"show": True, "position": "inside", "fontSize": 11},
                "markLine": {
                    "silent": True, "symbol": "none",
                    "lineStyle": {"color": pal.INK_MUTED, "type": "dashed", "width": 1.5},
                    "label": {"formatter": f"Global {global_taux:.0f}%", "color": pal.INK_MUTED, "fontSize": 10},
                    "data": [{"xAxis": global_taux}],
                },
            }],
        })
        return render(opt, height=height, dom_id="sous_couverture")
