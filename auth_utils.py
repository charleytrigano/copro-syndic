# auth_utils.py
from models import Coproprietaire
import streamlit as st
from sqlalchemy.orm import sessionmaker
from models import db

Session = sessionmaker(bind=db)
session = Session()

def login():
    st.subheader("Connexion")
    email = st.text_input("Email")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        user = session.query(Coproprietaire).filter_by(email=email, password=pwd).first()
        if user:
            st.session_state["user"] = user.id
            st.session_state["role"] = user.role
            st.success(f"Bienvenue {user.nom}")
        else:
            st.error("Email ou mot de passe incorrect")
