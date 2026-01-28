"""Repositorio de planetas sobre DynamoDB (SpacegomPlanets).

Lectura y actualización de planetas. Sustituye el acceso SQLite a la tabla planets.
"""
from __future__ import annotations

from typing import Any, Optional

from app.aws_client import (
    get_planets_table,
    item_from_decimal,
    item_to_decimal,
)


def _planet_from_item(item: dict[str, Any]) -> "Planet":
    """Construye Planet desde item DynamoDB (tras item_from_decimal)."""
    code = item.get("code")
    if code is None:
        code = int(item["planet_code"])
    return Planet(
        code=int(code),
        name=item.get("name", ""),
        life_support=item.get("life_support", ""),
        local_contagion_risk=item.get("local_contagion_risk", ""),
        days_to_hyperspace=_num(item.get("days_to_hyperspace")),
        legal_order_threshold=item.get("legal_order_threshold", ""),
        spaceport_quality=item.get("spaceport_quality", ""),
        fuel_density=item.get("fuel_density", ""),
        docking_price=int(item.get("docking_price") or 0),
        orbital_cartography_center=bool(item.get("orbital_cartography_center")),
        orbital_hackers=bool(item.get("orbital_hackers")),
        orbital_supply_depot=bool(item.get("orbital_supply_depot")),
        orbital_astro_academy=bool(item.get("orbital_astro_academy")),
        product_indu=bool(item.get("product_indu")),
        product_basi=bool(item.get("product_basi")),
        product_alim=bool(item.get("product_alim")),
        product_made=bool(item.get("product_made")),
        product_agua=bool(item.get("product_agua")),
        product_mico=bool(item.get("product_mico")),
        product_mira=bool(item.get("product_mira")),
        product_mipr=bool(item.get("product_mipr")),
        product_pava=bool(item.get("product_pava")),
        product_a=bool(item.get("product_a")),
        product_ae=bool(item.get("product_ae")),
        product_aei=bool(item.get("product_aei")),
        product_com=bool(item.get("product_com")),
        self_sufficiency_level=_num(item.get("self_sufficiency_level")),
        ucn_per_order=_num(item.get("ucn_per_order")),
        max_passengers=_num(item.get("max_passengers")),
        mission_threshold=item.get("mission_threshold", ""),
        tech_level=item.get("tech_level"),
        population_over_1000=bool(item.get("population_over_1000", True)),
        convenio_spacegom=bool(item.get("convenio_spacegom", True)),
        notes=item.get("notes") or "",
        is_custom=bool(item.get("is_custom")),
    )


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return float(v)


class Planet:
    """DTO de planeta (DynamoDB). Misma forma que el modelo anterior para format_planet_data / is_valid_start."""

    __slots__ = (
        "code", "name", "life_support", "local_contagion_risk", "days_to_hyperspace", "legal_order_threshold",
        "spaceport_quality", "fuel_density", "docking_price",
        "orbital_cartography_center", "orbital_hackers", "orbital_supply_depot", "orbital_astro_academy",
        "product_indu", "product_basi", "product_alim", "product_made", "product_agua", "product_mico",
        "product_mira", "product_mipr", "product_pava", "product_a", "product_ae", "product_aei", "product_com",
        "self_sufficiency_level", "ucn_per_order", "max_passengers", "mission_threshold",
        "tech_level", "population_over_1000", "convenio_spacegom", "notes", "is_custom",
    )

    def __init__(self, **kwargs: Any) -> None:
        for k in self.__slots__:
            setattr(self, k, kwargs.get(k))

    @property
    def spaceport(self) -> str:
        """Cadena espaciopuerto para listados (quality-fuel-docking)."""
        return f"{self.spaceport_quality}-{self.fuel_density}-{self.docking_price}"

    def __repr__(self) -> str:
        return f"<Planet {self.code}: {self.name}>"


def get_planet_by_code(code: int) -> Optional[Planet]:
    """Obtiene un planeta por código (111–666) desde DynamoDB."""
    table = get_planets_table()
    r = table.get_item(Key={"planet_code": str(code)})
    item = r.get("Item")
    if not item:
        return None
    return _planet_from_item(item_from_decimal(item))


def search_planets(name: Optional[str] = None, limit: int = 50) -> list[Planet]:
    """Busca planetas por nombre. Si name es None, devuelve hasta `limit` planetas."""
    table = get_planets_table()
    scan_kw: dict[str, Any] = {}
    if name and name.strip():
        scan_kw["FilterExpression"] = "contains(#n, :q)"
        scan_kw["ExpressionAttributeNames"] = {"#n": "name"}
        scan_kw["ExpressionAttributeValues"] = {":q": name.strip()}
    resp = table.scan(**scan_kw)
    items = resp.get("Items", [])
    while "LastEvaluatedKey" in resp and len(items) < limit:
        scan_kw["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
        resp = table.scan(**scan_kw)
        items.extend(resp.get("Items", []))
    out = [_planet_from_item(item_from_decimal(i)) for i in items[:limit]]
    return out


def update_planet_notes(code: int, notes: str) -> None:
    """Actualiza las notas de un planeta en DynamoDB."""
    table = get_planets_table()
    table.update_item(
        Key={"planet_code": str(code)},
        UpdateExpression="SET #notes = :n",
        ExpressionAttributeNames={"#notes": "notes"},
        ExpressionAttributeValues={":n": notes},
    )


def update_planet_bootstrap(code: int, tech_level: str, population_over_1000: bool) -> None:
    """Actualiza tech_level y population_over_1000 de un planeta (bootstrap)."""
    table = get_planets_table()
    table.update_item(
        Key={"planet_code": str(code)},
        UpdateExpression="SET tech_level = :t, population_over_1000 = :p",
        ExpressionAttributeValues={":t": tech_level, ":p": population_over_1000},
    )
