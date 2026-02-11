from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import date

# --- Base SQLAlchemy ---
DATABASE_URL = "sqlite:///db.sqlite"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()

# --- Modèles ---

class Immeuble(Base):
    __tablename__ = "immeubles"

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    adresse = Column(String)

    lots = relationship("Lot", back_populates="immeuble")


class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True)
    immeuble_id = Column(Integer, ForeignKey("immeubles.id"))
    reference = Column(String)
    tantiemes = Column(Float, default=0)

    immeuble = relationship("Immeuble", back_populates="lots")
    coproprietaires = relationship("Coproprietaire", back_populates="lot")


class Coproprietaire(Base):
    __tablename__ = "coproprietaires"

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"))
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="copro")  # copro / syndic

    lot = relationship("Lot", back_populates="coproprietaires")
    lignes = relationship("LigneAppel", back_populates="coproprietaire")


class AppelFonds(Base):
    __tablename__ = "appels_fonds"

    id = Column(Integer, primary_key=True)
    immeuble_id = Column(Integer, ForeignKey("immeubles.id"))
    periode = Column(String)
    date_emission = Column(Date, default=date.today)
    montant_total = Column(Float)
    statut = Column(String, default="brouillon")

    lignes = relationship("LigneAppel", back_populates="appel")


class LigneAppel(Base):
    __tablename__ = "lignes_appels"

    id = Column(Integer, primary_key=True)
    appel_id = Column(Integer, ForeignKey("appels_fonds.id"))
    copro_id = Column(Integer, ForeignKey("coproprietaires.id"))
    montant_du = Column(Float)
    montant_paye = Column(Float, default=0)

    appel = relationship("AppelFonds", back_populates="lignes")
    coproprietaire = relationship("Coproprietaire", back_populates="lignes")


# --- Création des tables ---
def init_db():
    Base.metadata.create_all(engine)
