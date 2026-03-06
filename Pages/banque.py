# -*- coding: utf-8 -*-
import dash
from dash import html, dcc, Input, Output, callback, no_update, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, base64, io

# --- IMPORT DU MOTEUR EXTERNE (Script 1) ---
try:
    from utils.report_engine import generate_report
except ImportError:
    def generate_report():
        candidates = [
            r"C:\Users\user\Documents\Data Ingenieur2\Projet_banque\Data\rapport_bgfi.html",
            os.path.join(os.getcwd(), "Data", "rapport_bgfi.html"),
        ]
        for p in candidates:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
        return "<p> Fichier rapport_bgfi.html introuvable dans Data/</p>"

dash.register_page(__name__, path="/banque", name="Banque")

C_BLUE      = "#004a99"
C_GOLD      = "#E8A020"
C_GOLD_PALE = "#fdf3e0"
C_DARK      = "#0d1b2e"
C_MUTED     = "#6b7c96"
C_CREAM     = "#f8f5ef"
C_GREEN     = "#1a8a5a"
C_RED       = "#c00000"

BASE_LAYOUT = dict(
    font=dict(family="DM Sans, Arial", color="#1a2940"),
    paper_bgcolor="white", plot_bgcolor="white",
    margin=dict(t=50, b=40, l=50, r=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
AX_CLEAN  = dict(showgrid=False, linecolor="#dddddd", visible=False)
AY_CLEAN  = dict(tickfont=dict(size=9), linecolor="#dddddd")
AY_GRID   = dict(gridcolor="#f0f0f0", linecolor="#dddddd")
BASE_SLIM = {k: v for k, v in BASE_LAYOUT.items() if k not in ("margin", "legend")}


# ═══════════════════════════════════════════════════════════════════════════
# CHARGEMENT ET CALCULS
# ═══════════════════════════════════════════════════════════════════════════
def _find_data():
    candidates = [
        r"C:\Users\user\Documents\Data Ingenieur2\Projet_banque\Data\BASE_SENEGAL2.xlsx",
        os.path.join(os.getcwd(), 'Data', 'BASE_SENEGAL2.xlsx'),
    ]
    for p in candidates:
        if os.path.exists(p): return p
    return None

def load_data():
    path = _find_data()
    if not path: return pd.DataFrame()
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.strip()
    rename_map = {}
    for c in df.columns:
        new = (c.replace("Û","U").replace("û","u").replace("Ô","O").replace("ô","o")
                .replace("É","E").replace("é","e").replace("È","E").replace("è","e")
                .replace("Î","I").replace("î","i").replace("Â","A").replace("â","a"))
        if new != c: rename_map[c] = new
    df.rename(columns=rename_map, inplace=True)

    df["ROE"]          = (df["RESULTAT.NET"]         / df["FONDS.PROPRE"]) * 100
    df["ROA"]          = (df["RESULTAT.NET"]         / df["BILAN"])        * 100
    df["LEVIER"]       =  df["BILAN"]                / df["FONDS.PROPRE"]
    df["RISQUE_PCT"]   = (df["COUT.DU.RISQUE"]       / df["BILAN"])        * 100
    df["RATIO_TRANSF"] = (df["EMPLOI"]               / df["BILAN"])        * 100
    df["PNB_BILAN"]    = (df["PRODUIT.NET.BANCAIRE"] / df["BILAN"])        * 100
    df["EMP_AG"]       =  df["EMPLOI"]   / df["AGENCE"]
    df["RES_AG"]       =  df["RESSOURCES"] / df["AGENCE"]
    df["EMP_EFF"]      =  df["EMPLOI"]   / df["EFFECTIF"]
    df["RES_EFF"]      =  df["RESSOURCES"] / df["EFFECTIF"]

    for y in df["ANNEE"].unique():
        m = df["ANNEE"] == y
        tot = df.loc[m, "BILAN"].sum()
        df.loc[m, "PART_MARCHE"] = (df.loc[m, "BILAN"] / tot) * 100

    def tcam5(b):
        d  = df[df["Sigle"] == b]
        v0 = d[d["ANNEE"] == 2015]["BILAN"].values
        v1 = d[d["ANNEE"] == 2020]["BILAN"].values
        return round(((v1[0]/v0[0])**(1/5)-1)*100, 1) if len(v0) and len(v1) and v0[0]>0 else np.nan

    df["TCAM_BILAN"] = df["Sigle"].map({b: tcam5(b) for b in df["Sigle"].unique()})
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df

DF    = load_data()
YEARS = sorted(DF["ANNEE"].unique().tolist()) if not DF.empty else []
BANKS = sorted(DF["Sigle"].unique().tolist()) if not DF.empty else []
GROUPS= ["Tous"] + sorted(DF["Goupe_Bancaire"].unique().tolist()) if not DF.empty else []
YEARS_FIN = sorted(DF.groupby("ANNEE")["RESULTAT.NET"].count().where(lambda x: x > 0).dropna().index.tolist()) if not DF.empty else []
YEAR_FIN_DEFAULT = YEARS_FIN[-1] if YEARS_FIN else 2020

KPI_OPTS = [
    {"label": " Total Bilan",    "value": "BILAN"},
    {"label": " Emplois",        "value": "EMPLOI"},
    {"label": " Ressources",     "value": "RESSOURCES"},
    {"label": " Fonds Propres",  "value": "FONDS.PROPRE"},
    {"label": " Nb Comptes",     "value": "COMPTE"},
    {"label": " Résultat Net",   "value": "RESULTAT.NET"},
]

# ═══════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════
def kpi_card(label, value, sub="", color=C_BLUE, icon=""):
    return html.Div(style={"background":"white","borderRadius":"10px","padding":"1.1rem 1.3rem",
        "borderLeft":f"4px solid {color}","boxShadow":"0 2px 10px rgba(0,0,0,0.06)","height":"100%"}, children=[
        html.Div(style={"display":"flex","justifyContent":"space-between","alignItems":"flex-start"}, children=[
            html.Div([
                html.Div(label, style={"fontSize":"0.68rem","textTransform":"uppercase","letterSpacing":"0.1em","color":C_MUTED,"fontWeight":"600"}),
                html.Div(value, style={"fontSize":"1.5rem","fontWeight":"800","color":C_DARK,"fontFamily":"Playfair Display,serif","lineHeight":"1.1","marginTop":"0.25rem"}),
                html.Div(sub,   style={"fontSize":"0.72rem","color":C_MUTED,"marginTop":"0.2rem"}),
            ]),
            html.Div(icon, style={"fontSize":"1.7rem","opacity":"0.2"}),
        ])
    ])

def section_hdr(title, sub=""):
    return html.Div(style={"marginBottom":"1rem"}, children=[
        html.Div(style={"width":"28px","height":"3px","borderRadius":"2px","marginBottom":"0.4rem",
                         "background":f"linear-gradient(90deg,{C_BLUE},{C_GOLD})"}),
        html.H5(title, style={"fontFamily":"Playfair Display,serif","fontWeight":"700","color":C_DARK,"margin":"0","fontSize":"1.1rem"}),
        html.P(sub, style={"color":C_MUTED,"fontSize":"0.8rem","margin":"0.15rem 0 0"}) if sub else None,
    ])

def card(children, mb=True):
    return html.Div(children, style={"background":"white","borderRadius":"10px","padding":"1rem",
        "boxShadow":"0 2px 8px rgba(0,0,0,0.06)","marginBottom":"1rem" if mb else "0"})

def empty_fig(msg="Données non disponibles"):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font=dict(size=13,color=C_MUTED))
    fig.update_layout(**BASE_LAYOUT, height=300)
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════════
layout = html.Div(style={"backgroundColor":C_CREAM,"minHeight":"100vh"}, children=[

    dcc.Download(id="bk-download-pdf"),
    dcc.Download(id="download-report-utils"),

    html.Div(style={"background":f"linear-gradient(135deg,{C_DARK} 0%,{C_BLUE} 100%)",
                     "padding":"2.2rem 2.5rem 1.8rem","position":"relative","overflow":"hidden"}, children=[
        html.Div(style={"position":"absolute","top":"-50px","right":"-50px","width":"260px","height":"260px",
                         "borderRadius":"50%","border":"50px solid rgba(232,160,32,0.08)"}),
        html.Div(style={"position":"relative","zIndex":"1","display":"flex",
                         "justifyContent":"space-between","alignItems":"flex-end","flexWrap":"wrap","gap":"1rem"}, children=[
            html.Div([
                html.Div("SECTEUR BANCAIRE · SÉNÉGAL 2015–2020",
                         style={"fontSize":"0.68rem","letterSpacing":"0.2em","textTransform":"uppercase",
                                "color":C_GOLD,"fontWeight":"600","marginBottom":"0.4rem"}),
                html.H1("Analyse du Positionnement Bancaire",
                        style={"fontFamily":"Playfair Display,serif","fontSize":"clamp(1.5rem,3vw,2.2rem)",
                               "fontWeight":"900","color":"white","margin":"0 0 0.4rem"}),
                html.P("24 banques · 6 années · Ratios financiers, productivité et positionnement stratégique",
                       style={"color":"rgba(255,255,255,0.5)","fontSize":"0.85rem","margin":"0"}),
            ]),
            html.Div(style={"display":"flex","flexDirection":"column","gap":"0.5rem","alignItems":"flex-end"}, children=[
                html.Div(style={"display":"flex","gap":"0.7rem"}, children=[
                    html.Button(" Rapport Standard", id="btn-gen-report", n_clicks=0,
                        style={"background":"white","color":C_BLUE,"border":"none","borderRadius":"6px",
                               "padding":"0.7rem 1.2rem","fontWeight":"700","fontSize":"0.75rem",
                               "letterSpacing":"0.06em","textTransform":"uppercase","cursor":"pointer"}),
                    html.Button(" Rapport Analytique", id="bk-btn-download", n_clicks=0,
                        style={"background":C_GOLD,"color":C_DARK,"border":"none","borderRadius":"6px",
                               "padding":"0.7rem 1.2rem","fontWeight":"700","fontSize":"0.75rem",
                               "letterSpacing":"0.06em","textTransform":"uppercase","cursor":"pointer",
                               "boxShadow":"0 4px 16px rgba(232,160,32,0.35)"}),
                ]),
                html.Div(id="bk-download-status",
                         style={"fontSize":"0.72rem","color":"rgba(255,255,255,0.5)","textAlign":"right"}),
            ]),
        ]),
    ]),

    html.Div(style={"background":"white","padding":"0.9rem 2.5rem",
                     "boxShadow":"0 2px 12px rgba(0,0,0,0.06)",
                     "position":"sticky","top":"64px","zIndex":"100",
                     "borderBottom":f"3px solid {C_GOLD}"}, children=[
        dbc.Row(className="g-2 align-items-end", children=[
            dbc.Col([html.Div(" Banque",     style={"fontSize":"0.68rem","fontWeight":"600","textTransform":"uppercase","color":C_MUTED}),
                     dcc.Dropdown(id="bk-bank",    options=[{"label":b,"value":b} for b in BANKS], value="BGFI",  clearable=False, style={"fontSize":"0.83rem"})], md=2),
            dbc.Col([html.Div(" Année",      style={"fontSize":"0.68rem","fontWeight":"600","textTransform":"uppercase","color":C_MUTED}),
                     dcc.Dropdown(id="bk-year",    options=[{"label":str(y),"value":y} for y in YEARS], value=2020, clearable=False, style={"fontSize":"0.83rem"})], md=1),
            dbc.Col([html.Div(" Groupe",     style={"fontSize":"0.68rem","fontWeight":"600","textTransform":"uppercase","color":C_MUTED}),
                     dcc.Dropdown(id="bk-group",   options=[{"label":g,"value":g} for g in GROUPS], value="Tous",  clearable=False, style={"fontSize":"0.83rem"})], md=2),
            dbc.Col([html.Div(" Indicateur", style={"fontSize":"0.68rem","fontWeight":"600","textTransform":"uppercase","color":C_MUTED}),
                     dcc.Dropdown(id="bk-kpi",     options=KPI_OPTS, value="BILAN", clearable=False, style={"fontSize":"0.83rem"})], md=3),
            dbc.Col([html.Div(" Comparer",   style={"fontSize":"0.68rem","fontWeight":"600","textTransform":"uppercase","color":C_MUTED}),
                     dcc.Dropdown(id="bk-compare", options=[{"label":b,"value":b} for b in BANKS], value=["CBAO","SGBS"], multi=True, style={"fontSize":"0.83rem"})], md=4),
        ])
    ]),

    html.Div(style={"padding":"1.8rem 2.5rem","maxWidth":"1600px","margin":"0 auto"}, children=[
        html.Div(id="bk-kpis", style={"marginBottom":"1.5rem"}),
        dcc.Tabs(id="bk-tabs", value="marche", style={"marginBottom":"1.2rem"}, children=[
            dcc.Tab(label=" Vue Marché",        value="marche",
                style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
            dcc.Tab(label=" Positionnement",    value="position",
                style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
            dcc.Tab(label=" Évolution",         value="evolution",
                style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
            dcc.Tab(label=" Ratios Financiers", value="ratios",
                style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
            dcc.Tab(label=" Productivité",      value="productivite",
                style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
            dcc.Tab(label=" Carte",            value="carte",
                    style={"padding":"0.5rem 1rem","fontWeight":"600","fontSize":"0.8rem"},
                    selected_style={"padding":"0.5rem 1rem","fontWeight":"700","fontSize":"0.8rem","borderTop":f"3px solid {C_BLUE}","color":C_BLUE}),
        ]),
        html.Div(id="bk-content"),
    ]),
])



# ── Helpers carte ──────────────────────────────────────────────────────────
def rank_str(col, bank, da, nb):
    try:
        lst = da.dropna(subset=[col]).sort_values(col,ascending=False)["Sigle"].tolist()
        return f"#{lst.index(bank)+1}/{nb}" if bank in lst else "N/A"
    except: return "N/A"

def _agence_rank(da, bank):
    ds = da.dropna(subset=["AGENCE"]).sort_values("AGENCE", ascending=True)
    if ds.empty: return empty_fig("Pas de données agences")
    fig = go.Figure(go.Bar(
        x=ds["AGENCE"], y=ds["Sigle"], orientation="h",
        marker_color=[C_GOLD if s==bank else C_BLUE for s in ds["Sigle"]],
        text=[str(int(v)) for v in ds["AGENCE"]], textposition="outside",
    ))
    fig.update_layout(**BASE_SLIM, height=420, showlegend=False,
                       xaxis=AX_CLEAN, yaxis=AY_CLEAN,
                       margin=dict(t=30,b=20,l=60,r=40))
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACK 1 — Rapport Standard (utils/report_engine)
# ═══════════════════════════════════════════════════════════════════════════
@callback(
    Output("download-report-utils", "data"),
    Input("btn-gen-report", "n_clicks"),
    prevent_initial_call=True,
)
def download_utils_report(n_clicks):
    content = generate_report()
    return dict(content=content, filename="Rapport_Standard.html")


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACK 2 — Rapport Analytique (généré dynamiquement)
# ═══════════════════════════════════════════════════════════════════════════
@callback(
    Output("bk-download-pdf",    "data"),
    Output("bk-download-status", "children"),
    Input("bk-btn-download",     "n_clicks"),
    State("bk-bank",             "value"),
    State("bk-year",             "value"),
    prevent_initial_call=True,
)
def cb_internal_report(n_clicks, bank, year):
    try:
        da = DF[DF["ANNEE"] == year]
        db = da[da["Sigle"] == bank]
        if db.empty: return no_update, " Données insuffisantes"
        r  = db.iloc[0]
        nb = da["Sigle"].nunique()

        def fmv(v, mode="M"):
            if pd.isna(v): return "N/A"
            if mode=="M":  return f"{v/1000:,.1f} Mds FCFA" if v>=1000 else f"{v:,.0f} M FCFA"
            if mode=="%":  return f"{v:.2f}%"
            if mode=="x":  return f"{v:.1f}x"
            return str(int(v))

        def rank(col):
            try:
                lst = da.dropna(subset=[col]).sort_values(col,ascending=False)["Sigle"].tolist()
                return f"#{lst.index(bank)+1}/{nb}" if bank in lst else "N/A"
            except: return "N/A"

        db_all = DF[DF["Sigle"]==bank].sort_values("ANNEE")
        v0 = db_all[db_all["ANNEE"]==2015]["BILAN"].values
        v1 = db_all[db_all["ANNEE"]==2020]["BILAN"].values
        tcam_str = f"+{((v1[0]/v0[0])**(1/5)-1)*100:.1f}%" if (len(v0) and len(v1) and v0[0]>0) else "N/A"

        html_content = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<style>
  body{{font-family:Arial,sans-serif;background:#f8f5ef;margin:0;color:#1a2940}}
  .header{{background:linear-gradient(135deg,#0d1b2e,#004a99);padding:40px 50px;color:white}}
  .header h1{{font-size:2rem;font-weight:900;margin:0 0 8px}}
  .sub{{color:rgba(255,255,255,0.5);font-size:0.85rem}}
  .gold-bar{{background:#E8A020;height:5px}}
  .body{{padding:40px 50px;max-width:900px;margin:0 auto}}
  .sec{{font-size:1.2rem;font-weight:700;color:#004a99;border-left:4px solid #E8A020;padding-left:12px;margin:2rem 0 1rem}}
  .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:2rem}}
  .box{{background:white;border-radius:8px;padding:16px 20px;border-left:4px solid #004a99;box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
  .lbl{{font-size:0.65rem;text-transform:uppercase;color:#6b7c96;font-weight:600;margin-bottom:4px}}
  .val{{font-size:1.4rem;font-weight:700;color:#0d1b2e}}
  .sub2{{font-size:0.7rem;color:#6b7c96;margin-top:2px}}
  .gold{{border-left-color:#E8A020!important}} .green{{border-left-color:#1a8a5a!important}}
  table{{width:100%;border-collapse:collapse;background:white;font-size:0.85rem;box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
  th{{background:#004a99;color:white;padding:10px 14px;text-align:left;font-size:0.75rem;text-transform:uppercase}}
  td{{padding:10px 14px;border-bottom:1px solid #f0f0f0}}
  .footer{{background:#0d1b2e;color:rgba(255,255,255,0.4);font-size:0.72rem;padding:20px 50px;text-align:center;margin-top:3rem}}
</style></head><body>
<div class="header">
  <div style="font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;color:#E8A020;margin-bottom:8px">RAPPORT DE POSITIONNEMENT</div>
  <h1>{bank} BANK</h1><div class="sub">Analyse · Sénégal · {year}</div>
</div>
<div class="gold-bar"></div>
<div class="body">
  <div class="sec">Indicateurs Bilanciels</div>
  <div class="grid">
    <div class="box"><div class="lbl">Total Bilan {year}</div><div class="val">{fmv(r['BILAN'])}</div><div class="sub2">{rank('BILAN')} du marché</div></div>
    <div class="box gold"><div class="lbl">Part de Marché</div><div class="val">{fmv(r.get('PART_MARCHE',float('nan')),'%')}</div><div class="sub2">du total bilan</div></div>
    <div class="box green"><div class="lbl">TCAM 2015→2020</div><div class="val">{tcam_str}</div><div class="sub2">croissance annuelle</div></div>
    <div class="box"><div class="lbl">Emplois</div><div class="val">{fmv(r['EMPLOI'])}</div><div class="sub2">{rank('EMPLOI')} du marché</div></div>
    <div class="box"><div class="lbl">Ressources</div><div class="val">{fmv(r['RESSOURCES'])}</div><div class="sub2">{rank('RESSOURCES')} du marché</div></div>
    <div class="box gold"><div class="lbl">Fonds Propres</div><div class="val">{fmv(r['FONDS.PROPRE'])}</div><div class="sub2">{rank('FONDS.PROPRE')} du marché</div></div>
  </div>
  <div class="sec">Ratios Financiers</div>
  <table><thead><tr><th>Ratio</th><th>Valeur {year}</th><th>Classement</th></tr></thead><tbody>
    <tr><td>ROE</td><td>{fmv(r.get('ROE',float('nan')),'%')}</td><td>{rank('ROE')}</td></tr>
    <tr><td>ROA</td><td>{fmv(r.get('ROA',float('nan')),'%')}</td><td>{rank('ROA')}</td></tr>
    <tr><td>Levier Financier</td><td>{fmv(r.get('LEVIER',float('nan')),'x')}</td><td>{rank('LEVIER')}</td></tr>
    <tr><td>Coût du Risque</td><td>{fmv(r.get('RISQUE_PCT',float('nan')),'%')}</td><td>{rank('RISQUE_PCT')}</td></tr>
    <tr><td>Taux de Transformation</td><td>{fmv(r.get('RATIO_TRANSF',float('nan')),'%')}</td><td>{rank('RATIO_TRANSF')}</td></tr>
  </tbody></table>
  <div class="sec">Réseau Commercial</div>
  <div class="grid">
    <div class="box"><div class="lbl">Comptes</div><div class="val">{fmv(r.get('COMPTE',float('nan')),'int')}</div><div class="sub2">{rank('COMPTE')}</div></div>
    <div class="box"><div class="lbl">Agences</div><div class="val">{fmv(r.get('AGENCE',float('nan')),'int')}</div></div>
    <div class="box"><div class="lbl">Effectif</div><div class="val">{fmv(r.get('EFFECTIF',float('nan')),'int')}</div></div>
  </div>
</div>
<div class="footer">Sources : Commission Bancaire UMOA · APBEF-Sénégal<br>Rapport · {bank} · {year}</div>
</body></html>"""

        return dict(content=html_content, filename=f"Rapport_Analytique_{bank}_{year}.html",
                    type="text/html"), f"✅ Rapport {bank} {year} téléchargé"
    except Exception as e:
        return no_update, f"❌ Erreur : {str(e)[:80]}"


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACK 3 — KPI Cards
# ═══════════════════════════════════════════════════════════════════════════
@callback(
    Output("bk-kpis","children"),
    Input("bk-bank","value"),
    Input("bk-year","value"),
)
def cb_kpis(bank, year):
    try:
        da = DF[DF["ANNEE"] == year]
        db = da[da["Sigle"] == bank]
        if db.empty: return html.P("Données insuffisantes.", style={"color":C_MUTED})
        r  = db.iloc[0]
        nb = da["Sigle"].nunique()

        def fmt(v, mode="M"):
            if pd.isna(v): return "N/A"
            if mode=="M":  return f"{v/1000:,.1f} Mds" if v>=1000 else f"{v:,.0f} M"
            if mode=="%":  return f"{v:.1f}%"
            return str(int(v))

        def rank(col):
            try:
                lst = da.dropna(subset=[col]).sort_values(col,ascending=False)["Sigle"].tolist()
                return f"#{lst.index(bank)+1}/{nb}" if bank in lst else "N/A"
            except: return "N/A"

        db_all = DF[DF["Sigle"]==bank].sort_values("ANNEE")
        v0 = db_all[db_all["ANNEE"]==2015]["BILAN"].values
        v1 = db_all[db_all["ANNEE"]==2020]["BILAN"].values
        tcam_str = f"+{((v1[0]/v0[0])**(1/5)-1)*100:.1f}%" if (len(v0) and len(v1) and v0[0]>0) else "N/A"

        items = [
            ("Bilan",          fmt(r["BILAN"]),                      rank("BILAN"),        C_BLUE,  "💰"),
            ("Part de Marché", fmt(r.get("PART_MARCHE",np.nan),"%"), "du marché total",    C_BLUE,  "📊"),
            ("TCAM 15→20",     tcam_str,                             "croissance bilan",   C_GREEN, "📈"),
            ("Fonds Propres",  fmt(r["FONDS.PROPRE"]),               rank("FONDS.PROPRE"), C_GOLD,  "🛡️"),
            ("Emplois",        fmt(r["EMPLOI"]),                     rank("EMPLOI"),       C_BLUE,  "💼"),
            ("Ressources",     fmt(r["RESSOURCES"]),                  rank("RESSOURCES"),  C_BLUE,  "🏦"),
            ("Nb Comptes",     fmt(r.get("COMPTE",np.nan),"int"),    rank("COMPTE"),       C_GOLD,  "👥"),
            ("Agences",        fmt(r.get("AGENCE",np.nan),"int"),    "réseau physique",    C_MUTED, "📍"),
        ]
        return dbc.Row([
            dbc.Col(kpi_card(t,v,s,c,i), xs=6, sm=4, md=3, lg=3, xl=2, className="mb-2 ps-1 pe-1")
            for t,v,s,c,i in items
        ], className="g-2")
    except Exception as e:
        return html.P(f"Erreur KPI : {e}", style={"color":C_RED})


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACK 4 — Contenu Tabs
# ═══════════════════════════════════════════════════════════════════════════
@callback(
    Output("bk-content","children"),
    Input("bk-tabs","value"),
    Input("bk-bank","value"),
    Input("bk-year","value"),
    Input("bk-group","value"),
    Input("bk-kpi","value"),
    Input("bk-compare","value"),
)
def cb_tabs(tab, bank, year, group, kpi, compare):
    try:
        compare = compare or []
        da      = DF[DF["ANNEE"] == year].copy()
        if group != "Tous":
            da  = da[da["Goupe_Bancaire"] == group]
        kpi_lbl = next((o["label"] for o in KPI_OPTS if o["value"]==kpi), kpi)

        # ── VUE MARCHÉ ────────────────────────────────────────────────────
        if tab == "marche":
            ds     = da.dropna(subset=[kpi]).sort_values(kpi, ascending=True)
            colors = [C_GOLD if s==bank else C_BLUE for s in ds["Sigle"]]
            fig_rank = go.Figure(go.Bar(
                x=ds[kpi], y=ds["Sigle"], orientation="h", marker_color=colors,
                text=[f"{v:,.0f}" for v in ds[kpi]], textposition="outside",
                hovertemplate="<b>%{y}</b><br>%{x:,.0f} M FCFA<extra></extra>",
            ))
            fig_rank.update_layout(**BASE_LAYOUT,
                title=dict(text=f"Classement — {kpi_lbl} · {year}",font=dict(size=13,color=C_DARK)),
                height=620, showlegend=False, xaxis=AX_CLEAN, yaxis=AY_CLEAN,
            )
            dg = da.groupby("Goupe_Bancaire")[kpi].sum().reset_index()
            fig_pie = px.pie(dg, values=kpi, names="Goupe_Bancaire", hole=0.45,
                             color_discrete_sequence=[C_BLUE,C_GOLD,"#1a8a5a","#9b59b6"])
            fig_pie.update_layout(**BASE_LAYOUT,
                title=dict(text="Parts par groupe",font=dict(size=12)),
                height=300, legend=dict(orientation="v",x=1,y=0.5))
            fig_pie.update_traces(textinfo="percent+label", textfont_size=10)

            def mini_tbl(data, titre, col_c):
                rows = [html.Tr([
                    html.Td(r["Sigle"], style={"fontWeight":"700" if r["Sigle"]==bank else "400",
                                               "color":C_GOLD if r["Sigle"]==bank else C_DARK}),
                    html.Td(f"{r[kpi]:,.0f} M", style={"textAlign":"right","fontSize":"0.83rem"}),
                    html.Td(r["Goupe_Bancaire"], style={"fontSize":"0.7rem","color":C_MUTED}),
                ], style={"background":C_GOLD_PALE if r["Sigle"]==bank else "white"})
                for _,r in data.iterrows()]
                return html.Div([
                    html.Div(titre, style={"fontSize":"0.68rem","textTransform":"uppercase","fontWeight":"700",
                                           "color":col_c,"marginBottom":"0.4rem","paddingLeft":"0.5rem",
                                           "borderLeft":f"3px solid {col_c}"}),
                    html.Table([
                        html.Thead(html.Tr([html.Th("Banque"),html.Th("Valeur",style={"textAlign":"right"}),html.Th("Groupe")])),
                        html.Tbody(rows),
                    ], style={"width":"100%","borderCollapse":"collapse","fontSize":"0.82rem"}),
                ], style={"background":"white","borderRadius":"8px","padding":"0.9rem","boxShadow":"0 2px 8px rgba(0,0,0,0.06)"})

            top5 = da.dropna(subset=[kpi]).nlargest(5,kpi)
            bot5 = da.dropna(subset=[kpi]).nsmallest(5,kpi)
            return html.Div([dbc.Row([
                dbc.Col(card([section_hdr(f"Classement {year}",f"Indicateur : {kpi_lbl}"),
                               dcc.Graph(figure=fig_rank,config={"displayModeBar":False})]),md=7,className="mb-3"),
                dbc.Col([card([section_hdr("Répartition par groupe"),
                               dcc.Graph(figure=fig_pie,config={"displayModeBar":False})]),
                         dbc.Row([dbc.Col(mini_tbl(top5," Top 5",C_GREEN),xs=12,lg=6,className="mb-2"),
                                  dbc.Col(mini_tbl(bot5," Bottom 5",C_RED),xs=12,lg=6,className="mb-2")])
                        ],md=5,className="mb-3"),
            ])])

        # ── POSITIONNEMENT ────────────────────────────────────────────────
        elif tab == "position":
            d20 = DF[DF["ANNEE"]==2020].copy()
            if group != "Tous": d20 = d20[d20["Goupe_Bancaire"]==group]

            def scatter(col, titre):
                tot = d20[col].sum()
                if tot == 0: return empty_fig(f"Données {col} insuffisantes")
                fig = go.Figure()
                oth = d20[~d20["Sigle"].isin([bank]+compare)].dropna(subset=[col,"TCAM_BILAN"])
                if not oth.empty:
                    fig.add_trace(go.Scatter(x=(oth[col]/tot*100), y=oth["TCAM_BILAN"],
                        mode="markers+text", name="Marché", text=oth["Sigle"], textposition="top center",
                        textfont=dict(size=8,color=C_MUTED), marker=dict(size=8,color=C_BLUE,opacity=0.55)))
                cmp = d20[d20["Sigle"].isin(compare)].dropna(subset=[col,"TCAM_BILAN"])
                if not cmp.empty:
                    fig.add_trace(go.Scatter(x=(cmp[col]/tot*100), y=cmp["TCAM_BILAN"],
                        mode="markers+text", name="Comparées", text=cmp["Sigle"], textposition="top center",
                        textfont=dict(size=9,color=C_GREEN,family="Arial Black"),
                        marker=dict(size=13,color=C_GREEN,opacity=0.85,line=dict(width=2,color="white"))))
                tgt = d20[d20["Sigle"]==bank].dropna(subset=[col,"TCAM_BILAN"])
                if not tgt.empty:
                    fig.add_trace(go.Scatter(x=(tgt[col]/tot*100), y=tgt["TCAM_BILAN"],
                        mode="markers+text", name=bank, text=[bank], textposition="top center",
                        textfont=dict(size=11,color=C_GOLD,family="Arial Black"),
                        marker=dict(size=22,color=C_GOLD,symbol="star",line=dict(width=2,color="white"))))
                all_x = d20.dropna(subset=[col])[col]/tot*100
                all_y = d20["TCAM_BILAN"].dropna()
                if len(all_x): fig.add_vline(x=all_x.median(),line_dash="dot",line_color="#e0e0e0",line_width=1)
                if len(all_y): fig.add_hline(y=all_y.median(),line_dash="dot",line_color="#e0e0e0",line_width=1)
                fig.update_layout(**BASE_LAYOUT,
                    title=dict(text=titre,font=dict(size=12,color=C_DARK)),
                    xaxis_title="Part de Marché (%)", yaxis_title="TCAM 2015–2020 (%)", height=360)
                return fig

            figs = [scatter("BILAN","Total Bilan"), scatter("EMPLOI","Emplois"),
                    scatter("RESSOURCES","Ressources"), scatter("COMPTE","Nb Comptes")]
            return html.Div([
                section_hdr("Matrice de Positionnement",f"Part de marché vs croissance — {bank} ★"),
                dbc.Row([dbc.Col(card([dcc.Graph(figure=f,config={"displayModeBar":False})],mb=False),
                                 md=6,className="mb-3") for f in figs])
            ])

        # ── ÉVOLUTION ─────────────────────────────────────────────────────
        elif tab == "evolution":
            all_b = [bank] + compare
            pal   = [C_GOLD,C_BLUE,C_GREEN,"#9b59b6","#e74c3c","#3498db"]
            cmap  = {b:pal[i%len(pal)] for i,b in enumerate(all_b)}

            def line_chart(col, titre):
                fig = go.Figure()
                for b in all_b:
                    db_ = DF[DF["Sigle"]==b].sort_values("ANNEE")
                    if not db_[col].notna().any(): continue
                    is_t = b==bank
                    fig.add_trace(go.Scatter(x=db_["ANNEE"], y=db_[col], name=b, mode="lines+markers",
                        line=dict(width=3 if is_t else 1.8,color=cmap.get(b,C_BLUE),dash="solid" if is_t else "dot"),
                        marker=dict(size=9 if is_t else 6,symbol="star" if is_t else "circle"),
                        hovertemplate=f"<b>{b}</b> · %{{x}}: %{{y:,.0f}} M<extra></extra>"))
                if not fig.data: return empty_fig(f"Aucune donnée pour {col}")
                fig.update_layout(**BASE_LAYOUT,
                    title=dict(text=titre,font=dict(size=12,color=C_DARK)),
                    xaxis=dict(tickvals=YEARS,ticktext=[str(y) for y in YEARS],showgrid=False,linecolor="#dddddd"),
                    yaxis=AY_GRID, height=300)
                return fig

            pairs = [("BILAN","Évolution du Bilan"),("EMPLOI","Évolution des Emplois"),
                     ("RESSOURCES","Évolution des Ressources"),("FONDS.PROPRE","Évolution des Fonds Propres"),
                     ("RESULTAT.NET","Évolution du Résultat Net"),("PRODUIT.NET.BANCAIRE","Évolution du PNB")]
            rows = []
            for i in range(0,len(pairs),2):
                rows.append(dbc.Row([dbc.Col(card([dcc.Graph(figure=line_chart(c,t),
                    config={"displayModeBar":False})],mb=False),md=6,className="mb-3") for c,t in pairs[i:i+2]]))
            return html.Div([section_hdr("Trajectoires 2015–2020",f"{bank} (★) vs sélection"), *rows])

        # ── RATIOS FINANCIERS ─────────────────────────────────────────────
        elif tab == "ratios":
            dr_year = year if year in YEARS_FIN else YEAR_FIN_DEFAULT
            dr = DF[DF["ANNEE"]==dr_year].copy()
            if group != "Tous": dr = dr[dr["Goupe_Bancaire"]==group]
            note = f"  Ratios non disponibles pour {year}. Affichage sur {dr_year}." if dr_year!=year else ""

            def ratio_bar(col, titre, pct=True, inv=False):
                ds_ = dr.dropna(subset=[col])
                if ds_.empty: return empty_fig(f"Pas de données {col}")
                ds_ = ds_.sort_values(col, ascending=not inv)
                suffix = "%" if pct else "x"
                fig = go.Figure(go.Bar(x=ds_[col], y=ds_["Sigle"], orientation="h",
                    marker_color=[C_GOLD if s==bank else C_BLUE for s in ds_["Sigle"]],
                    text=[f"{v:.1f}{suffix}" for v in ds_[col]], textposition="outside",
                    hovertemplate=f"<b>%{{y}}</b><br>{titre}: %{{x:.2f}}{suffix}<extra></extra>"))
                med = ds_[col].median()
                fig.add_vline(x=med, line_dash="dash", line_color=C_GOLD,
                              annotation_text=f"Méd: {med:.1f}{suffix}",
                              annotation_font_size=8, annotation_font_color=C_GOLD)
                fig.update_layout(**BASE_LAYOUT,
                    title=dict(text=f"{titre} — {dr_year}",font=dict(size=12,color=C_DARK)),
                    height=500, showlegend=False, xaxis=AX_CLEAN,
                    yaxis=dict(tickfont=dict(size=8),linecolor="#dddddd"))
                return fig

            # Radar normalisé
            radar_def = {"ROE":("Rentabilité ROE",True),"ROA":("Rendement ROA",True),
                         "PART_MARCHE":("Part de Marché",True),"RISQUE_PCT":("Maîtrise Risque",False),
                         "LEVIER":("Levier Financier",False),"RATIO_TRANSF":("Tx Transformation",True)}
            row_b = dr[dr["Sigle"]==bank]
            lbls, vals_b, vals_m = [], [], []
            def norm_v(v, all_v, higher):
                mn,mx = np.nanmin(all_v),np.nanmax(all_v)
                if mx==mn: return 50.0
                n = (v-mn)/(mx-mn)*100
                return n if higher else 100-n
            if not row_b.empty:
                rb = row_b.iloc[0]
                for col,(lbl,higher) in radar_def.items():
                    all_v = dr[col].dropna().values
                    if not len(all_v): continue
                    v_b = rb.get(col,np.nan); v_m = dr[col].mean()
                    if pd.isna(v_b) or pd.isna(v_m): continue
                    lbls.append(lbl); vals_b.append(norm_v(v_b,all_v,higher)); vals_m.append(norm_v(v_m,all_v,higher))
            fig_radar = go.Figure()
            if lbls:
                fig_radar.add_trace(go.Scatterpolar(r=vals_b+[vals_b[0]],theta=lbls+[lbls[0]],fill="toself",
                    name=bank,line=dict(color=C_GOLD,width=2.5),fillcolor="rgba(232,160,32,0.12)"))
                fig_radar.add_trace(go.Scatterpolar(r=vals_m+[vals_m[0]],theta=lbls+[lbls[0]],fill="toself",
                    name=f"Moy. Marché {dr_year}",line=dict(color=C_BLUE,width=1.5,dash="dot"),
                    fillcolor="rgba(0,74,153,0.07)"))
            else:
                fig_radar.add_annotation(text="Données insuffisantes",xref="paper",yref="paper",
                    x=0.5,y=0.5,showarrow=False,font=dict(size=13,color=C_MUTED))
            fig_radar.update_layout(**BASE_LAYOUT,
                polar=dict(radialaxis=dict(visible=True,range=[0,100],tickfont=dict(size=7))),
                title=dict(text=f"Profil — {bank} vs Marché ({dr_year})",font=dict(size=12)),
                height=360, legend=dict(orientation="h",y=-0.12))

            return html.Div([
                html.Div(note,style={"background":"#fff8e6","borderLeft":f"4px solid {C_GOLD}",
                    "padding":"0.6rem 1rem","borderRadius":"4px","fontSize":"0.82rem",
                    "color":"#7a5500","marginBottom":"1rem"}) if note else None,
                section_hdr(f"Ratios Financiers — {dr_year}",f"{bank} en surbrillance ★"),
                dbc.Row([
                    dbc.Col(card([section_hdr("Profil Radar","Score normalisé 0–100"),
                                   dcc.Graph(figure=fig_radar,config={"displayModeBar":False})]),md=4,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=ratio_bar("ROE","ROE (%)"),config={"displayModeBar":False})]),md=4,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=ratio_bar("RISQUE_PCT","Coût du Risque (%)",inv=True),config={"displayModeBar":False})]),md=4,className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(card([dcc.Graph(figure=ratio_bar("LEVIER","Levier (x)",pct=False,inv=True),config={"displayModeBar":False})]),md=4,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=ratio_bar("ROA","ROA (%)"),config={"displayModeBar":False})]),md=4,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=ratio_bar("RATIO_TRANSF","Taux de Transformation (%)"),config={"displayModeBar":False})]),md=4,className="mb-3"),
                ]),
            ])

        # ── PRODUCTIVITÉ ──────────────────────────────────────────────────
        elif tab == "productivite":
            dp = DF[DF["ANNEE"]==year].copy()
            if group != "Tous": dp = dp[dp["Goupe_Bancaire"]==group]

            def prod_bar(col, titre):
                ds_ = dp.dropna(subset=[col]).sort_values(col, ascending=True)
                if ds_.empty: return empty_fig(f"Pas de données {col}")
                fig = go.Figure(go.Bar(x=ds_[col], y=ds_["Sigle"], orientation="h",
                    marker_color=[C_GOLD if s==bank else C_BLUE for s in ds_["Sigle"]],
                    text=[f"{v:,.0f}" for v in ds_[col]], textposition="outside"))
                med = ds_[col].median()
                fig.add_vline(x=med, line_dash="dash", line_color=C_GOLD,
                              annotation_text=f"Méd: {med:,.0f}",
                              annotation_font_size=8, annotation_font_color=C_GOLD)
                fig.update_layout(**BASE_LAYOUT,
                    title=dict(text=titre,font=dict(size=12,color=C_DARK)),
                    height=480, showlegend=False, xaxis=AX_CLEAN,
                    yaxis=dict(tickfont=dict(size=8),linecolor="#dddddd"))
                return fig

            dbub = dp.dropna(subset=["EMP_EFF","PART_MARCHE","BILAN"]).copy()
            fig_bub = go.Figure()
            if not dbub.empty:
                max_b = dbub["BILAN"].max()
                for _,r in dbub.iterrows():
                    b=r["Sigle"]; is_t=b==bank; is_c=b in compare
                    fig_bub.add_trace(go.Scatter(x=[r["PART_MARCHE"]], y=[r["EMP_EFF"]],
                        mode="markers+text", text=[b], textposition="top center", showlegend=False,
                        textfont=dict(size=11 if is_t else 8,
                                      color=C_GOLD if is_t else (C_GREEN if is_c else C_MUTED)),
                        marker=dict(size=max(8,r["BILAN"]/max_b*55),
                                    color=C_GOLD if is_t else (C_GREEN if is_c else C_BLUE),
                                    opacity=1.0 if is_t else 0.6,
                                    line=dict(width=2 if is_t else 0,color="white")),
                        hovertemplate=(f"<b>{b}</b><br>PDM: {r['PART_MARCHE']:.1f}%<br>"
                                       f"Emplois/Agent: {r['EMP_EFF']:,.0f} M<br>"
                                       f"Bilan: {r['BILAN']:,.0f} M<extra></extra>")))
            fig_bub.update_layout(**BASE_LAYOUT,
                title=dict(text="Productivité / Agent vs Part de Marché (bulle ∝ bilan)",font=dict(size=12,color=C_DARK)),
                xaxis_title="Part de Marché (%)", yaxis_title="Emplois / Agent (M FCFA)",
                height=380, showlegend=False)

            return html.Div([
                section_hdr("Productivité Commerciale",f"Efficacité réseau & agents — {year}"),
                dbc.Row([dbc.Col(card([dcc.Graph(figure=fig_bub,config={"displayModeBar":False})]),md=12,className="mb-3")]),
                dbc.Row([
                    dbc.Col(card([dcc.Graph(figure=prod_bar("EMP_AG","Emplois / Agence (M FCFA)"),config={"displayModeBar":False})]),md=6,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=prod_bar("RES_AG","Ressources / Agence (M FCFA)"),config={"displayModeBar":False})]),md=6,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=prod_bar("EMP_EFF","Emplois / Agent (M FCFA)"),config={"displayModeBar":False})]),md=6,className="mb-3"),
                    dbc.Col(card([dcc.Graph(figure=prod_bar("RES_EFF","Ressources / Agent (M FCFA)"),config={"displayModeBar":False})]),md=6,className="mb-3"),
                ]),
            ])


        # ── CARTE ────────────────────────────────────────────────────────
        elif tab == "carte":
            # Coordonnées des sièges sociaux à Dakar (légèrement décalées pour visibilité)
            BANK_HQ = {
                "BGFI":    (14.6888, -17.4488), "CBAO":    (14.6952, -17.4401),
                "SGBS":    (14.6831, -17.4536), "BICIS":   (14.6905, -17.4455),
                "ECOBANK": (14.6970, -17.4470), "BOA":     (14.6860, -17.4420),
                "BHS":     (14.6920, -17.4380), "BNDE":    (14.6940, -17.4510),
                "ATB":     (14.6875, -17.4395), "CIB":     (14.6998, -17.4435),
                "BRM":     (14.6845, -17.4475), "CNCAS":   (14.6930, -17.4365),
                "BSIC":    (14.6810, -17.4450), "ORABANK": (14.6960, -17.4490),
                "UBA":     (14.6895, -17.4415), "CITIBANK":(14.6985, -17.4460),
                "BICICI":  (14.6850, -17.4350), "NSIA":    (14.6915, -17.4525),
                "SIB":     (14.6870, -17.4480), "VISTA":   (14.6940, -17.4430),
                "LCB":     (14.6905, -17.4500), "CORIS":   (14.6925, -17.4445),
                "AGF":     (14.6840, -17.4465), "BICI":    (14.6980, -17.4415),
            }
            # Années avec slider
            dp_all = DF.copy()
            dp_year = dp_all[dp_all["ANNEE"] == year].copy()

            map_rows = []
            for _, r in dp_year.iterrows():
                sigle = r["Sigle"]
                key = sigle.upper().replace(" ","").replace("-","")
                # Chercher la clé la plus proche
                match = next((k for k in BANK_HQ if k in key or key in k), None)
                lat, lon = BANK_HQ.get(match, (14.6937 + np.random.uniform(-0.02,0.02),
                                                -17.4467 + np.random.uniform(-0.02,0.02)))
                map_rows.append({
                    "Sigle": sigle, "lat": lat, "lon": lon,
                    "Agences":      max(1, r.get("AGENCE",    1) or 1),
                    "Bilan":        r.get("BILAN",       0) or 0,
                    "Part_Marche":  round(r.get("PART_MARCHE", 0) or 0, 2),
                    "Emplois":      r.get("EMPLOI",      0) or 0,
                    "Groupe":       r.get("Goupe_Bancaire","—"),
                    "Resultat_Net": r.get("RESULTAT.NET", 0) or 0,
                    "ROE":          round(r.get("ROE", 0) or 0, 1),
                    "TCAM":         round(r.get("TCAM_BILAN", 0) or 0, 1),
                })
            map_df = pd.DataFrame(map_rows)
            if map_df.empty:
                return empty_fig("Pas de données cartographiques pour cette sélection")

            # Couleurs par groupe
            grp_colors = {"Continentaux":C_BLUE,"Régionaux":C_GOLD,"Internationaux":C_GREEN,"Locaux":"#9b59b6"}
            map_df["color"] = map_df["Groupe"].map(grp_colors).fillna(C_MUTED)

            fig_map = go.Figure()
            for grp in map_df["Groupe"].unique():
                sub = map_df[(map_df["Groupe"]==grp) & (map_df["Sigle"]!=bank)]
                if not sub.empty:
                    fig_map.add_trace(go.Scattermapbox(
                        lat=sub["lat"], lon=sub["lon"],
                        mode="markers+text",
                        name=grp,
                        text=sub["Sigle"],
                        textposition="top right",
                        textfont=dict(size=9, color="white"),
                        marker=dict(
                            size=[max(12, a/2) for a in sub["Agences"]],
                            color=grp_colors.get(grp, C_MUTED),
                            opacity=0.85,
                        ),
                        customdata=sub[["Bilan","Part_Marche","Agences","Emplois","ROE","TCAM","Resultat_Net"]].values,
                        hovertemplate=(
                            "<b>%{text}</b><br>"
                            "Groupe : " + grp + "<br>"
                            "Bilan : %{customdata[0]:,.0f} M FCFA<br>"
                            "Part de Marché : %{customdata[1]:.2f}%<br>"
                            "Agences : %{customdata[2]:.0f}<br>"
                            "Emplois : %{customdata[3]:,.0f} M FCFA<br>"
                            "ROE : %{customdata[4]:.1f}%<br>"
                            "TCAM : %{customdata[5]:.1f}%<br>"
                            "<extra></extra>"
                        ),
                    ))
            # Trace séparée pour la banque cible (or, plus grande)
            tgt = map_df[map_df["Sigle"]==bank]
            if not tgt.empty:
                fig_map.add_trace(go.Scattermapbox(
                    lat=tgt["lat"], lon=tgt["lon"],
                    mode="markers+text",
                    name=bank,
                    text=tgt["Sigle"],
                    textposition="top right",
                    textfont=dict(size=13, color=C_GOLD),
                    marker=dict(
                        size=[max(20, a/2) for a in tgt["Agences"]],
                        color=C_GOLD,
                        opacity=1.0,
                        symbol="star",
                    ),
                    customdata=tgt[["Bilan","Part_Marche","Agences","Emplois","ROE","TCAM","Resultat_Net"]].values,
                    hovertemplate=(
                        "<b>%{text} ★</b><br>"
                        "Bilan : %{customdata[0]:,.0f} M FCFA<br>"
                        "Part de Marché : %{customdata[1]:.2f}%<br>"
                        "Agences : %{customdata[2]:.0f}<br>"
                        "Emplois : %{customdata[3]:,.0f} M FCFA<br>"
                        "ROE : %{customdata[4]:.1f}%<br>"
                        "TCAM : %{customdata[5]:.1f}%<br>"
                        "<extra></extra>"
                    ),
                ))

            fig_map.update_layout(
                mapbox=dict(style="open-street-map", zoom=10,
                            center=dict(lat=14.693, lon=-17.447)),
                margin=dict(t=0,b=0,l=0,r=0),
                height=560,
                legend=dict(bgcolor="rgba(255,255,255,0.85)",
                             bordercolor="#dddddd",borderwidth=1,
                             x=0.01,y=0.99,xanchor="left",yanchor="top"),
                paper_bgcolor="white",
            )

            # Évolution temporelle : courbe AGENCE total par année
            evo = DF.groupby("ANNEE")["AGENCE"].sum().reset_index()
            bank_evo = DF[DF["Sigle"]==bank][["ANNEE","AGENCE","PART_MARCHE"]].sort_values("ANNEE")
            fig_evo = go.Figure()
            fig_evo.add_trace(go.Scatter(
                x=evo["ANNEE"], y=evo["AGENCE"],
                name="Total marché", mode="lines+markers",
                line=dict(color=C_BLUE, width=2),
                yaxis="y",
            ))
            fig_evo.add_trace(go.Scatter(
                x=bank_evo["ANNEE"], y=bank_evo["AGENCE"],
                name=f"{bank} — Agences", mode="lines+markers",
                line=dict(color=C_GOLD, width=3),
                marker=dict(size=9, symbol="star"),
                yaxis="y",
            ))
            fig_evo.add_trace(go.Scatter(
                x=bank_evo["ANNEE"], y=bank_evo["PART_MARCHE"],
                name=f"{bank} — Part de marché (%)", mode="lines+markers",
                line=dict(color=C_GREEN, width=2, dash="dot"),
                marker=dict(size=7),
                yaxis="y2",
            ))
            evo_layout = BASE_SLIM
            fig_evo.update_layout(**evo_layout,
                title=dict(text=f"Évolution réseau & part de marché 2015–2020 — {bank}",
                           font=dict(size=12,color=C_DARK)),
                height=280,
                yaxis=dict(title="Nb Agences", gridcolor="#f0f0f0"),
                yaxis2=dict(title="Part de Marché (%)", overlaying="y", side="right",
                             showgrid=False, tickfont=dict(color=C_GREEN)),
                legend=dict(orientation="h",y=-0.18),
            )

            # KPI tableau réseau
            dp_b = dp_year[dp_year["Sigle"]==bank]
            kpi_net = []
            if not dp_b.empty:
                rb = dp_b.iloc[0]
                med = dp_year["AGENCE"].median()
                kpi_net = [
                    ("Nb Agences",         f"{int(rb.get('AGENCE',0) or 0)}",  f"Méd. marché : {med:.0f}", C_BLUE,  "📍"),
                    ("Emplois / Agence",   f"{rb.get('EMP_AG',0) or 0:,.0f} M", rank_str("EMP_AG", bank, dp_year, dp_year['Sigle'].nunique()), C_GOLD, "🏪"),
                    ("Ressources / Agence",f"{rb.get('RES_AG',0) or 0:,.0f} M", rank_str("RES_AG", bank, dp_year, dp_year['Sigle'].nunique()), C_GREEN,"💳"),
                ]

            return html.Div([
                section_hdr(f"Carte du Réseau Bancaire — Sénégal {year}",
                             f"{bank} ★ en surbrillance · Bulle ∝ Nb Agences"),
                dbc.Row([
                    dbc.Col(card([dcc.Graph(figure=fig_map, config={"displayModeBar":False})],mb=False),
                            md=8, className="mb-3"),
                    dbc.Col([
                        card([section_hdr("Réseau physique","Indicateurs clés"),
                              dbc.Row([
                                  dbc.Col(kpi_card(t,v,s,c,i), xs=12, className="mb-2")
                                  for t,v,s,c,i in kpi_net
                              ] if kpi_net else [html.P("N/A")])
                        ]),
                        card([section_hdr("Classement par agences",f"Année {year}"),
                              dcc.Graph(figure=_agence_rank(dp_year, bank), config={"displayModeBar":False})
                        ], mb=False),
                    ], md=4, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(card([dcc.Graph(figure=fig_evo, config={"displayModeBar":False})]),
                            md=12),
                ]),
            ])

        return html.P("Sélectionnez un onglet.", style={"color":C_MUTED,"padding":"2rem"})

    except Exception as e:
        import traceback
        return html.Div([
            html.P(f"❌ Erreur tab '{tab}' : {str(e)}",
                   style={"color":C_RED,"fontWeight":"700","marginBottom":"0.5rem"}),
            html.Pre(traceback.format_exc(),
                     style={"fontSize":"0.72rem","color":C_MUTED,"background":"#f8f8f8",
                            "padding":"1rem","borderRadius":"6px","overflow":"auto"}),
        ], style={"padding":"1.5rem","background":"white","borderRadius":"10px","borderLeft":f"4px solid {C_RED}"})