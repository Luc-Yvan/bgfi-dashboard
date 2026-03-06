from bs4 import BeautifulSoup


def add_toc(html_content):
    """
    Fonction pour ajouter un sommaire (table of contents) au contenu HTML avec une hiérarchie de sections.

    Parameters:
    html_content (str): Contenu HTML du notebook.

    Returns:
    str: Contenu HTML avec le sommaire hiérarchisé ajouté.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Trouver tous les titres
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

    if not headers:
        return html_content

    # Initialisation de la hiérarchie des niveaux de titres
    toc_list = []
    current_level = 0
    toc_stack = []

    def add_to_toc(header, level):
        nonlocal current_level, toc_stack

        # Enlever les symboles de paragraphe
        header_text = header.get_text().replace("¶", "").strip()
        header_id = header_text.replace(" ", "-").lower()
        header["id"] = header_id

        # Créer un nouvel item pour le sommaire
        toc_item = f'<li><a href="#{header_id}">{header_text}</a>'

        # Initialisation de toc_stack si vide
        if not toc_stack:
            toc_stack.append(toc_item)
        else:
            # Si c'est un sous-titre (h2 ou plus), on l'ajoute au niveau approprié
            if level > current_level:
                # Ajouter une sous-liste pour les sous-sections
                toc_stack[-1] += "<ul>"
                toc_stack.append(toc_item)
            elif level == current_level:
                toc_stack[-1] += "</li>"
                toc_stack.append(toc_item)
            else:
                # Fermer les sous-listes jusqu'à revenir au bon niveau
                while current_level > level:
                    toc_stack[-1] += "</li></ul>"
                    current_level -= 1
                toc_stack[-1] += "</li>"
                toc_stack.append(toc_item)

        current_level = level

    # Ajouter chaque titre à la table des matières hiérarchique
    for header in headers:
        level = int(header.name[1])  # h1 -> 1, h2 -> 2, etc.
        add_to_toc(header, level)

    # Fermer toutes les balises <ul> restantes
    while current_level > 0:
        toc_stack[-1] += "</li></ul>"
        current_level -= 1

    # Fermer la dernière balise <li>
    if toc_stack:
        toc_stack[-1] += "</li>"

    # Générer le HTML final du sommaire
    toc_html = (
        '<div id="toc"><h2>Table of Contents</h2><ul>'
        + "".join(toc_stack)
        + "</ul></div>"
    )

    # Insérer le sommaire au début du body
    body_tag = soup.body
    if body_tag:
        body_tag.insert(0, BeautifulSoup(toc_html, "html.parser"))

    return str(soup)
