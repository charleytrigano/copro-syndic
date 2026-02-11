diff --git a/app.py b/app.py
index 8ea2750cfecea6dcadd2e1a6fc50569699160ef8..884f314aa09b33088622cb49b918a57d4977182c 100644
--- a/app.py
+++ b/app.py
@@ -1,88 +1,127 @@
 import streamlit as st
 from sqlalchemy.orm import sessionmaker
-from models import db, Coproprietaire, Immeuble, Lot, AppelFonds, LigneAppel
+
 from auth_utils import login
+from models import (
+    AppelFonds,
+    Coproprietaire,
+    Immeuble,
+    LigneAppel,
+    db,
+    ensure_default_data,
+)
 from pdf_utils import generer_pdf_releve
 
-# --- Base SQLAlchemy ---
-Session = sessionmaker(bind=db)
-session = Session()
 
-# --- Login ---
-if "user" not in st.session_state:
-    login()
-else:
+def main() -> None:
+    # --- Base SQLAlchemy ---
+    Session = sessionmaker(bind=db)
+    session = Session()
+    ensure_default_data(session)
+
+    # --- Login ---
+    if "user" not in st.session_state:
+        login()
+        return
+
     user_id = st.session_state["user"]
     role = st.session_state["role"]
-    user = session.query(Coproprietaire).get(user_id)
+    user = session.get(Coproprietaire, user_id)
+
+    if user is None:
+        st.session_state.clear()
+        st.warning("Session expirée. Merci de vous reconnecter.")
+        st.rerun()
 
     st.title("Gestion Syndic – Multi Immeubles")
     st.sidebar.write(f"Connecté : {user.nom} ({role})")
 
+    if st.sidebar.button("Se déconnecter"):
+        st.session_state.clear()
+        st.rerun()
+
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
-        if st.button("Ajouter un immeuble"):
+
+        with st.form("ajout_immeuble"):
             nom = st.text_input("Nom de l'immeuble")
             adresse = st.text_input("Adresse")
-            if st.button("Créer"):
-                immeuble = Immeuble(nom=nom, adresse=adresse)
+            submitted = st.form_submit_button("Créer")
+
+        if submitted:
+            if not nom.strip() or not adresse.strip():
+                st.error("Le nom et l'adresse sont obligatoires.")
+            else:
+                immeuble = Immeuble(nom=nom.strip(), adresse=adresse.strip())
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
             # Relevé PDF pour le copro connecté
             lignes = session.query(LigneAppel).filter_by(copro_id=user.id).all()
             if st.button("Générer mon relevé PDF"):
                 fichier = generer_pdf_releve(user, lignes)
-                st.download_button(
-                    "Télécharger PDF",
-                    data=open(fichier, "rb").read(),
-                    file_name=f"releve_{user.nom}.pdf"
-                )
+                with open(fichier, "rb") as pdf_file:
+                    st.download_button(
+                        "Télécharger PDF",
+                        data=pdf_file.read(),
+                        file_name=f"releve_{user.nom}.pdf",
+                    )
 
     # --- Appels de fonds ---
     elif choice == "Appels de fonds" and role == "syndic":
         st.subheader("Appels de fonds")
         immeubles = session.query(Immeuble).all()
-        im_sel = st.selectbox("Sélectionner un immeuble", immeubles, format_func=lambda x: x.nom)
-        periode = st.text_input("Période (ex: T1 2026)")
-        montant_total = st.number_input("Montant total (€)", min_value=0.0, step=0.01)
-        if st.button("Créer l'appel de fonds"):
-            appel = AppelFonds(
-                immeuble_id=im_sel.id,
-                periode=periode,
-                montant_total=montant_total,
-                statut="brouillon"
-            )
-            session.add(appel)
-            session.commit()
-            st.success("Appel de fonds créé !")
-            st.info("Ajoute maintenant la répartition par tantièmes dans le code ou utils")
+
+        if not immeubles:
+            st.info("Ajoutez d'abord un immeuble avant de créer un appel de fonds.")
+        else:
+            im_sel = st.selectbox("Sélectionner un immeuble", immeubles, format_func=lambda x: x.nom)
+            periode = st.text_input("Période (ex: T1 2026)")
+            montant_total = st.number_input("Montant total (€)", min_value=0.0, step=0.01)
+            if st.button("Créer l'appel de fonds"):
+                if not periode.strip():
+                    st.error("La période est obligatoire.")
+                else:
+                    appel = AppelFonds(
+                        immeuble_id=im_sel.id,
+                        periode=periode.strip(),
+                        montant_total=montant_total,
+                        statut="brouillon",
+                    )
+                    session.add(appel)
+                    session.commit()
+                    st.success("Appel de fonds créé !")
+                    st.info("Étape suivante : ajouter la répartition par tantièmes.")
+
+
+if __name__ == "__main__":
+    main()
