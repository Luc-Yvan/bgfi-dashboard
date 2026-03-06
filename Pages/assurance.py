import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

dash.register_page(__name__, path='/assurance')

# --- CHARGEMENT ---
file_path = os.path.join(os.getcwd(), 'Data', 'assurance_data_1000.csv')
try:
    # Lecture avec point-virgule comme séparateur (vu dans ton fichier)
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
except Exception as e:
    print(f"Erreur assurance: {e}")
    df = pd.DataFrame()

# --- LAYOUT ---
layout = dbc.Container([
    html.H2("🛡️ Dashboard Assurance", className="my-4 text-primary"),

    # Filtre Type Assurance
    dbc.Row([
        dbc.Col(html.Label("Filtrer par Type :"), width=2, className="mt-2"),
        dbc.Col(dcc.Dropdown(
            id='type-filter',
            options=[{'label': t, 'value': t} for t in sorted(df['type_assurance'].unique())] if not df.empty else [],
            value=None,
            placeholder="Tous les types",
            clearable=True
        ), width=4)
    ], className="mb-4"),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Chiffre d'Affaires (Primes)"),
            dbc.CardBody(html.H3(id="kpi-primes", className="text-success"))
        ], color="light"), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Sinistres Payés"),
            dbc.CardBody(html.H3(id="kpi-sinistres", className="text-danger"))
        ], color="light"), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Rentabilité (S/P)"),
            dbc.CardBody(html.H3(id="kpi-ratio", className="text-info"))
        ], color="light"), width=4),
    ], className="mb-4"),

    # Graphiques
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-region"), width=6),
        dbc.Col(dcc.Graph(id="graph-repartition"), width=6),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-age-sinistre"), width=12),
    ], className="mt-4")
])

# --- CALLBACKS ---
@callback(
    [Output("kpi-primes", "children"),
     Output("kpi-sinistres", "children"),
     Output("kpi-ratio", "children"),
     Output("graph-region", "figure"),
     Output("graph-repartition", "figure"),
     Output("graph-age-sinistre", "figure")],
    Input("type-filter", "value")
)
def update_assurance(type_selected):
    if df.empty: return "0", "0", "0%", {}, {}, {}
    
    # Filtrage
    dff = df.copy()
    if type_selected:
        dff = dff[dff['type_assurance'] == type_selected]

    # Calculs KPI
    total_primes = dff['montant_prime'].sum()
    total_sinistres = dff['montant_sinistres'].sum()
    ratio = (total_sinistres / total_primes * 100) if total_primes > 0 else 0

    # Graph 1 : Primes par Région (Barres)
    fig_region = px.bar(
        dff.groupby("region")["montant_prime"].sum().reset_index().sort_values("montant_prime"),
        x="montant_prime", y="region", orientation='h',
        title="Montant des Primes par Région",
        color="montant_prime", color_continuous_scale="Viridis"
    )

    # Graph 2 : Répartition Types ou Sexes (Pie)
    if type_selected:
        # Si un type est choisi, on regarde la répartition Homme/Femme
        fig_repart = px.pie(dff, names='sexe', values='montant_prime', title=f"Répartition H/F ({type_selected})")
    else:
        # Sinon répartition par Type d'assurance
        fig_repart = px.pie(dff, names='type_assurance', values='montant_prime', title="Répartition par Type d'Assurance")

    # Graph 3 : Scatter Age vs Sinistres
    fig_scatter = px.scatter(
        dff, x="age", y="montant_sinistres", color="type_assurance",
        size="nb_sinistres", hover_data=['duree_contrat'],
        title="Corrélation : Âge vs Montant des Sinistres"
    )

    return f"{total_primes:,.0f} €", f"{total_sinistres:,.0f} €", f"{ratio:.1f} %", fig_region, fig_repart, fig_scatter