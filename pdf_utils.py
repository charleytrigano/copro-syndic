 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/pdf_utils.py b/pdf_utils.py
index d37cefe8e97cc2f641b314070b49ffd14b4f1d9c..7d0cf50a7d71e0dae88233efac0251b1464e8fd6 100644
--- a/pdf_utils.py
+++ b/pdf_utils.py
@@ -1,11 +1,17 @@
 # pdf_utils.py
+from pathlib import Path
+
 from weasyprint import HTML
 
+
 def generer_pdf_releve(copro, lignes):
     html = f"<h1>Relevé de compte {copro.nom}</h1>"
     for l in lignes:
         html += f"<p>{l.montant_du} € - {l.montant_paye} €</p>"
-    fichier = f"assets/releve_{copro.id}.pdf"
-    HTML(string=html).write_pdf(fichier)
-    return fichier
 
+    output_dir = Path("assets")
+    output_dir.mkdir(parents=True, exist_ok=True)
+    fichier = output_dir / f"releve_{copro.id}.pdf"
+
+    HTML(string=html).write_pdf(str(fichier))
+    return str(fichier)
 
EOF
)
