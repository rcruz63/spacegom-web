"""Cliente AWS DynamoDB para Spacegom Companion.

Módulo de acceso a DynamoDB. Proporciona recurso boto3, tablas y helpers
de serialización (Decimal <-> float) para lectura/escritura.

Uso:
    from app.aws_client import get_dynamodb_resource, get_planets_table, get_games_table

Variables de entorno (cargadas desde .env vía load_dotenv en main):
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY: Credenciales AWS (boto3).
    AWS_REGION (str): Región AWS (default: eu-west-1).
    DYNAMODB_ENDPOINT_URL (str): Opcional. Endpoint para DynamoDB local (ej. Docker).
"""
from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import boto3


def get_dynamodb_resource():
    """Obtiene el recurso DynamoDB configurado.

    Usa AWS_REGION y, si existe, DYNAMODB_ENDPOINT_URL (DynamoDB local).

    Returns:
        boto3.resource: Recurso DynamoDB.
    """
    kwargs = {"region_name": os.getenv("AWS_REGION", "eu-west-1")}
    endpoint = os.getenv("DYNAMODB_ENDPOINT_URL")
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    return boto3.resource("dynamodb", **kwargs)


def get_planets_table():
    """Tabla SpacegomPlanets (PK: planet_code)."""
    return get_dynamodb_resource().Table("SpacegomPlanets")


def get_games_table():
    """Tabla SpacegomGames (PK: game_id, SK: entity_id)."""
    return get_dynamodb_resource().Table("SpacegomGames")


def item_from_decimal(obj: Any) -> Any:
    """Convierte recursivamente Decimal a int/float para uso en Python/JSON.

    DynamoDB devuelve números como Decimal. Esta función permite
    consumir items en memoria como tipos nativos.

    Args:
        obj: Valor o estructura (dict/list) a convertir.

    Returns:
        Mismo tipo con Decimals reemplazados por int o float.
    """
    if isinstance(obj, Decimal):
        i = int(obj)
        return i if i == obj else float(obj)
    if isinstance(obj, dict):
        return {k: item_from_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [item_from_decimal(v) for v in obj]
    return obj


def item_to_decimal(obj: Any) -> Any:
    """Convierte recursivamente float a Decimal para escritura en DynamoDB.

    DynamoDB no acepta float nativos. Usar antes de PutItem/BatchWriteItem.

    Args:
        obj: Valor o estructura a convertir.

    Returns:
        Mismo tipo con floats convertidos a Decimal.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: item_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [item_to_decimal(v) for v in obj]
    return obj
