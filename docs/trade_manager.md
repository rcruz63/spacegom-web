# trade_manager.py - Gestión de Comercio

## Overview

Módulo para manejar lógica de compra/venta, cálculo de precios y cooldowns de comercio.

**Ubicación**: `app/trade_manager.py`
**Líneas**: 292
**Dependencias**: `database`, `game_state`, `dice`

## Constantes TRADE_PRODUCTS

Diccionario con datos de productos del manual:
- `buy`: Precio de compra
- `sell`: Precio de venta
- `prod_days`: Días de producción
- `demand_days`: Días de demanda

## Clase TradeManager

### __init__(game_id: str, db: Session)
Inicializa con ID de juego y sesión de BD.

### get_market_data(planet_code: int) -> Dict
Obtiene productos disponibles para comprar/vender en planeta, considerando cooldowns.

### negotiate_price(negotiator_skill: int, reputation: int, is_buy: bool, manual_roll: Optional[int] = None) -> Dict
Calcula multiplicador de precio basado en tirada de 2d6.

**Modificadores**:
- Reputación / 2
- Habilidad del negociador

**Resultados**:
- < 7: Malo (1.2x buy, 0.8x sell)
- 7-9: Normal (1.0x)
- ≥ 10: Bueno (0.8x buy, 1.2x sell)

### execute_buy(planet_code: int, product_code: str, quantity: int, unit_price: int, traceability: bool = True) -> Dict
Ejecuta orden de compra:
1. Verifica tesorería
2. Descuenta costo
3. Crea TradeOrder
4. Registra transacción

### execute_sell(order_id: int, planet_code: int, sell_price_total: int) -> Dict
Ejecuta orden de venta:
1. Actualiza TradeOrder
2. Agrega créditos
3. Calcula ganancia

### _get_game_date_value()
Helper para obtener valor numérico de fecha del juego.

## Dependencias

- **Planet/TradeOrder**: Modelos de BD
- **GameState**: Estado del juego
- **DiceRoller**: Tiradas de dados

## Notas de Implementación

- **Cooldowns**: Basados en órdenes previas (no implementado completamente)
- **Traceability**: Afecta ventas en planetas no adscritos
- **Transacciones**: Logging automático en estado del juego
- **Eventos**: Placeholder para eventos de carga/venta

## Mejores Prácticas

- Verificar fondos antes de transacciones
- Usar transacciones DB para consistencia
- Calcular cooldowns basados en fechas del juego
- Mantener consistencia con reglas del manual