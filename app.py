import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import os

# ─── Initialisation ────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=[
        dbc.themes.LUX,
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap",
    ],
    suppress_callback_exceptions=True,
)
server = app.server

# ─── CSS Global injecté dans le <head> ────────────────────────────────────────
app.index_string = """
<!DOCTYPE html>
<html lang="fr">
<head>
    {%metas%}
    <title>Sénégal Data Monitor</title>
    {%favicon%}
    {%css%}
    <style>
    /* ══ Variables BGFI ══════════════════════════════════════════════ */
    :root {
        --blue:      #004a99;
        --blue-dark: #003070;
        --blue-mid:  #1a5fad;
        --gold:      #E8A020;
        --gold-light:#F5CF7E;
        --cream:     #f8f5ef;
        --dark:      #0d1b2e;
        --text:      #1a2940;
        --muted:     #6b7c96;
    }

    /* ══ Reset & Base ════════════════════════════════════════════════ */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--cream);
        color: var(--text);
        overflow-x: hidden;
    }
    

    /* ══ Navbar ══════════════════════════════════════════════════════ */
    .sdm-nav {
        background: var(--dark) !important;
        border-bottom: 3px solid var(--gold);
        padding: 0 2rem;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }
    .sdm-brand {
        font-family: 'Playfair Display', serif;
        font-size: 1.25rem;
        font-weight: 900;
        color: white !important;
        letter-spacing: 0.04em;
        text-decoration: none;
    }
    .sdm-brand span { color: var(--gold); }
    .sdm-navlink {
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.6rem 1.1rem !important;
        border-radius: 4px;
        transition: all 0.2s ease;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .sdm-navlink:hover, .sdm-navlink.active {
        color: white !important;
        background: rgba(232,160,32,0.15) !important;
        border-bottom: 2px solid var(--gold);
    }
    .sdm-icon { font-size: 0.9rem; opacity: 0.85; }

    /* ══ Hero ════════════════════════════════════════════════════════ */
    .sdm-hero {
        position: relative;
        min-height: 92vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        background: var(--dark);
    }
    /* Motif géométrique de fond */
    .sdm-hero::before {
        content: '';
        position: absolute; inset: 0;
        background-image:
            linear-gradient(135deg, rgba(0,74,153,0.55) 0%, rgba(13,27,46,0.9) 60%),
            repeating-linear-gradient(
                45deg,
                transparent,
                transparent 40px,
                rgba(232,160,32,0.04) 40px,
                rgba(232,160,32,0.04) 41px
            );
        z-index: 0;
    }
    /* Cercle décoratif grand */
    .sdm-hero::after {
        content: '';
        position: absolute;
        right: -180px; top: -180px;
        width: 700px; height: 700px;
        border-radius: 50%;
        border: 100px solid rgba(232,160,32,0.06);
        z-index: 0;
    }
    .sdm-hero-inner {
        position: relative;
        z-index: 1;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 3rem;
        width: 100%;
    }

    /* Pill pays */
    .sdm-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(232,160,32,0.12);
        border: 1px solid rgba(232,160,32,0.4);
        color: var(--gold-light);
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        padding: 0.38rem 0.9rem;
        border-radius: 50px;
        margin-bottom: 1.8rem;
        font-weight: 500;
    }
    .sdm-pill::before {
        content: '';
        width: 6px; height: 6px;
        background: var(--gold);
        border-radius: 50%;
        animation: pulse-dot 1.8s ease-in-out infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.4; transform: scale(1.4); }
    }

    /* Titre hero */
    .sdm-hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(3rem, 6vw, 5.5rem);
        font-weight: 900;
        line-height: 1.05;
        color: white;
        margin-bottom: 1.6rem;
    }
    .sdm-hero-title em {
        font-style: normal;
        color: var(--gold);
        position: relative;
    }
    .sdm-hero-title em::after {
        content: '';
        position: absolute;
        bottom: -4px; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, var(--gold), transparent);
    }

    /* Sous-titre */
    .sdm-hero-sub {
        color: rgba(255,255,255,0.6);
        font-size: 1.05rem;
        font-weight: 300;
        line-height: 1.7;
        max-width: 560px;
        margin-bottom: 2.8rem;
    }

    /* Boutons CTA */
    .sdm-cta-group { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 4.5rem; }
    .sdm-btn-primary {
        background: var(--gold);
        color: var(--dark);
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.85rem 2rem;
        border: none;
        border-radius: 4px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 4px 20px rgba(232,160,32,0.35);
    }
    .sdm-btn-primary:hover {
        background: var(--gold-light);
        color: var(--dark);
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(232,160,32,0.45);
        text-decoration: none;
    }
    .sdm-btn-outline {
        background: transparent;
        color: rgba(255,255,255,0.8);
        font-weight: 500;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.85rem 2rem;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 4px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.25s ease;
    }
    .sdm-btn-outline:hover {
        border-color: rgba(255,255,255,0.6);
        color: white;
        text-decoration: none;
    }

    /* Stats rapides hero */
    .sdm-hero-stats {
        display: flex;
        gap: 3rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 2rem;
        flex-wrap: wrap;
    }
    .sdm-stat-item {}
    .sdm-stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
    }
    .sdm-stat-label {
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.45);
        margin-top: 0.3rem;
    }

    /* Décoration droite */
    .sdm-hero-deco {
        position: absolute;
        right: 3rem; top: 50%;
        transform: translateY(-50%);
        width: 340px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .sdm-deco-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 3px solid var(--gold);
        backdrop-filter: blur(8px);
        border-radius: 8px;
        padding: 1.1rem 1.4rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .sdm-deco-icon {
        font-size: 1.6rem;
        width: 42px;
        text-align: center;
        flex-shrink: 0;
    }
    .sdm-deco-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.45);
    }
    .sdm-deco-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        color: white;
        font-weight: 700;
    }

    /* ══ Section Cards Secteurs ══════════════════════════════════════ */
    .sdm-sectors {
        padding: 5rem 2rem;
        background: white;
        position: relative;
    }
    .sdm-sectors::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--blue) 0%, var(--gold) 50%, var(--blue) 100%);
    }
    .sdm-section-tag {
        font-size: 0.7rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--gold);
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .sdm-section-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--dark);
        margin-bottom: 0.8rem;
    }
    .sdm-section-lead {
        color: var(--muted);
        font-size: 0.95rem;
        max-width: 480px;
        line-height: 1.7;
    }

    /* Cards secteur */
    .sdm-sector-card {
        background: var(--cream);
        border-radius: 12px;
        border: 1px solid rgba(0,74,153,0.08);
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        display: block;
        height: 100%;
    }
    .sdm-sector-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(0,74,153,0.15);
        border-color: var(--gold);
        text-decoration: none;
    }
    .sdm-card-header {
        height: 7px;
    }
    .sdm-card-body { padding: 2rem; }
    .sdm-card-icon {
        font-size: 2.4rem;
        margin-bottom: 1.2rem;
        display: block;
    }
    .sdm-card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--dark);
        margin-bottom: 0.6rem;
    }
    .sdm-card-desc {
        font-size: 0.85rem;
        color: var(--muted);
        line-height: 1.65;
        margin-bottom: 1.6rem;
    }
    .sdm-card-kpis {
        display: flex;
        gap: 1.2rem;
        border-top: 1px solid rgba(0,0,0,0.06);
        padding-top: 1.2rem;
        margin-bottom: 1.4rem;
    }
    .sdm-kpi-val {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--blue);
    }
    .sdm-kpi-lab {
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
    }
    .sdm-card-cta {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        transition: gap 0.2s ease;
    }
    .sdm-sector-card:hover .sdm-card-cta { gap: 0.8rem; }

    /* ══ Band chiffres clés ══════════════════════════════════════════ */
    .sdm-band {
        background: var(--dark);
        padding: 3.5rem 2rem;
        position: relative;
        overflow: hidden;
    }
    .sdm-band::after {
        content: '';
        position: absolute;
        bottom: -60px; right: -60px;
        width: 300px; height: 300px;
        border-radius: 50%;
        border: 60px solid rgba(232,160,32,0.06);
    }
    .sdm-band-stat {
        text-align: center;
        padding: 1rem;
        position: relative;
        z-index: 1;
    }
    .sdm-band-stat + .sdm-band-stat::before {
        content: '';
        position: absolute;
        left: 0; top: 20%; bottom: 20%;
        width: 1px;
        background: rgba(255,255,255,0.1);
    }
    .sdm-band-num {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: var(--gold);
        line-height: 1;
    }
    .sdm-band-unit {
        font-size: 1.1rem;
        color: rgba(232,160,32,0.6);
    }
    .sdm-band-label {
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.4);
        margin-top: 0.5rem;
    }

    /* ══ Footer ══════════════════════════════════════════════════════ */
    .sdm-footer {
        background: var(--dark);
        border-top: 1px solid rgba(255,255,255,0.06);
        padding: 2rem 3rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .sdm-footer-brand {
        font-family: 'Playfair Display', serif;
        font-size: 1rem;
        font-weight: 700;
        color: white;
    }
    .sdm-footer-brand span { color: var(--gold); }
    .sdm-footer-copy {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.3);
    }
    .sdm-footer-source {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.3);
        font-style: italic;
    }

    /* ══ Page container (pour les sous-pages) ════════════════════════ */
    .page-content {
        min-height: 80vh;
        padding: 2rem 2rem 4rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    @media (max-width: 992px) {
        .sdm-hero-deco { display: none; }
        .sdm-hero-title { font-size: 2.6rem; }
    }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

# ─── Navbar ────────────────────────────────────────────────────────────────────
navbar = html.Nav(
    className="sdm-nav",
    children=html.Div(
        style={"display":"flex","alignItems":"center","justifyContent":"space-between",
               "maxWidth":"1400px","margin":"0 auto","height":"64px"},
        children=[
            # Brand
            dcc.Link(
                children=[html.Span("Luc-Yvan"), " DATA", html.Span(" MONITOR", style={"color":"#E8A020"})],
                href="/",
                className="sdm-brand",
                style={"fontFamily":"'Playfair Display',serif","fontSize":"1.2rem",
                       "fontWeight":"900","color":"white","textDecoration":"none","letterSpacing":"0.04em"}
            ),
            # Links
            html.Div(
                style={"display":"flex","gap":"0.3rem","alignItems":"center"},
                children=[
                    dcc.Link("  Accueil",  href="/",          className="sdm-navlink"),
                    dcc.Link("  Banque",    href="/banque",     className="sdm-navlink"),
                    dcc.Link("  Assurance", href="/assurance",  className="sdm-navlink"),
                    dcc.Link("  Énergie",   href="/energie",    className="sdm-navlink"),
                ]
            ),
        ]
    )
)

# ─── Page de Garde (Hero) ──────────────────────────────────────────────────────
landing_page = html.Div([

    # ── Hero ──────────────────────────────────────────────────────────────────
    html.Div(className="sdm-hero", children=[
        # Contenu gauche
        html.Div(className="sdm-hero-inner", children=[
            # Pill
            html.Div(className="sdm-pill",
                     children="République du Sénégal · Données 2015–2023"),
            # Titre
            html.H1(className="sdm-hero-title", children=[
                "Observatoire Financier", html.Br(),
                "du ", html.Em("Sénégal")
            ]),
            # Sous-titre
            html.P(className="sdm-hero-sub",
                   children="Analyse comparative et dynamique de croissance des secteurs "
                             "Bancaire, Assurantiel et Énergétique. Données consolidées "
                             "issues de la Commission Bancaire et de l'APBEF-Sénégal."),
            # CTA
            html.Div(className="sdm-cta-group", children=[
                dcc.Link("Explorer la Banque →", href="/banque", className="sdm-btn-primary"),
                dcc.Link("Voir l'Assurance",     href="/assurance", className="sdm-btn-outline"),
                dcc.Link("Secteur Énergie",       href="/energie",   className="sdm-btn-outline"),
            ]),
            # Stats
            html.Div(className="sdm-hero-stats", children=[
                html.Div(className="sdm-stat-item", children=[
                    html.Div("27", className="sdm-stat-number"),
                    html.Div("Banques analysées", className="sdm-stat-label"),
                ]),
                html.Div(className="sdm-stat-item", children=[
                    html.Div("8 600", className="sdm-stat-number"),
                    html.Div("Mds FCFA Bilan secteur", className="sdm-stat-label"),
                ]),
                html.Div(className="sdm-stat-item", children=[
                    html.Div("+11%", className="sdm-stat-number"),
                    html.Div("TCAM Bilan 2015–2020", className="sdm-stat-label"),
                ]),
                html.Div(className="sdm-stat-item", children=[
                    html.Div("6", className="sdm-stat-number"),
                    html.Div("Années de données", className="sdm-stat-label"),
                ]),
            ]),
        ]),

        # Décoration droite (cards flottantes)
        html.Div(className="sdm-hero-deco", children=[
            html.Div(className="sdm-deco-card", children=[
                html.Div("", className="sdm-deco-icon"),
                html.Div([
                    html.Div("Secteur Bancaire", className="sdm-deco-label"),
                    html.Div("8 603 Mds FCFA", className="sdm-deco-value"),
                ])
            ]),
            html.Div(className="sdm-deco-card", children=[
                html.Div("", className="sdm-deco-icon"),
                html.Div([
                    html.Div("Secteur Assurance", className="sdm-deco-label"),
                    html.Div("TCAM +12%", className="sdm-deco-value"),
                ])
            ]),
            html.Div(className="sdm-deco-card", children=[
                html.Div("", className="sdm-deco-icon"),
                html.Div([
                    html.Div("Secteur Énergie", className="sdm-deco-label"),
                    html.Div("En développement", className="sdm-deco-value"),
                ])
            ]),
            html.Div(className="sdm-deco-card", children=[
                html.Div("", className="sdm-deco-icon"),
                html.Div([
                    html.Div("Source principale", className="sdm-deco-label"),
                    html.Div("Commission Bancaire UMOA", className="sdm-deco-value"),
                ])
            ]),
        ]),
    ]),

    # ── Bande chiffres clés ────────────────────────────────────────────────────
    html.Div(className="sdm-band", children=[
        dbc.Container(dbc.Row([
            dbc.Col(html.Div(className="sdm-band-stat", children=[
                html.Div([html.Span("8 603", className="sdm-band-num"),
                           html.Span(" Mds", className="sdm-band-unit")]),
                html.Div("Total Bilan Bancaire 2020", className="sdm-band-label"),
            ]), xs=12, sm=6, md=3),
            dbc.Col(html.Div(className="sdm-band-stat", children=[
                html.Div([html.Span("27", className="sdm-band-num"),
                           html.Span(" banques", className="sdm-band-unit")]),
                html.Div("Établissements analysés", className="sdm-band-label"),
            ]), xs=12, sm=6, md=3),
            dbc.Col(html.Div(className="sdm-band-stat", children=[
                html.Div([html.Span("+58.7", className="sdm-band-num"),
                           html.Span(" %", className="sdm-band-unit")]),
                html.Div("TCAM BGFI Bank 2015-2020", className="sdm-band-label"),
            ]), xs=12, sm=6, md=3),
            dbc.Col(html.Div(className="sdm-band-stat", children=[
                html.Div([html.Span("60", className="sdm-band-num"),
                           html.Span(" % PIB", className="sdm-band-unit")]),
                html.Div("Poids du secteur / PIB national", className="sdm-band-label"),
            ]), xs=12, sm=6, md=3),
        ]), fluid=True)
    ]),

    # ── Section secteurs ───────────────────────────────────────────────────────
    html.Div(className="sdm-sectors", children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div("NOS ANALYSES", className="sdm-section-tag"),
                    html.H2("Trois secteurs,\nune vision complète", className="sdm-section-title"),
                    html.P("Positionnement stratégique, dynamiques de croissance et "
                           "productivité comparée — pour chaque acteur du marché.",
                           className="sdm-section-lead"),
                ], md=4, className="mb-5"),
            ]),
            dbc.Row(className="g-4", children=[

                # Card Banque
                dbc.Col(
                    dcc.Link(href="/banque", style={"textDecoration":"none"}, children=[
                        html.Div(className="sdm-sector-card", children=[
                            html.Div(className="sdm-card-header",
                                     style={"background":"linear-gradient(90deg,#004a99,#1a5fad)"}),
                            html.Div(className="sdm-card-body", children=[
                                html.Span("", className="sdm-card-icon"),
                                html.H3("Secteur Bancaire", className="sdm-card-title"),
                                html.P("Analyse complète du positionnement de BGFI Bank face "
                                       "aux 23 autres établissements du marché sénégalais. "
                                       "Parts de marché, TCAM, productivité et risque.",
                                       className="sdm-card-desc"),
                                html.Div(className="sdm-card-kpis", children=[
                                    html.Div([
                                        html.Div("27", className="sdm-kpi-val"),
                                        html.Div("Banques", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("2015–2020", className="sdm-kpi-val"),
                                        html.Div("Période", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("+11%", className="sdm-kpi-val"),
                                        html.Div("TCAM marché", className="sdm-kpi-lab"),
                                    ]),
                                ]),
                                html.Div(className="sdm-card-cta",
                                         style={"color":"#004a99"},
                                         children=["Accéder à l'analyse", " →"]),
                            ]),
                        ])
                    ]),
                    md=4,
                ),

                # Card Assurance
                dbc.Col(
                    dcc.Link(href="/assurance", style={"textDecoration":"none"}, children=[
                        html.Div(className="sdm-sector-card", children=[
                            html.Div(className="sdm-card-header",
                                     style={"background":"linear-gradient(90deg,#E8A020,#F5CF7E)"}),
                            html.Div(className="sdm-card-body", children=[
                                html.Span("", className="sdm-card-icon"),
                                html.H3("Secteur Assurance", className="sdm-card-title"),
                                html.P("Vue comparative du marché assurantiel sénégalais. "
                                       "Primes émises, sinistres, taux de pénétration et "
                                       "dynamiques de croissance par acteur.",
                                       className="sdm-card-desc"),
                                html.Div(className="sdm-card-kpis", children=[
                                    html.Div([
                                        html.Div("–", className="sdm-kpi-val"),
                                        html.Div("Assureurs", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("+12%", className="sdm-kpi-val"),
                                        html.Div("TCAM estimé", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("En cours", className="sdm-kpi-val",
                                                 style={"fontSize":"0.9rem","color":"#E8A020"}),
                                        html.Div("Statut données", className="sdm-kpi-lab"),
                                    ]),
                                ]),
                                html.Div(className="sdm-card-cta",
                                         style={"color":"#E8A020"},
                                         children=["Accéder à l'analyse", " →"]),
                            ]),
                        ])
                    ]),
                    md=4,
                ),

                # Card Énergie
                dbc.Col(
                    dcc.Link(href="/energie", style={"textDecoration":"none"}, children=[
                        html.Div(className="sdm-sector-card", children=[
                            html.Div(className="sdm-card-header",
                                     style={"background":"linear-gradient(90deg,#1a8a5a,#2ec07e)"}),
                            html.Div(className="sdm-card-body", children=[
                                html.Span("⚡", className="sdm-card-icon"),
                                html.H3("Secteur Énergie", className="sdm-card-title"),
                                html.P("Analyse du secteur énergétique sénégalais dans le "
                                       "contexte de la transition vers les énergies renouvelables "
                                       "et des nouveaux gisements pétro-gaziers.",
                                       className="sdm-card-desc"),
                                html.Div(className="sdm-card-kpis", children=[
                                    html.Div([
                                        html.Div("–", className="sdm-kpi-val"),
                                        html.Div("Acteurs", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("Pétrole & Gaz", className="sdm-kpi-val",
                                                 style={"fontSize":"0.85rem","color":"#1a8a5a"}),
                                        html.Div("Focus", className="sdm-kpi-lab"),
                                    ]),
                                    html.Div([
                                        html.Div("À venir", className="sdm-kpi-val",
                                                 style={"fontSize":"0.9rem","color":"#1a8a5a"}),
                                        html.Div("Statut", className="sdm-kpi-lab"),
                                    ]),
                                ]),
                                html.Div(className="sdm-card-cta",
                                         style={"color":"#1a8a5a"},
                                         children=["Accéder à l'analyse", " →"]),
                            ]),
                        ])
                    ]),
                    md=4,
                ),
            ]),
        ], fluid="lg")
    ]),

    # ── Footer ─────────────────────────────────────────────────────────────────
    html.Footer(className="sdm-footer", children=[
        html.Div([
            html.Span("Luc-Yvan ", className="sdm-footer-brand"),
            html.Span("DATA MONITOR", style={"color":"#E8A020","fontFamily":"'Playfair Display',serif","fontWeight":"700"}),
        ]),
        html.Div("© 2026 — Analyses Performances Luc-Yvan Group", className="sdm-footer-copy"),
        html.Div("Sources : Commission Bancaire UMOA · APBEF-Sénégal", className="sdm-footer-source"),
    ]),
])

# ─── Layout principal ──────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    # Page container : affiche la landing OU la page Dash selon l'URL
    html.Div(id="page-content"),
    # Toujours rendu (nécessaire pour use_pages)
    html.Div(dash.page_container, style={"display":"none"}),
])

# ─── Callback : home = landing page, autres = pages Dash ──────────────────────
from dash import Input, Output

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page(pathname):
    if pathname in ("/", None, ""):
        return landing_page
    # Pour les sous-pages, on laisse Dash gérer via page_container
    return html.Div(
        dash.page_container,
        className="page-content"
    )

# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # debug=False obligatoire en production (Render)
    debug = os.environ.get("DASH_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))










