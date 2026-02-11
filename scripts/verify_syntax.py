diff --git a/scripts/verify_syntax.py b/scripts/verify_syntax.py
new file mode 100644
index 0000000000000000000000000000000000000000..999221d27f5e01c1beaf062f002b6bec75b59201
--- /dev/null
+++ b/scripts/verify_syntax.py
@@ -0,0 +1,30 @@
+#!/usr/bin/env python3
+"""Vérifie la validité syntaxique de tous les fichiers Python du projet."""
+
+from __future__ import annotations
+
+import ast
+from pathlib import Path
+
+
+def main() -> int:
+    root = Path(__file__).resolve().parents[1]
+    py_files = sorted(
+        p for p in root.glob("*.py") if p.name not in {".venv"}
+    )
+
+    has_error = False
+    for path in py_files:
+        source = path.read_text(encoding="utf-8")
+        try:
+            ast.parse(source, filename=str(path))
+            print(f"OK   {path.name}")
+        except SyntaxError as exc:
+            has_error = True
+            print(f"FAIL {path.name}: {exc.msg} (ligne {exc.lineno}, colonne {exc.offset})")
+
+    return 1 if has_error else 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
