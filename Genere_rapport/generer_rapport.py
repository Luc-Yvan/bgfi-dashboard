import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
import pandas as pd
from Genere_rapport.htm_rapport import add_toc


def notebook_to_html(
    notebook_path,
    data_path="C:/Users/user/Documents/Data Ingenieur2/Projet_banque/Data/BASE_SENEGAL2.csv",
    output_filename="Rapport.html"
):  
    # Lecture du notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook_content = f.read()
    notebook = nbformat.reads(notebook_content, as_version=4)

    # Exécution du notebook
    executor = ExecutePreprocessor(timeout=-1)
    executor.preprocess(notebook)

    # Exportation en HTML
    html_exporter = HTMLExporter(template_name="classic", exclude_input=True)
    resources = {"embed_widgets": True}
    body, _ = html_exporter.from_notebook_node(notebook, resources=resources)

    # Ajout du sommaire
    body = add_toc(body)

    # Calcul dynamique du total bilan
    df = pd.read_excel(data_path)
    df.columns = df.columns.str.strip()
    total_bilan = df["BILAN"].sum()
    total_bilan_milliards = round(total_bilan / 1000, 2)
    nb_banques = df["Sigle"].nunique()

    synthese = f"""
    <div style="margin-top:20px; padding:10px; background:#f0f0f0; border-radius:5px;">
        <h3> Synthèse bancaire</h3>
        <p>Le secteur bancaire sénégalais compte <b>{nb_banques}</b> banques,
        représentant un <b>total bilan de {total_bilan_milliards:,} milliards FCFA</b>,
        soit près de 60% du PIB national.</p>
    </div>
    """
    body += synthese

    # Sauvegarde du fichier HTML
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(body)

    return body
