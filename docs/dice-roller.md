# dice-roller.js - Sistema Universal de Dados

## Overview

Interfaz JavaScript consistente para todas las tiradas de dados del juego. Proporciona modo automático/manual y visualización de resultados.

**Ubicación**: `app/static/js/dice-roller.js`
**Líneas**: 301
**Dependencias**: Fetch API, DOM manipulation

## Clase DiceRollerUI

### requestRoll(config)
Método principal para solicitar tirada de dados.

**Parámetros**:
- `numDice`: Número de dados
- `diceSides`: Caras por dado (default: 6)
- `title`: Título del modal
- `description`: Descripción opcional
- `modifiers`: Objeto con modificadores {name: value}
- `onResult`: Callback con resultado

**Retorno**: Promise con resultado de tirada

### showModeSelectionModal()
Muestra modal para elegir entre modo automático o manual.

### showManualInputModal()
Muestra modal para introducir resultados manuales de dados físicos.

### rollAutomatic(numDice, diceSides)
Realiza tirada automática llamando al endpoint `/api/dice/roll`.

### showResultModal()
Muestra modal con resultado de la tirada, dados individuales y modificadores.

## Estructura del Resultado

```javascript
{
    dice: [3, 5],        // Valores individuales
    sum: 8,              // Suma de dados
    mode: "manual",      // "manual" o "automatic"
    modifiers: {rep: 2}, // Modificadores aplicados
    total: 10            // Suma + modificadores
}
```

## Funcionalidades

- **Modo Dual**: Automático (backend) o manual (dados físicos)
- **Visualización**: Muestra dados individuales con diseño cyberpunk
- **Modificadores**: Soporte para múltiples modificadores nombrados
- **Responsive**: Modales centrados y adaptables
- **Fallback**: Tirada local si falla el backend

## Estilos

Usa clases CSS:
- `glass-panel`: Panel con efecto glassmorphism
- `tech-border`: Bordes neón
- `font-orbitron`: Tipografía técnica
- `neon-blue/green`: Colores temáticos

## Integración

Disponible globalmente como `window.DiceRollerUI`.

**Uso típico**:
```javascript
const result = await DiceRollerUI.requestRoll({
    numDice: 2,
    title: "Tirada de Combate",
    modifiers: {fuerza: 2, armadura: -1}
});
```

## Mejores Prácticas

- Usar para todas las tiradas del juego
- Proporcionar títulos descriptivos
- Manejar errores de red
- Mantener consistencia visual