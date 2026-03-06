import os
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from bs4 import BeautifulSoup

def generate_report():
    """Exécute le notebook Rapport.ipynb et renvoie le HTML."""
    base_dir = os.getcwd()
    # On pointe vers ton fichier exact dans le dossier Data
    notebook_path = os.path.join(base_dir, 'Data', 'Rapport.ipynb')
    
    if not os.path.exists(notebook_path):
        return "<h1>Erreur : Fichier Data/Rapport.ipynb introuvable</h1>"

    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        
        # Exécution
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': base_dir}})

        # Export HTML
        html_exporter = HTMLExporter(template_name="classic", exclude_input=True)
        body, _ = html_exporter.from_notebook_node(nb)
        
        return body

    except Exception as e:
        return f"<h1>Erreur lors de la génération : {e}</h1>"