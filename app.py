import streamlit as st
from sqlalchemy.orm import sessionmaker
from models import (
    engine,
    init_db,
    Coproprietaire,
    Immeuble,
    Lot,
    AppelFonds,
    LigneAppel
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# --- Initialisation DB ---
init_db()
Session = sessionmaker(bind=engine)
db = Session()

st.set_page_config(page_title="Syndic", layout="wide")

# --- Authentification ---
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

# --- PDF ---
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
                f"Période {l.appel.periode} — Dû : {l.montant_du:.2f} € | "
                f"Payé : {l.montant_paye:.2f} € | Solde : {solde:.2f} €",
                styles["Normal"]
            )
        )

    elements.append(Paragraph(" ", styles["Normal"]))
    elements.append(
        Paragraph(f"<b>Total dû : {total:.2f} €</b>", styles["Heading2"])
    )

    doc.build(elements)
    return fichier

# --- UTILISATEUR ---
user = db.query(Coproprietaire).get(st.session_state["user_id"])
role = st.session_state["role"]

st.sidebar.success(f"{user.nom} ({role})")

menu = ["Dashboard", "Immeubles", "Appels de fonds", "Mon compte"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Dashboard ---
if choice == "Dashboard":
    st.title("Dashboard")
    st.metric("Immeubles", db.query(Immeuble).count())
    st.metric("Copropriétaires", db.query(Coproprietaire).count())

# --- Immeubles (syndic seulement) ---
elif choice == "Immeubles" and role == "syndic":
    st.title("Immeubles")

    with st.form("add_immeuble"):
        nom = st.text_input("Nom")
        adresse = st.text_input("Adresse")
        if st.form_submit_button("Créer"):
            db.add(Immeuble(nom=nom, adresse=adresse))
            db.commit()
            st.success("Immeuble créé")

    for im in db.query(Immeuble).all():
        st.write(f"🏢 {im.nom} – {im.adresse}")

# --- Appels de fonds ---
elif choice == "Appels de fonds" and role == "syndic":
    st.title("Appels de fonds")

    immeubles = db.query(Immeuble).all()
    im = st.selectbox("Immeuble", immeubles, format_func=lambda x: x.nom)

    periode = st.text_input("Période")
    montant = st.number_input("Montant total", min_value=0.0)

    if st.button("Créer appel"):
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
            if copro:
                part = (lot.tantiemes / total_tantiemes) * montant
                db.add(LigneAppel(
                    appel_id=appel.id,
                    copro_id=copro.id,
                    montant_du=round(part, 2)
                ))
        db.commit()
        st.success("Appel réparti")

# --- Mon compte (copro) ---
elif choice == "Mon compte":
    st.title("Mon compte")

    lignes = db.query(LigneAppel).filter_by(copro_id=user.id).all()

    for l in lignes:
        st.write(
            f"{l.appel.periode} | Dû : {l.montant_du:.2f} € | Payé : {l.montant_paye:.2f} €"
        )

    if st.button("Télécharger mon relevé PDF"):
        fichier = generer_pdf(user, lignes)
        with open(fichier, "rb") as f:
            st.download_button(
                "Télécharger PDF",
                f,
                file_name=fichier
            )
