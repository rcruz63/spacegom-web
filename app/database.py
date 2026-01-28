"""
Database configuration and models for Spacegom.

Este módulo define todos los modelos SQLAlchemy para la base de datos SQLite del proyecto.
Incluye modelos para planetas, personal, misiones, comercio y tareas de empleados.

**Dependencias**: `sqlalchemy`, `os`

**Notas de Implementación**:
- **SQLite**: Base de datos simple, sin servidor requerido
- **Foreign Keys**: Implícitas mediante `game_id` (no se usan constraints SQL)
- **JSON Fields**: `task_data` y `result_data` almacenan JSON como texto
- **Enums**: Se usan campos string para flexibilidad en lugar de enums SQL
- **Initial Data**: Personal inicial creado en setup, no en migraciones
- **Validation**: Lógica de negocio en endpoints, no en modelos

**Mejores Prácticas**:
- Usar `get_db()` como dependencia FastAPI para inyección de dependencias
- Mantener consistencia en formatos de fecha (formato del juego: "1-01-05")
- Validar datos en endpoints antes de commit
- Usar transacciones para operaciones complejas
- Documentar campos con comentarios detallados
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# ===== CONFIGURACIÓN DE BASE DE DATOS =====

# Directorio donde se almacena la base de datos
DATABASE_DIR: str = "data"
DATABASE_PATH: str = f"{DATABASE_DIR}/spacegom.db"

# Asegurar que el directorio existe
os.makedirs(DATABASE_DIR, exist_ok=True)

# Crear engine SQLite (sin servidor, archivo local)
# echo=False desactiva el logging SQL para producción
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

# SessionLocal: Factory para crear sesiones de base de datos
# autocommit=False: Requiere commits explícitos
# autoflush=False: No hace flush automático antes de queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para definir modelos SQLAlchemy
Base = declarative_base()


# ===== MODELO PLANET =====

class Planet(Base):
    """
    Modelo de planeta para Spacegom.
    
    Basado en el manual del juego y el archivo Excel de referencia.
    Todos los campos están documentados según las reglas oficiales.
    
    Attributes:
        code: Código 3d6 (111-666), clave primaria única
        name: Nombre del planeta
        
        # Soporte Vital
        life_support: Tipo requerido (NO, SO, MF, RE, RF, TE, TA, TH)
        local_contagion_risk: Riesgo de contagio local (SI/NO)
        days_to_hyperspace: Días hasta estación de hiperdisparo
        legal_order_threshold: Umbral de ordenamiento legal (ej: "7+")
        
        # Espaciopuerto
        spaceport_quality: Calidad (EXC, NOT, MED, BAS, RUD, SIN)
        fuel_density: Densidad combustible (DB, DM, DA, N)
        docking_price: Precio de amarre
        
        # Instalaciones Orbitales (booleanos)
        orbital_cartography_center: Centro de Cartografía (CC)
        orbital_hackers: Piratas Informáticos (PI)
        orbital_supply_depot: Depósito de Suministros (DS)
        orbital_astro_academy: Academia de Astronavegación (AA)
        
        # Productos Disponibles (booleanos)
        product_indu: Productos industriales y manufacturados comunes
        product_basi: Metal, plásticos, productos químicos básicos
        product_alim: Productos de alimentación
        product_made: Madera y derivados
        product_agua: Agua potable
        product_mico: Minerales comunes
        product_mira: Minerales raros y materias primas poco comunes
        product_mipr: Metales preciosos, diamantes, gemas
        product_pava: Productos avanzados, computadores, robótica
        product_a: Armas hasta etapa espacial
        product_ae: Armas a partir de etapa espacial
        product_aei: Armas modernas a partir de etapa interestelar
        product_com: Combustible para astronavegación
        
        # Información Comercial
        self_sufficiency_level: Nivel autosuficiencia (positivo=produce más, negativo=necesita más)
        ucn_per_order: UCN por pedido
        max_passengers: Número máximo de pasajeros
        mission_threshold: Umbral de misiones (valor a igualar o superar en 2d6, ej: "7+")
        
        # Validación para Inicio
        tech_level: Nivel tecnológico (PR, RUD, ES, INT, POL, N.S)
        population_over_1000: Población mayor a 1000 habitantes
        convenio_spacegom: Adscrito al Convenio Universal Spacegom
        
        # Notas y Personalización
        notes: Notas editables desde el frontend
        is_custom: Indica si es un planeta personalizado creado durante la partida
    """
    __tablename__ = "planets"

    # === IDENTIFICACIÓN ===
    code = Column(Integer, primary_key=True)  # Código 3d6 (111-666)
    name = Column(String, nullable=False)  # Nombre del planeta
    
    # === SOPORTE VITAL ===
    # Tipo de soporte vital necesario
    # Valores: NO (No es necesario), SO (Suministro básico de oxígeno),
    #          MF (Máscara con Filtraje), RE (Respirador), RF (Respirador con Filtraje),
    #          TE (Traje espacial estándar), TA (Traje espacial avanzado),
    #          TH (Traje espacial hiperavanzado)
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
    
    def __repr__(self) -> str:
        """Representación string del planeta."""
        return f"<Planet {self.code}: {self.name}>"


# ===== DICCIONARIOS DE REFERENCIA PARA PLANETAS =====

# Diccionarios de referencia para documentación y validación
# Estos ayudan a entender los códigos utilizados en los campos del modelo Planet

LIFE_SUPPORT_TYPES: dict[str, str] = {
    "NO": "No es necesario",
    "SO": "Suministro básico de oxígeno",
    "MF": "Máscara con Filtraje",
    "RE": "Respirador",
    "RF": "Respirador con Filtraje",
    "TE": "Traje espacial estándar",
    "TA": "Traje espacial avanzado",
    "TH": "Traje espacial hiperavanzado"
}

SPACEPORT_QUALITY: dict[str, str] = {
    "EXC": "Excelente",
    "NOT": "Notable",
    "MED": "Medio",
    "BAS": "Básico",
    "RUD": "Rudimentario",
    "SIN": "Sin espaciopuerto"
}

FUEL_DENSITY: dict[str, str] = {
    "DB": "Densidad Baja",
    "DM": "Densidad Media",
    "DA": "Densidad Alta",
    "N": "Ninguno"
}

PRODUCT_DESCRIPTIONS: dict[str, str] = {
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


# ===== MODELO PERSONNEL =====

class Personnel(Base):
    """
    Modelo de personal/empleados para gestión de tripulación.
    
    Cada juego tiene su propia lista de empleados. Los empleados pueden ser
    contratados, despedidos o modificados durante la partida.
    
    Attributes:
        id: ID autoincremental, clave primaria
        game_id: Foreign Key al game_id (índice para búsquedas rápidas)
        position: Puesto de trabajo
        name: Nombre completo del empleado
        monthly_salary: Salario en SC (Créditos Spacegom)
        experience: Nivel de experiencia (N=Novato, E=Experto, V=Veterano)
        morale: Nivel de moral (B=Baja, M=Media, A=Alta)
        hire_date: Fecha de contratación (formato: "2026-01-08" o formato del juego)
        is_active: True si está activo, False si fue despedido
        notes: Notas adicionales editables
    """
    __tablename__ = "personnel"
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, nullable=False, index=True)  # FK al game_id (índice para performance)
    
    # === INFORMACIÓN DEL EMPLEADO ===
    position = Column(String, nullable=False)  # Puesto de trabajo
    name = Column(String, nullable=False)  # Nombre completo
    monthly_salary = Column(Integer, nullable=False)  # Salario en SC (Créditos Spacegom)
    
    # === CARACTERÍSTICAS ===
    experience = Column(String, nullable=False)  # N=Novato, E=Experto, V=Veterano
    morale = Column(String, nullable=False)  # B=Baja, M=Media, A=Alta
    
    # === GESTIÓN ===
    hire_date = Column(String)  # Fecha de contratación (formato: "2026-01-08" o formato del juego)
    is_active = Column(Boolean, default=True)  # True si está activo, False si fue despedido
    notes = Column(Text, default="")  # Notas adicionales
    
    def __repr__(self) -> str:
        """Representación string del empleado."""
        status = "Activo" if self.is_active else "Inactivo"
        return f"<Personnel {self.id}: {self.name} - {self.position} ({status})>"


# ===== DICCIONARIOS Y CONSTANTES PARA PERSONAL =====

# Diccionarios de referencia para documentación
EXPERIENCE_LEVELS: dict[str, str] = {
    "N": "Novato",
    "E": "Experto",
    "V": "Veterano"
}

MORALE_LEVELS: dict[str, str] = {
    "B": "Baja",
    "M": "Media",
    "A": "Alta"
}

# Personal inicial creado automáticamente al completar setup
# Lista de 11 empleados con sus características iniciales
INITIAL_PERSONNEL: list[dict[str, str | int]] = [
    {"position": "Director gerente", "name": "Widaker Farq", "salary": 20, "exp": "V", "morale": "A"},
    {"position": "Comandante de hipersaltos", "name": "Samantha Warm", "salary": 15, "exp": "V", "morale": "M"},
    {"position": "Ingeniero computacional", "name": "Thomas Muller", "salary": 4, "exp": "N", "morale": "B"},
    {"position": "Ingeniero de astronavegación", "name": "Walter Lopez", "salary": 8, "exp": "N", "morale": "B"},
    {"position": "Técnico de repostaje y análisis", "name": "Jeffrey Cook", "salary": 8, "exp": "E", "morale": "B"},
    {"position": "Piloto", "name": "Danielle Rivers", "salary": 10, "exp": "E", "morale": "B"},
    {"position": "Operario de logística y almacén", "name": "Isaac Peterson", "salary": 1, "exp": "N", "morale": "B"},
    {"position": "Contabilidad y burocracia", "name": "Katherine Smith", "salary": 3, "exp": "E", "morale": "M"},
    {"position": "Suministros de mantenimiento", "name": "Jason Wilson", "salary": 3, "exp": "E", "morale": "B"},
    {"position": "Cocinero", "name": "Sam Hernández", "salary": 3, "exp": "E", "morale": "M"},
    {"position": "Asistente doméstico", "name": "Alexandra Adams", "salary": 1, "exp": "E", "morale": "B"},
]


# ===== MODELO MISSION =====

class Mission(Base):
    """
    Modelo de misiones para tracking de objetivos de campaña y misiones especiales.
    
    Tipos de misiones:
    - campaign: Objetivos de campaña (ej: Objetivo #1 - Contratar personal)
    - special: Misiones especiales del libro (ej: Misión M-47, Página 234)
    
    Attributes:
        id: ID autoincremental, clave primaria
        game_id: Foreign Key al game_id (índice para búsquedas rápidas)
        mission_type: Tipo de misión ("campaign" o "special")
        origin_world: Código/nombre del planeta donde se aceptó la misión
        execution_place: Dónde debe ejecutarse la misión
        max_date: Fecha máxima para completar (formato: "YYYY-MM-DD" o formato del juego)
        result: Resultado de la misión ("", "exito", "fracaso")
        objective_number: Número del objetivo (solo para campaign)
        mission_code: Código de la misión especial (ej: "M-47", solo para special)
        book_page: Página del libro donde se detalla (solo para special)
        created_date: Cuando se acepta la misión (fecha del juego)
        completed_date: Cuando se completa la misión
        notes: Notas adicionales editables
    """
    __tablename__ = "missions"
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, nullable=False, index=True)  # FK al game_id
    
    # === TIPO DE MISIÓN ===
    mission_type = Column(String, nullable=False)  # "campaign" o "special"
    
    # === CAMPOS COMUNES ===
    origin_world = Column(String)  # Código/nombre del planeta donde se aceptó
    execution_place = Column(String)  # Dónde debe ejecutarse
    max_date = Column(String)  # Fecha máxima (formato: "YYYY-MM-DD" o del juego)
    result = Column(String, default="")  # "", "exito", "fracaso"
    
    # === ESPECÍFICO DE OBJETIVOS DE CAMPAÑA ===
    objective_number = Column(Integer)  # Número del objetivo (1, 2, 3...)
    
    # === ESPECÍFICO DE MISIONES ESPECIALES ===
    mission_code = Column(String)  # Código de la misión (ej: "M-47")
    book_page = Column(Integer)  # Página del libro donde se detalla
    
    # === METADATA ===
    created_date = Column(String)  # Cuando se acepta (fecha del juego)
    completed_date = Column(String)  # Cuando se completa
    notes = Column(Text, default="")  # Notas adicionales
    
    def __repr__(self) -> str:
        """Representación string de la misión."""
        if self.mission_type == "campaign":
            type_str = f"Objetivo #{self.objective_number}"
        else:
            type_str = f"Misión {self.mission_code}"
        status = self.result or "Activa"
        return f"<Mission {type_str} - {status}>"


# Definición del Primer Objetivo de Campaña
# Estructura de referencia para el primer objetivo del juego
FIRST_OBJECTIVE: dict[str, str | int | list[str]] = {
    "objective_number": 1,
    "description": "Contratar personal específico",
    "requirements": [
        "1 Responsable de soporte a pasajeros",
        "1 Auxiliar de vuelo",
        "1 Negociador de compraventa de mercadería",
        "1 Técnico de mantenimiento de astronaves",
        "1 Técnico de soportes vitales",
        "1 Abogado"
    ]
}


# ===== MODELO TRADEORDER =====

class TradeOrder(Base):
    """
    Modelo de pedidos de comercio de mercancías (Trading).
    
    Cada fila representa una entrada en la tabla de comercio del usuario.
    
    **Reglas de Negocio**:
    - 25 filas máximo por AREA (controlado por lógica de negocio, no en BD)
    - Al vender en mundos NO adscritos al convenio, se pierde trazabilidad
    
    Attributes:
        id: ID autoincremental, clave primaria
        game_id: Foreign Key al game_id (índice para búsquedas rápidas)
        area: Área a la que pertenece este pedido (hay una hoja de pedidos por Área)
        
        # Detalles de COMPRA
        buy_planet_code: Código del planeta donde se compró
        buy_planet_name: Nombre del planeta (guardado por referencia)
        product_code: Código del producto (INDU, BASI, etc.)
        quantity: Cantidad en UCN (Unidades de Carga Normalizadas)
        buy_price_per_unit: Precio unitario de compra
        total_buy_price: Precio total de compra
        buy_date: Fecha de compra (formato string YYYY-MM-DD o formato del juego)
        traceability: Cumple convenio Spacegom (True=Sí, False=No)
        
        # Estado del pedido
        status: Estado actual ("in_transit"=Comprado y en almacén, "sold"=Vendido)
        
        # Detalles de VENTA (se llenan al vender)
        sell_planet_code: Código del planeta donde se vendió
        sell_planet_name: Nombre del planeta de venta
        sell_price_total: Precio total de venta
        sell_date: Fecha de venta
        profit: Ganancia o pérdida calculada (sell_price_total - total_buy_price)
        
        # Metadata
        created_at: Fecha de creación del registro
        updated_at: Fecha de última actualización
    """
    __tablename__ = "trade_orders"

    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, nullable=False, index=True)
    
    # === ÁREA ===
    # Área a la que pertenece este pedido (hay una hoja de pedidos por Área)
    area = Column(Integer, nullable=False)
    
    # === DETALLES DE COMPRA ===
    buy_planet_code = Column(Integer, nullable=False)
    buy_planet_name = Column(String)  # Guardamos nombre por si acaso
    product_code = Column(String, nullable=False)  # INDU, BASI, etc.
    quantity = Column(Integer, nullable=False)  # UCN
    buy_price_per_unit = Column(Integer, nullable=False)
    total_buy_price = Column(Integer, nullable=False)
    
    # Fecha de COMPRA (Día, Mes, Año)
    # El juego usa "Día, Mes y Año". Usamos formato string YYYY-MM-DD para consistencia
    buy_date = Column(String, nullable=False)
    
    # Trazabilidad Convenio Spacegom
    # True = Cumple (Sí), False = No cumple (No)
    traceability = Column(Boolean, default=True)
    
    # === ESTADO DEL PEDIDO ===
    # "in_transit": Comprado y en almacén (o cargando)
    # "sold": Vendido
    status = Column(String, default="in_transit")
    
    # === DETALLES DE VENTA (se llenan al vender) ===
    sell_planet_code = Column(Integer, nullable=True)
    sell_planet_name = Column(String, nullable=True)
    sell_price_total = Column(Integer, nullable=True)
    sell_date = Column(String, nullable=True)
    profit = Column(Integer, nullable=True)  # Ganancia o pérdida calculada
    
    # === METADATA ===
    created_at = Column(String)
    updated_at = Column(String)
    
    def __repr__(self) -> str:
        """Representación string del pedido de comercio."""
        return f"<TradeOrder {self.id}: {self.product_code} x{self.quantity} ({self.status})>"


# ===== MODELO EMPLOYEETASK =====

class EmployeeTask(Base):
    """
    Cola de tareas para empleados (principalmente Director Gerente).
    
    Gestiona búsquedas de personal con cola ordenada. Permite que el Director Gerente
    tenga múltiples búsquedas pendientes que se ejecutan secuencialmente.
    
    Attributes:
        id: ID autoincremental, clave primaria
        game_id: Foreign Key al game_id (índice para búsquedas rápidas)
        employee_id: Foreign Key a personnel.id (empleado que ejecuta la tarea)
        task_type: Tipo de tarea ("hire_search", futuras: "mission", etc.)
        status: Estado de la tarea ("pending", "in_progress", "completed", "failed")
        queue_position: Posición en la cola (1, 2, 3...)
        task_data: JSON con datos específicos de la tarea (almacenado como texto)
        created_date: Cuando se creó (formato del juego: "1-01-05")
        started_date: Cuando comenzó (pasa a in_progress)
        completion_date: Cuando debe terminar (fecha esperada)
        finished_date: Cuando terminó realmente
        result_data: JSON con resultado (solo para completed/failed, almacenado como texto)
    """
    __tablename__ = "employee_tasks"
    
    # === IDENTIFICACIÓN ===
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, nullable=False, index=True)
    employee_id = Column(Integer, nullable=False)  # FK a personnel.id
    
    # === TIPO Y ESTADO ===
    task_type = Column(String, nullable=False)  # "hire_search", futuras: "mission", etc.
    status = Column(String, default="pending")  # "pending", "in_progress", "completed", "failed"
    
    # === ORDEN EN LA COLA ===
    queue_position = Column(Integer, nullable=False)  # 1, 2, 3...
    
    # === DATOS ESPECÍFICOS (JSON) ===
    # JSON almacenado como texto: {position, experience_level, search_days, etc}
    task_data = Column(Text)
    
    # === FECHAS (formato del juego: "1-01-05") ===
    created_date = Column(String)  # Cuando se creó
    started_date = Column(String)  # Cuando comenzó (pasa a in_progress)
    completion_date = Column(String)  # Cuando debe terminar
    finished_date = Column(String)  # Cuando terminó realmente
    
    # === RESULTADO (JSON, solo para completed/failed) ===
    # JSON almacenado como texto: {dice, modifiers, final_result, success, employee_id}
    result_data = Column(Text)
    
    def __repr__(self) -> str:
        """Representación string de la tarea."""
        return f"<Task {self.task_type} - {self.status} (Pos: {self.queue_position})>"


# ===== CATÁLOGO DE PUESTOS DE TRABAJO =====

# Catálogo de Puestos de Trabajo con configuración para contratación
# Cada puesto tiene:
# - tech_level: Nivel tecnológico requerido del planeta
# - search_time_dice: Dados para calcular tiempo de búsqueda (ej: "1d6", "2d6", "1" para fijo)
# - base_salary: Salario base en SC
# - hire_threshold: Umbral de contratación (valor a igualar o superar en tirada)

POSITIONS_CATALOG: dict[str, dict[str, str | int]] = {
    # === NIVEL RUDIMENTARIO (>1000 hab + nivel RUD o superior) ===
    "Abogado": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 5,
        "hire_threshold": 8,
    },
    "Agente secreto": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "2d6",
        "base_salary": 25,
        "hire_threshold": 8,
    },
    "Asistente doméstico": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1",  # 1 día fijo
        "base_salary": 1,
        "hire_threshold": 4,
    },
    "Auxiliar de vuelo": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1",
        "base_salary": 2,
        "hire_threshold": 7,
    },
    "Cocinero": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 3,
        "hire_threshold": 8,
    },
    "Negociador de compraventa de mercadería": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 10,
        "hire_threshold": 8,
    },
    "Operario de logística y almacén": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1",
        "base_salary": 1,
        "hire_threshold": 6,
    },
    "Político demagogo": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "2d6",
        "base_salary": 30,
        "hire_threshold": 9,
    },
    "Psicólogo": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 5,
        "hire_threshold": 8,
    },
    "Responsable de contabilidad y burocracia": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 3,
        "hire_threshold": 7,
    },
    "Responsable de soporte a pasajeros": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 4,
        "hire_threshold": 7,
    },
    "Responsable de suministros de manutención": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 3,
        "hire_threshold": 7,
    },
    "Soldado mercenario": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "2",
        "base_salary": 5,
        "hire_threshold": 7,
    },
    "Recursos Humanos": {
        "tech_level": "RUDIMENTARIO",
        "search_time_dice": "1d6",
        "base_salary": 5,
        "hire_threshold": 7,
    },
    
    # === NIVEL ESPACIAL (>1000 hab + nivel ES o superior) ===
    "Ingeniero de astronavegación": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "2d6",
        "base_salary": 8,
        "hire_threshold": 9,
    },
    "Ingeniero computacional": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "2d6",
        "base_salary": 15,
        "hire_threshold": 8,
    },
    "Médico": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "1d6",
        "base_salary": 7,
        "hire_threshold": 8,
    },
    "Piloto": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "2d6",
        "base_salary": 10,
        "hire_threshold": 7,
    },
    "Técnico de mantenimiento de astronaves": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "1d6",
        "base_salary": 6,
        "hire_threshold": 8,
    },
    "Técnico de repostaje y análisis de combustibles": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "1d6",
        "base_salary": 7,
        "hire_threshold": 8,
    },
    "Técnico de soportes vitales": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "1d6",
        "base_salary": 5,
        "hire_threshold": 7,
    },
    "Vicedirector gerente": {
        "tech_level": "ESPACIAL",
        "search_time_dice": "1d6",
        "base_salary": 20,
        "hire_threshold": 7,
    },
    
    # === NIVEL AVANZADO (>1000 hab + nivel INT, POL o N.SUP) ===
    "Comandante de hipersaltos": {
        "tech_level": "AVANZADO",
        "search_time_dice": "3d6",
        "base_salary": 15,
        "hire_threshold": 9,
    },
    "Científico de terraformación": {
        "tech_level": "AVANZADO",
        "search_time_dice": "2d6",
        "base_salary": 8,
        "hire_threshold": 9,
    },
    "Director gerente": {
        "tech_level": "AVANZADO",
        "search_time_dice": "2d6",
        "base_salary": 20,
        "hire_threshold": 7,
    },
}

# Mapeo de niveles tecnológicos a códigos válidos de planeta
# Usado para filtrar qué puestos están disponibles según el nivel tecnológico del planeta
TECH_LEVEL_REQUIREMENTS: dict[str, list[str]] = {
    "RUDIMENTARIO": ["RUD", "ES", "INT", "POL", "N.S"],
    "ESPACIAL": ["ES", "INT", "POL", "N.S"],
    "AVANZADO": ["INT", "POL", "N.S"]
}


# ===== FUNCIONES DE UTILIDAD =====

def init_db() -> None:
    """
    No-op: la app usa DynamoDB. Se mantiene para compatibilidad con startup.

    Las tablas SQLite ya no se crean; persistencia en SpacegomPlanets y SpacegomGames.
    """
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos para inyección de dependencias FastAPI.
    
    Esta función es un generador que crea una sesión de base de datos, la entrega
    al endpoint que la necesita, y la cierra automáticamente al finalizar.
    
    **Uso en FastAPI**:
    ```python
    @app.get("/endpoint")
    async def my_endpoint(db: Session = Depends(get_db)):
        # Usar db aquí
        pass
    ```
    
    Yields:
        Session: Sesión de SQLAlchemy lista para usar
        
    **Mejores Prácticas**:
    - Usar siempre como dependencia FastAPI (Depends)
    - No crear sesiones manualmente en endpoints
    - La sesión se cierra automáticamente al finalizar la request
    - Usar transacciones explícitas para operaciones complejas
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
