"""
Database configuration and models for Spacegom
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_DIR = "data"
DATABASE_PATH = f"{DATABASE_DIR}/spacegom.db"

# Ensure data directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Create engine
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Planet(Base):
    """Planet model based on the Excel database"""
    __tablename__ = "planets"

    code = Column(Integer, primary_key=True)  # 111-666
    name = Column(String, nullable=False)
    
    # Soporte vital (*1 a *6)
    life_support_1 = Column(String)  # NO/NO*/SÍ
    life_support_2 = Column(String)
    life_support_3 = Column(String)
    life_support_4 = Column(String)  # Número
    life_support_5 = Column(String)  # Número con +
    
    # Espaciopuerto e instalaciones
    spaceport = Column(String)  # MED-DB-2, NOT-DM-9, etc.
    orbital_facilities = Column(String)  # CC, PI, DS, AA
    
    # Productos disponibles (INDU, BASI, ALIM, MADE, AGUA, MICO, MIRA, MIPR, PAVA, A, AE, AEI, COM)
    product_indu = Column(Boolean, default=False)
    product_basi = Column(Boolean, default=False)
    product_alim = Column(Boolean, default=False)
    product_made = Column(Boolean, default=False)
    product_agua = Column(Boolean, default=False)
    product_mico = Column(Boolean, default=False)
    product_mira = Column(Boolean, default=False)
    product_mipr = Column(Boolean, default=False)
    product_pava = Column(Boolean, default=False)
    product_a = Column(Boolean, default=False)
    product_ae = Column(Boolean, default=False)
    product_aei = Column(Boolean, default=False)
    product_com = Column(Boolean, default=False)
    
    # Campos adicionales (*7 a *10)
    field_7 = Column(String)
    field_8 = Column(String)
    field_9 = Column(String)
    field_10 = Column(String)
    
    # Campos para validación inicial (Bootstrap)
    tech_level = Column(String)  # PR, RUD, ES, INT, POL, N.S
    population_over_1000 = Column(Boolean, default=True)
    convenio_spacegom = Column(Boolean, default=True)
    
    # Campo para planetas personalizados creados durante la partida
    is_custom = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Planet {self.code}: {self.name}>"


# Create tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
