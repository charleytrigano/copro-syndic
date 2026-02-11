import streamlit as st
from sqlalchemy.orm import sessionmaker
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from models import (
    engine,
    init_db,
    Coproprietaire,
    Immeuble,
    Lot,
    AppelFonds,
    LigneAppel
)

# --------------------------------------------------
# INITIALISATION
# --------------------------------------------------

st.set_page_config(page_title="Syndic", layout="wide")

init_db()
Session = sessionmaker(bind=engine)
db = Session()

# --------------------------------------------------
# SESSION STATE (CRUCIAL)
# --------------------------------------------------

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

# --------------------------------------------------
# AUTHENTIFICATION
# --------------------------------------------------

def login():
    st.title("Connexion")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        user = db.query(Coproprietaire).filter_by(
            email=email,
            password=password
        ).first()

        if user:
            st.session_state["user_id"] = user.id
            st.session_state["role"] = user.role
            st.experimental_rerun()
        else:
            st.error("Identifiants incorrects")

# --------------------------------------------------
# PDF (REPORTLAB)
# --------------------------------------------------

def generer_pdf(copro, lignes):
    fichier = f"releve_{copro.id}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(fichier)
    elements = []

    elements.append(Paragraph("Relevé de compte", styles["Title"]))
    elements.append(Paragraph(f"Copropriétaire : {copro.nom}", styles["Normal"]))
    elements.append(Paragraph(" ", styles["Normal"]))

    total = 0
    for l in lignes:
        solde = l.montant_du - l.montant_paye
        total += solde
        elements.append(
            Paragraph(
                f"Période {l.appel.periode} — "
                f"Dû : {l.montant_du:.2f} € | "
                f"Payé : {l.montant_paye:.2f} € | "
                f"Solde : {solde:.2f} €",
                styles["Normal"]
            )
        )

    elements.append(Paragraph(" ", styles["Normal"]))
    elements.append(
        Paragraph(f"<b>Total dû : {total:.2f} €</b>", styles["Heading2"])
    )

    doc.build(elements)
    return fichier

# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if st.session_state["user_id"] is None:
    login()
    st.stop()

# --------------------------------------------------
# UTILISATEUR CONNECTÉ
# --------------------------------------------------

user = db.query(Coproprietaire).get(st.session_state["user_id"])
role = st.session_state["role"]

st.sidebar.success(f"{user.nom} ({role})")

menu = ["Dashboard", "Immeubles", "Appels de fonds", "Mon compte"]
choice = st.sidebar.selectbox("Menu", menu)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if choice == "Dashboard":
    st.title("Dashboard")
    st.metric("Immeubles", db.query(Immeuble).count())
    st.metric("Copropriétaires", db.query(Coproprietaire).count())
    st.metric("Appels de fonds", db.query(AppelFonds).count())

# --------------------------------------------------
# IMMEUBLES (SYNDIC)
# --------------------------------------------------

elif choice == "Immeubles" and role == "syndic":
    st.title("Immeubles")

    with st.form("add_immeuble"):
        nom = st.text_input("Nom de l'immeuble")
        adresse = st.text_input("Adresse")
        submit = st.form_submit_button("Créer")

        if submit:
            db.add(Immeuble(nom=nom, adresse=adresse))
            db.commit()
            st.success("Immeuble créé")

    st.subheader("Liste des immeubles")
    for im in db.query(Immeuble).all():
        st.write(f"🏢 {im.nom} – {im.adresse}")

# --------------------------------------------------
# APPELS DE FONDS (SYNDIC)
# --------------------------------------------------

elif choice == "Appels de fonds" and role == "syndic":
    st.title("Appels de fonds")

    immeubles = db.query(Immeuble).all()
    if not immeubles:
        st.warning("Aucun immeuble existant")
        st.stop()

    im = st.selectbox("Immeuble", immeubles, format_func=lambda x: x.nom)
    periode = st.text_input("Période (ex : T1 2026)")
    montant = st.number_input("Montant total (€)", min_value=0.0)

    if st.button("Créer et répartir l'appel"):
        appel = AppelFonds(
            immeuble_id=im.id,
            periode=periode,
            montant_total=montant,
            statut="valide"
        )
        db.add(appel)
        db.commit()

        lots = db.query(Lot).filter_by(immeuble_id=im.id).all()
        total_tantiemes = sum(l.tantiemes for l in lots)

        for lot in lots:
            copro = db.query(Coproprietaire).filter_by(lot_id=lot.id).first()
            if copro and total_tantiemes > 0:
                part = (lot.tantiemes / total_tantiemes) * montant
                db.add(LigneAppel(
                    appel_id=appel.id,
                    copro_id=copro.id,
                    montant_du=round(part, 2)
                ))

        db.commit()
        st.success("Appel de fonds créé et réparti")

# --------------------------------------------------
# MON COMPTE (COPRO)
# --------------------------------------------------

elif choice == "Mon compte":
    st.title("Mon compte")

    lignes = db.query(LigneAppel).filter_by(copro_id=user.id).all()

    if not lignes:
        st.info("Aucune ligne comptable")
    else:
        for l in lignes:
            st.write(
                f"{l.appel.periode} | "
                f"Dû : {l.montant_du:.2f} € | "
                f"Payé : {l.montant_paye:.2f} €"
            )

        if st.button("Télécharger mon relevé PDF"):
            fichier = generer_pdf(user, lignes)
            with open(fichier, "rb") as f:
                st.download_button(
                    "Télécharger le PDF",
                    f,
                    file_name=fichier
                )
