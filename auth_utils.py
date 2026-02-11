diff --git a/auth_utils.py b/auth_utils.py
index d405987d2750ceb7011421aa630d4153e70252ab..04ab5656cfb6504b47e145db45a51034ac330f92 100644
--- a/auth_utils.py
+++ b/auth_utils.py
@@ -1,21 +1,24 @@
 # auth_utils.py
-from models import Coproprietaire
 import streamlit as st
 from sqlalchemy.orm import sessionmaker
-from models import db
+
+from models import Coproprietaire, db
 
 Session = sessionmaker(bind=db)
 session = Session()
 
+
 def login():
     st.subheader("Connexion")
+    st.caption("Compte de démonstration initial : admin@copro.local / admin")
     email = st.text_input("Email")
     pwd = st.text_input("Mot de passe", type="password")
     if st.button("Se connecter"):
         user = session.query(Coproprietaire).filter_by(email=email, password=pwd).first()
         if user:
             st.session_state["user"] = user.id
             st.session_state["role"] = user.role
             st.success(f"Bienvenue {user.nom}")
+            st.rerun()
         else:
             st.error("Email ou mot de passe incorrect")
