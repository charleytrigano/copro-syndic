import streamlit as st
from models import db, Coproprietaire, Immeuble
from sqlalchemy.orm import sessionmaker

# Base SQLAlchemy
Session = sessionmaker(bind=db)
session = Session()

st.title("Gestion Syndic – Multi Immeubles")

menu = ["Dashboard", "Immeubles", "Copropriétaires", "Appels de fonds"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("Dashboard")
    nb_copro = session.query(Coproprietaire).count()
    nb_immeubles = session.query(Immeuble).count()
    st.write(f"Nombre de copropriétaires : {nb_copro}")
    st.write(f"Nombre d'immeubles : {nb_immeubles}")

elif choice == "Immeubles":
    st.subheader("Immeubles")
    if st.button("Ajouter un immeuble"):
        nom = st.text_input("Nom de l'immeuble")
        adresse = st.text_input("Adresse")
        if st.button("Créer"):
            immeuble = Immeuble(nom=nom, adresse=adresse)
            session.add(immeuble)
            session.commit()
            st.success("Immeuble créé !")

# Ajouter ici les sections Copropriétaires / Appels de fonds

