diff --git a/models.py b/models.py
index 8b137891791fe96927ad78e64b0aad7bded08bdc..57430adad989da6314c0e733a39ba52bd6a49688 100644
--- a/models.py
+++ b/models.py
@@ -1 +1,107 @@
+from __future__ import annotations
 
+from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
+from sqlalchemy.orm import declarative_base, relationship
+
+
+Base = declarative_base()
+
+# Conservé sous le nom `db` pour rester compatible avec le reste du code.
+db = create_engine("sqlite:///db.sqlite", future=True)
+
+
+class Coproprietaire(Base):
+    __tablename__ = "coproprietaires"
+
+    id = Column(Integer, primary_key=True)
+    nom = Column(String(120), nullable=False)
+    email = Column(String(120), unique=True, nullable=False)
+    password = Column(String(255), nullable=False)
+    role = Column(String(32), nullable=False, default="copro")
+
+    lots = relationship("Lot", back_populates="coproprietaire", cascade="all, delete-orphan")
+    lignes_appel = relationship("LigneAppel", back_populates="coproprietaire", cascade="all, delete-orphan")
+
+    def __repr__(self) -> str:
+        return f"Coproprietaire(id={self.id!r}, nom={self.nom!r}, role={self.role!r})"
+
+
+class Immeuble(Base):
+    __tablename__ = "immeubles"
+
+    id = Column(Integer, primary_key=True)
+    nom = Column(String(120), nullable=False)
+    adresse = Column(String(255), nullable=False)
+
+    lots = relationship("Lot", back_populates="immeuble", cascade="all, delete-orphan")
+    appels = relationship("AppelFonds", back_populates="immeuble", cascade="all, delete-orphan")
+
+    def __repr__(self) -> str:
+        return f"Immeuble(id={self.id!r}, nom={self.nom!r})"
+
+
+class Lot(Base):
+    __tablename__ = "lots"
+
+    id = Column(Integer, primary_key=True)
+    reference = Column(String(50), nullable=False)
+    tantiemes = Column(Integer, nullable=False, default=0)
+    copro_id = Column(Integer, ForeignKey("coproprietaires.id"), nullable=False)
+    immeuble_id = Column(Integer, ForeignKey("immeubles.id"), nullable=False)
+
+    coproprietaire = relationship("Coproprietaire", back_populates="lots")
+    immeuble = relationship("Immeuble", back_populates="lots")
+
+    def __repr__(self) -> str:
+        return f"Lot(id={self.id!r}, reference={self.reference!r}, tantiemes={self.tantiemes!r})"
+
+
+class AppelFonds(Base):
+    __tablename__ = "appels_fonds"
+
+    id = Column(Integer, primary_key=True)
+    immeuble_id = Column(Integer, ForeignKey("immeubles.id"), nullable=False)
+    periode = Column(String(50), nullable=False)
+    montant_total = Column(Float, nullable=False, default=0.0)
+    statut = Column(String(32), nullable=False, default="brouillon")
+
+    immeuble = relationship("Immeuble", back_populates="appels")
+    lignes = relationship("LigneAppel", back_populates="appel", cascade="all, delete-orphan")
+
+    def __repr__(self) -> str:
+        return f"AppelFonds(id={self.id!r}, periode={self.periode!r}, statut={self.statut!r})"
+
+
+class LigneAppel(Base):
+    __tablename__ = "lignes_appel"
+
+    id = Column(Integer, primary_key=True)
+    appel_id = Column(Integer, ForeignKey("appels_fonds.id"), nullable=False)
+    copro_id = Column(Integer, ForeignKey("coproprietaires.id"), nullable=False)
+    montant_du = Column(Float, nullable=False, default=0.0)
+    montant_paye = Column(Float, nullable=False, default=0.0)
+
+    appel = relationship("AppelFonds", back_populates="lignes")
+    coproprietaire = relationship("Coproprietaire", back_populates="lignes_appel")
+
+    def __repr__(self) -> str:
+        return f"LigneAppel(id={self.id!r}, montant_du={self.montant_du!r}, montant_paye={self.montant_paye!r})"
+
+
+Base.metadata.create_all(db)
+
+
+def ensure_default_data(session) -> None:
+    """Insère un compte syndic de démonstration si la base est vide."""
+    has_user = session.query(Coproprietaire).first() is not None
+    if has_user:
+        return
+
+    syndic = Coproprietaire(
+        nom="Syndic Demo",
+        email="admin@copro.local",
+        password="admin",
+        role="syndic",
+    )
+    session.add(syndic)
+    session.commit()

