# pdf_utils.py
from weasyprint import HTML

def generer_pdf_releve(copro, lignes):
    html = f"<h1>Relevé de compte {copro.nom}</h1>"
    for l in lignes:
        html += f"<p>{l.montant_du} € - {l.montant_paye} €</p>"
    fichier = f"assets/releve_{copro.id}.pdf"
    HTML(string=html).write_pdf(fichier)
    return fichier

