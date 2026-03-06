import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

dash.register_page(__name__, path='/energie')

# --- CHARGEMENT ---
file_path = os.path.join(os.getcwd(), 'Data', 'salar_data.csv')
try:
    # Lecture avec point-virgule
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    # Conversion Date
    df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True, errors='coerce')
except Exception as e:
    print(f"Erreur energie: {e}")
    df = pd.DataFrame()

# --- LAYOUT ---
layout = dbc.Container([
    html.H2("⚡ Dashboard Énergie (Solaire)", className="my-4 text-warning"),

    # Filtre Pays
    dbc.Row([
        dbc.Col(html.Label("Pays :"), width=1, className="mt-2"),
        dbc.Col(dcc.Dropdown(
            id='country-filter',
            options=[{'label': c, 'value': c} for c in df['Country'].unique()] if not df.empty else [],
            value=df['Country'].unique()[0] if not df.empty else None,
            clearable=False
        ), width=3)
    ], className="mb-4"),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Production Totale (AC)"),
            dbc.CardBody(html.H3(id="kpi-ac-power", className="text-warning"))
        ], inverse=True, style={"backgroundColor": "#34495e"}), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Irradiation Moyenne"),
            dbc.CardBody(html.H3(id="kpi-irr", className="text-white"))
        ], inverse=True, style={"backgroundColor": "#f39c12"}), width=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Température Max Module"),
            dbc.CardBody(html.H3(id="kpi-temp", className="text-white"))
        ], inverse=True, style={"backgroundColor": "#c0392b"}), width=4),
    ], className="mb-4"),

    # Graphiques
    dcc.Graph(id="graph-production-time"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-yield-daily"), width=6),
        dbc.Col(dcc.Graph(id="graph-temp-scatter"), width=6),
    ], className="mt-4")
])

# --- CALLBACKS ---
@callback(
    [Output("kpi-ac-power", "children"),
     Output("kpi-irr", "children"),
     Output("kpi-temp", "children"),
     Output("graph-production-time", "figure"),
     Output("graph-yield-daily", "figure"),
     Output("graph-temp-scatter", "figure")],
    Input("country-filter", "value")
)
def update_energie(country):
    if df.empty or not country: return "0", "0", "0", {}, {}, {}

    dff = df[df['Country'] == country]

    # KPIs
    total_ac = dff['AC_Power'].sum()
    avg_irr = dff['Irradiation'].mean()
    max_temp = dff['Module_Temperature'].max()

    # Graph 1 : Production AC dans le temps (Line)
    # On agrège par heure pour alléger le graph
    df_time = dff.groupby('DateTime')['AC_Power'].mean().reset_index()
    fig_prod = px.line(df_time, x='DateTime', y='AC_Power', 
                       title=f"Production Électrique (AC Power) - {country}",
                       labels={'AC_Power': 'Puissance (W)'})
    fig_prod.update_traces(line_color='#f1c40f')

    # Graph 2 : Daily Yield par Mois (Bar)
    fig_yield = px.bar(dff.groupby('Month')['Daily_Yield'].sum().reset_index(), 
                       x='Month', y='Daily_Yield', 
                       title="Rendement Quotidien Cumulé par Mois",
                       color='Daily_Yield', color_continuous_scale='Solar')

    # Graph 3 : Température Ambiante vs Module (Scatter)
    fig_temp = px.scatter(dff, x='Ambient_Temperature', y='Module_Temperature', 
                          color='Irradiation',
                          title="Relation Température Ambiante / Module",
                          hover_data=['AC_Power'])

    return f"{total_ac:,.0f} W", f"{avg_irr:.3f}", f"{max_temp:.1f} °C", fig_prod, fig_yield, fig_temp