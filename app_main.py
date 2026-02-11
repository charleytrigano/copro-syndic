import streamlit as st
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import hashlib
import subprocess

from auth_utils import login
from models import (
    AppelFonds,
    Coproprietaire,
    Immeuble,
    LigneAppel,
    db,
    ensure_default_data,
)
from pdf_utils import generer_pdf_releve


def main() -> None:
    # --- Base SQLAlchemy ---
    Session = sessionmaker(bind=db)
    session = Session()
    ensure_default_data(session)

    # --- Login ---
    if "user" not in st.session_state:
        login()
        return

    user_id = st.session_state["user"]
    role = st.session_state["role"]
    user = session.get(Coproprietaire, user_id)

    if user is None:
        st.session_state.clear()
        st.warning("Session expirée. Merci de vous reconnecter.")
        st.rerun()

    st.title("Gestion Syndic – Multi Immeubles")
    st.sidebar.write(f"Connecté : {user.nom} ({role})")

    with st.sidebar.expander("Diagnostic déploiement"):
        st.caption("Vérifiez ici le commit et le contenu d'entrée réellement chargés.")
        st.code(_build_diagnostic(), language="text")

    if st.sidebar.button("Se déconnecter"):
        st.session_state.clear()
        st.rerun()

    # --- Menu principal ---
    menu = ["Dashboard", "Immeubles", "Copropriétaires", "Appels de fonds"]
    choice = st.sidebar.selectbox("Menu", menu)

    # --- Dashboard ---
    if choice == "Dashboard":
        st.subheader("Dashboard")
        nb_copro = session.query(Coproprietaire).count()
        nb_immeubles = session.query(Immeuble).count()
        st.write(f"Nombre de copropriétaires : {nb_copro}")
        st.write(f"Nombre d'immeubles : {nb_immeubles}")

    # --- Immeubles ---
    elif choice == "Immeubles" and role == "syndic":
        st.subheader("Immeubles")

        with st.form("ajout_immeuble"):
            nom = st.text_input("Nom de l'immeuble")
            adresse = st.text_input("Adresse")
            submitted = st.form_submit_button("Créer")

        if submitted:
            if not nom.strip() or not adresse.strip():
                st.error("Le nom et l'adresse sont obligatoires.")
            else:
                immeuble = Immeuble(nom=nom.strip(), adresse=adresse.strip())
                session.add(immeuble)
                session.commit()
                st.success("Immeuble créé !")

        st.write("Liste des immeubles existants :")
        immeubles = session.query(Immeuble).all()
        for im in immeubles:
            st.write(f"- {im.nom} ({im.adresse})")

    # --- Copropriétaires ---
    elif choice == "Copropriétaires":
        st.subheader("Copropriétaires")
        if role == "syndic":
            st.write("Liste complète des copropriétaires :")
            copros = session.query(Coproprietaire).all()
            for c in copros:
                st.write(f"- {c.nom} ({c.email})")
        else:
            st.write(f"Bienvenue {user.nom}")
            lignes = session.query(LigneAppel).filter_by(copro_id=user.id).all()
            if st.button("Générer mon relevé PDF"):
                fichier = generer_pdf_releve(user, lignes)
                with open(fichier, "rb") as pdf_file:
                    st.download_button(
                        "Télécharger PDF",
                        data=pdf_file.read(),
                        file_name=f"releve_{user.nom}.pdf",
                    )

    # --- Appels de fonds ---
    elif choice == "Appels de fonds" and role == "syndic":
        st.subheader("Appels de fonds")
        immeubles = session.query(Immeuble).all()

        if not immeubles:
            st.info("Ajoutez d'abord un immeuble avant de créer un appel de fonds.")
        else:
            im_sel = st.selectbox("Sélectionner un immeuble", immeubles, format_func=lambda x: x.nom)
            periode = st.text_input("Période (ex: T1 2026)")
            montant_total = st.number_input("Montant total (€)", min_value=0.0, step=0.01)
            if st.button("Créer l'appel de fonds"):
                if not periode.strip():
                    st.error("La période est obligatoire.")
                else:
                    appel = AppelFonds(
                        immeuble_id=im_sel.id,
                        periode=periode.strip(),
                        montant_total=montant_total,
                        statut="brouillon",
                    )
                    session.add(appel)
                    session.commit()
                    st.success("Appel de fonds créé !")
                    st.info("Étape suivante : ajouter la répartition par tantièmes.")


def _build_diagnostic() -> str:
    app_path = Path(__file__).with_name("app.py")
    app_preview = ""

    if app_path.exists():
        app_preview = "\n".join(app_path.read_text(encoding="utf-8").splitlines()[:3])

    commit = "inconnu"
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        pass

    app_hash = "inconnu"
    if app_path.exists():
        app_hash = hashlib.sha256(app_path.read_bytes()).hexdigest()[:12]

    return (
        f"commit: {commit}\n"
        f"app.py sha256: {app_hash}\n"
        "app.py (3 premières lignes):\n"
        f"{app_preview}"
    )


if __name__ == "__main__":
    main()
