"""
Modelos de datos adicionales usando SQLModel.

Este módulo contiene modelos básicos que pueden extender la funcionalidad
del sistema. Actualmente contiene una estructura mínima diseñada para ser
extensible según necesidades futuras.

Dependencias:
    - sqlmodel: Framework para modelos ORM con validación de tipos
"""

from sqlmodel import SQLModel, Field
from typing import Optional


class EstadoPartida(SQLModel, table=True):
    """
    Modelo básico para estado de partida usando SQLModel.
    
    Este modelo está diseñado para almacenar información adicional del estado
    de una partida. Actualmente contiene solo la estructura mínima con un ID
    autoincremental como clave primaria.
    
    Notas de implementación:
        - Usa SQLModel en lugar de SQLAlchemy puro para mejor integración con Pydantic
        - Diseñado para ser extensible según necesidades futuras
        - Mantiene consistencia con modelos existentes en database.py
    
    Attributes:
        id: ID autoincremental, clave primaria (None antes de insertar)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
