import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = dbc.Container([
    html.H1("Portail de Visualisation Données Sénégal", className="text-center my-5"),
    dbc.Row([
        dbc.Col(dbc.Button("Accéder au Secteur Bancaire", href="/banque", color="primary", size="lg", className="w-100"), width=4),
        dbc.Col(dbc.Button("Secteur Assurance (Bientôt)", href="/assurance", color="secondary", size="lg", className="w-100 disabled"), width=4),
        dbc.Col(dbc.Button("Secteur Énergie (Bientôt)", href="/energie", color="secondary", size="lg", className="w-100 disabled"), width=4),
    ], className="mt-5")
])