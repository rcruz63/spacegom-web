"""
Database configuration and models for Spacegom
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Float
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
    """
    Modelo de planeta para Spacegom
    
    Basado en el manual del juego y el archivo Excel de referencia.
    Todos los campos están documentados según las reglas oficiales.
    """
    __tablename__ = "planets"

    # Identificación
    code = Column(Integer, primary_key=True)  # Código 3d6 (111-666)
    name = Column(String, nullable=False)     # Nombre del planeta
    
    # === SOPORTE VITAL ===
    # Tipo de soporte vital necesario
    # Valores: NO, SO, MF, RE, RF, TE, TA, TH
    life_support = Column(String, nullable=False)
    
    # Riesgo de contagio local (SI/NO)
    local_contagion_risk = Column(String, nullable=False)
    
    # Días hasta estación de hiperdisparo
    days_to_hyperspace = Column(Float, nullable=False)
    
    # Ordenamiento legal (valor a igualar o superar, ej: "7+")
    legal_order_threshold = Column(String, nullable=False)
    
    # === ESPACIOPUERTO ===
    # Calidad del espaciopuerto
    # Valores: EXC (Excelente), NOT (Notable), MED (Medio), 
    #         BAS (Básico), RUD (Rudimentario), SIN (Sin espaciopuerto)
    spaceport_quality = Column(String, nullable=False)
    
    # Tipo de combustible disponible
    # Valores: DB (Densidad Baja), DM (Densidad Media), 
    #         DA (Densidad Alta), N (Ninguno)
    fuel_density = Column(String, nullable=False)
    
    # Precio de amarre (número)
    docking_price = Column(Integer, nullable=False)
    
    # === INSTALACIONES ORBITALES ===
    # CC - Centro de Cartografía
    orbital_cartography_center = Column(Boolean, default=False)
    
    # PI - Piratas Informáticos
    orbital_hackers = Column(Boolean, default=False)
    
    # DS - Depósito de Suministros
    orbital_supply_depot = Column(Boolean, default=False)
    
    # AA - Academia de Astronavegación
    orbital_astro_academy = Column(Boolean, default=False)
    
    # === PRODUCTOS DISPONIBLES ===
    # INDU - Productos industriales y manufacturados comunes
    product_indu = Column(Boolean, default=False)
    
    # BASI - Metal, plásticos, productos químicos y otros materiales básicos elaborados
    product_basi = Column(Boolean, default=False)
    
    # ALIM - Productos de alimentación
    product_alim = Column(Boolean, default=False)
    
    # MADE - Madera y derivados
    product_made = Column(Boolean, default=False)
    
    # AGUA - Agua potable
    product_agua = Column(Boolean, default=False)
    
    # MICO - Minerales comunes
    product_mico = Column(Boolean, default=False)
    
    # MIRA - Minerales raros y materias primas poco comunes
    product_mira = Column(Boolean, default=False)
    
    # MIPR - Metales preciosos, diamantes, gemas
    product_mipr = Column(Boolean, default=False)
    
    # PAVA - Productos avanzados, computadores modernos, robótica y otros equipos
    product_pava = Column(Boolean, default=False)
    
    # A - Armas hasta etapa espacial
    product_a = Column(Boolean, default=False)
    
    # AE - Armas a partir de etapa espacial
    product_ae = Column(Boolean, default=False)
    
    # AEI - Armas modernas a partir de etapa interestelar
    product_aei = Column(Boolean, default=False)
    
    # COM - Combustible para astronavegación
    product_com = Column(Boolean, default=False)
    
    # === INFORMACIÓN COMERCIAL ===
    # Nivel de autosuficiencia
    # Positivo: produce más de lo que necesita
    # Negativo: necesita más de lo que produce
    self_sufficiency_level = Column(Float, nullable=False)
    
    # UCN por pedido
    ucn_per_order = Column(Float, nullable=False)
    
    # Número máximo de pasajeros
    max_passengers = Column(Float, nullable=False)
    
    # Umbral de misiones (valor a igualar o superar en 2d6, ej: "7+")
    mission_threshold = Column(String, nullable=False)
    
    # === VALIDACIÓN PARA INICIO ===
    # Nivel tecnológico
    # Valores: PR (Primitivo), RUD (Rudimentario), ES (Estándar), 
    #         INT (Intermedio), POL (Pólvora), N.S (No Significativo)
    tech_level = Column(String)
    
    # Población mayor a 1000 habitantes
    population_over_1000 = Column(Boolean, default=True)
    
    # Adscrito al Convenio Universal Spacegom
    convenio_spacegom = Column(Boolean, default=True)
    
    # === NOTAS Y PERSONALIZACIÓN ===
    # Notas editables desde el frontend
    notes = Column(Text, default="")
    
    # Indica si es un planeta personalizado creado durante la partida
    is_custom = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Planet {self.code}: {self.name}>"


# Diccionarios de referencia para documentación
LIFE_SUPPORT_TYPES = {
    "NO": "No es necesario",
    "SO": "Suministro básico de oxígeno",
    "MF": "Máscara con Filtraje",
    "RE": "Respirador",
    "RF": "Respirador con Filtraje",
    "TE": "Traje espacial estándar",
    "TA": "Traje espacial avanzado",
    "TH": "Traje espacial hiperavanzado"
}

SPACEPORT_QUALITY = {
    "EXC": "Excelente",
    "NOT": "Notable",
    "MED": "Medio",
    "BAS": "Básico",
    "RUD": "Rudimentario",
    "SIN": "Sin espaciopuerto"
}

FUEL_DENSITY = {
    "DB": "Densidad Baja",
    "DM": "Densidad Media",
    "DA": "Densidad Alta",
    "N": "Ninguno"
}

PRODUCT_DESCRIPTIONS = {
    "INDU": "Productos industriales y manufacturados comunes",
    "BASI": "Metal, plásticos, productos químicos y otros materiales básicos elaborados",
    "ALIM": "Productos de alimentación",
    "MADE": "Madera y derivados",
    "AGUA": "Agua potable",
    "MICO": "Minerales comunes",
    "MIRA": "Minerales raros y materias primas poco comunes",
    "MIPR": "Metales preciosos, diamantes, gemas",
    "PAVA": "Productos avanzados, computadores modernos, robótica y otros equipos",
    "A": "Armas hasta etapa espacial",
    "AE": "Armas a partir de etapa espacial",
    "AEI": "Armas modernas a partir de etapa interestelar",
    "COM": "Combustible para astronavegación"
}


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
